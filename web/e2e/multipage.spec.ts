import { expect, test } from '@playwright/test';

const pages = [
  ['how-it-works', 'Valid message. Contradicted agreement.'],
  ['product', 'One workbench for every hold.'],
  ['safeguards', 'The model recommends. It never releases.'],
  ['evidence-record', 'Five cases. Five controlled outcomes.'],
  ['run-locally', 'Start the IRIS production.'],
] as const;

for (const [slug, heading] of pages) {
  test(`${slug} is a separate public document with a refreshable URL`, async ({ page, request }) => {
    const apiRequests: string[] = [];
    const errors: string[] = [];
    page.on('request', r => { if (new URL(r.url()).pathname.startsWith('/api/')) apiRequests.push(r.url()); });
    page.on('pageerror', error => errors.push(error.message));
    const response = await request.get(`/${slug}/index.html`);
    expect(response.status()).toBe(200);
    expect(await response.text()).toContain(`data-page="${slug}"`);
    await page.goto(`/${slug}/`);
    await expect(page.getByRole('heading', { level: 1, name: heading, exact: true })).toBeVisible();
    const title = await page.title();
    expect(title).toContain('SilentShift');
    await expect(page.locator('.site-nav [aria-current="page"]')).toHaveCount(1);
    await page.reload();
    await expect(page.getByRole('heading', { level: 1, name: heading, exact: true })).toBeVisible();
    await expect(page).toHaveTitle(title);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    const images = page.locator('.site picture img');
    for (const image of await images.all()) {
      await image.scrollIntoViewIfNeeded();
      await expect.poll(() => image.evaluate((node: HTMLImageElement) => node.complete && node.naturalWidth > 0)).toBe(true);
    }
    expect(apiRequests).toEqual([]);
    expect(errors).toEqual([]);
  });
}

test('public navigation supports keyboard, history and reduced motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/product/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#site-main')).toBeFocused();
  const menu = page.getByRole('button', { name: /^(Open|Close) site navigation$/ });
  if (await menu.isVisible()) {
    await menu.focus();
    await page.keyboard.press('Enter');
    await expect(menu).toHaveAttribute('aria-expanded', 'true');
    await page.keyboard.press('Escape');
    await expect(menu).toBeFocused();
    await expect(menu).toHaveAttribute('aria-expanded', 'false');
    await page.keyboard.press('Enter');
  }
  const target = page.getByRole('navigation', { name: 'Site', exact: true }).getByRole('link', { name: 'How it works', exact: true });
  await target.focus();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/how-it-works\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Valid message. Contradicted agreement.');
  await page.goBack();
  await expect(page).toHaveURL(/\/product\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('One workbench for every hold.');
  await page.goForward();
  await expect(page).toHaveURL(/\/how-it-works\/$/);
  await expect(page.locator('#site-main')).toHaveCSS('animation-name', 'none');
});
