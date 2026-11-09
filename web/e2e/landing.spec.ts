import { expect, test } from '@playwright/test';
import { mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';

test('public landing and section links never request the native API', async ({ page }, testInfo) => {
  const apiRequests: string[] = [];
  const pageErrors: string[] = [];
  page.on('request', (request) => {
    if (new URL(request.url()).pathname.startsWith('/api/')) apiRequests.push(request.url());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  for (const fragment of ['', '#landing', '#landing/proof', '#landing/route', '#landing/setup']) {
    await page.goto(`/${fragment}`);
    await expect(page.getByRole('heading', { name: 'Catch what status codes miss.', exact: true })).toBeVisible();
    await expect(page).toHaveTitle('SilentShift · Catch what status codes miss');
    await page.waitForLoadState('networkidle');
    expect(apiRequests).toEqual([]);
    if (!fragment) {
      await mkdir(path.resolve('..','evidence/browser'), {recursive:true});
      await page.screenshot({path:path.resolve('..',`evidence/browser/landing-refresh-${testInfo.project.name}.png`)});
    }
  }
  await page.getByRole('link', { name: 'Inspect recorded evidence', exact: true }).click();
  await expect(page).toHaveURL(/#landing\/proof$/);
  await expect(page.getByRole('heading', { name: 'Five cases. Five controlled outcomes.', exact: true })).toBeInViewport();
  expect(apiRequests).toEqual([]);
  expect(pageErrors).toEqual([]);
});

test('public proof is scoped and real JSON and product captures are available', async ({ page, request }) => {
  // Six real asset requests can contend with native compilation on the demo host.
  test.setTimeout(45_000);
  await page.goto('/');
  await expect(page.getByText('Five synthetic scenarios, run natively in IRIS.', { exact: true })).toBeVisible();
  await expect(page.getByText('Rule-only baseline: 5/5. No AI accuracy uplift demonstrated.', { exact: true })).toBeVisible();
  await expect(page.locator('figcaption').filter({ hasText: 'Native investigation of a synthetic payment event' })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Recorded scenario outcomes' }).locator('tbody tr')).toHaveCount(5);

  const summaryResponse = await request.get('/evidence/native-summary.json');
  const traceResponse = await request.get('/evidence/traceability.json');
  for (const response of [summaryResponse, traceResponse]) {
    expect(response.status()).toBe(200);
    expect(response.headers()['content-type']).toContain('application/json');
    const filename = path.basename(new URL(response.url()).pathname);
    expect(await response.body()).toEqual(await readFile(path.resolve('..', 'docs', 'evidence', filename)));
  }
  expect((await summaryResponse.json()).trials.length).toBeGreaterThan(0);
  expect((await traceResponse.json()).cases.length).toBeGreaterThan(0);

  const captureFiles = [
    'native-currency-workbench.png', 'native-currency-mobile.png',
    'native-approved-workbench.png', 'native-approved-mobile.png',
  ];
  for (const filename of captureFiles) {
    const response = await request.get(`/evidence/${filename}`);
    expect(response.status(), filename).toBe(200);
    expect(response.headers()['content-type'], filename).toContain('image/png');
    expect((await response.body()).length, filename).toBeGreaterThan(10_000);
  }
  for (const image of await page.locator('.landing-page picture img').all()) {
    await image.scrollIntoViewIfNeeded();
    await expect.poll(() => image.evaluate((node: HTMLImageElement) => node.complete && node.naturalWidth > 0)).toBe(true);
  }
});

test('workbench action opens the actual unavailable-upstream experience', async ({ page }) => {
  const apiRequests: string[] = [];
  page.on('request', (request) => {
    if (new URL(request.url()).pathname.startsWith('/api/')) apiRequests.push(request.url());
  });
  await page.goto('/');
  await page.locator('.landing-actions').getByRole('link', { name: 'Open workbench', exact: true }).click();
  await expect(page).toHaveURL(/#investigations$/);
  await expect(page.getByRole('heading', { name: 'Investigations', exact: true })).toBeVisible();
  await expect(page.getByText('Native API offline', { exact: true })).toBeVisible();
  await expect(page.getByText('The native IRIS API could not be reached.', { exact: false }).first()).toBeVisible();
  expect(apiRequests.some((url) => new URL(url).pathname === '/api/health')).toBe(true);
  await expect(page.locator('.queue-item')).toHaveCount(0);
});

test('keyboard skip link and reduced-motion landing remain usable', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('[id="landing/main"]')).toBeFocused();
  const action = page.locator('.landing-actions').getByRole('link', { name: 'Open workbench', exact: true });
  await action.focus();
  const styles = await action.evaluate((node) => {
    const computed = getComputedStyle(node);
    return { animation: computed.animationName, transition: computed.transitionDuration, outlineStyle: computed.outlineStyle, outlineWidth: computed.outlineWidth };
  });
  expect(styles.animation).toBe('none');
  expect(styles.transition.split(',').every((duration) => parseFloat(duration) === 0)).toBe(true);
  expect(styles.outlineStyle).not.toBe('none');
  expect(parseFloat(styles.outlineWidth)).toBeGreaterThanOrEqual(2);
});

test('320px landing preserves readable actions without overflow and captures the real page', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 320, height: 844 });
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);
  const action = page.locator('.landing-actions').getByRole('link', { name: 'Open workbench', exact: true });
  await expect(action).toBeVisible();
  await expect(action).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  const geometry = await action.evaluate((node) => {
    const bounds = node.getBoundingClientRect();
    const computed = getComputedStyle(node);
    return { x: bounds.x, right: bounds.right, height: bounds.height, fontSize: parseFloat(computed.fontSize), color: computed.color, background: computed.backgroundColor, clientWidth: node.clientWidth, scrollWidth: node.scrollWidth };
  });
  expect(geometry.x).toBeGreaterThanOrEqual(0);
  expect(geometry.right).toBeLessThanOrEqual(320);
  // A generic link reset must not turn the mint action's label pale.
  const luminance = (color: string) => {
    const rgb = color.match(/[\d.]+/g)!.slice(0, 3).map(Number).map((channel) => {
      const value = channel / 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
  };
  const foreground = luminance(geometry.color);
  const background = luminance(geometry.background);
  expect((Math.max(foreground, background) + 0.05) / (Math.min(foreground, background) + 0.05)).toBeGreaterThanOrEqual(4.5);
  expect(geometry.height).toBeGreaterThanOrEqual(44);
  expect(geometry.fontSize).toBeGreaterThanOrEqual(14);
  expect(geometry.scrollWidth).toBeLessThanOrEqual(geometry.clientWidth);
  for (const image of await page.locator('.landing-page picture img').all()) {
    await image.scrollIntoViewIfNeeded();
    await expect.poll(() => image.evaluate((node: HTMLImageElement) => node.complete && node.naturalWidth > 0)).toBe(true);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  const directory = path.resolve('..', 'evidence', 'browser', 'landing');
  await mkdir(directory, { recursive: true });
  await page.screenshot({ path: path.join(directory, `${testInfo.project.name}-320px.png`), fullPage: true });
});


test('illustrated decision changes with authority and walkthrough completes without API calls', async ({ page }) => {
  const requests: string[]=[];
  page.on('request',request=>{if(new URL(request.url()).pathname.startsWith('/api/')) requests.push(request.url());});
  await page.goto('/');
  await expect(page.getByText('Held before delivery',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Approved amendment',exact:true}).click();
  await expect(page.getByText('Eligible for delivery',{exact:true})).toBeVisible();
  await expect(page.locator('.flow-compare > div').nth(1).locator('strong')).toHaveText('20 CASE');
  await page.getByRole('button',{name:'01 Receive',exact:true}).click();
  await expect(page.locator('.flow-detail')).toContainText('valid JSON');
  await page.getByRole('button',{name:'Play the walkthrough',exact:true}).click();
  await expect(page.getByRole('button',{name:'04 Route',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('button',{name:'Replay walkthrough',exact:true})).toBeVisible();
  expect(requests).toEqual([]);
});

test('reduced motion keeps the decision interactive without animation', async ({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');
  await page.getByRole('button',{name:'Play the walkthrough',exact:true}).click();
  await expect(page.getByRole('button',{name:'04 Route',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(page.locator('.flow-outcome')).toHaveCSS('animation-name','none');
  await page.getByRole('button',{name:'Approved amendment',exact:true}).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByText('Eligible for delivery',{exact:true})).toBeVisible();
});
