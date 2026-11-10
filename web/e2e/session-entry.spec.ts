import { expect, test } from '@playwright/test';

// UI contracts only: synthetic HTTP errors, no invented case records or native pass claim.
test('missing session offers one workbench connection action without stealing focus', async ({ page }) => {
  await page.route('**/api/**', (route) => route.fulfill({
    status: 401,
    contentType: 'application/json',
    body: JSON.stringify({ error: { code: 'AUTHENTICATION_REQUIRED', message: 'Sign in with your IRIS credentials to read this workspace.' } }),
  }));
  await page.goto('/#investigations');
  const welcome = page.getByRole('region', { name: 'Connect your IRIS session' });
  await expect(welcome).toBeVisible();
  await expect(page.locator('.queue-item')).toHaveCount(0);
  await expect(page.getByText('AUTHENTICATION_REQUIRED', { exact: true })).toHaveCount(0);
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content', exact: true })).toBeFocused();
  const expandQueue = page.getByRole('button', { name: 'Expand investigation queue', exact: true });
  if (await expandQueue.isVisible()) await expandQueue.click();
  await expect(page.getByText('Connection required', { exact: true })).toBeVisible();
  const connect = welcome.getByRole('button', { name: 'Connect to IRIS', exact: true });
  await connect.focus();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog', { name: 'Connect to native IRIS' });
  await expect(dialog.getByLabel('IRIS username')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(connect).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
});

test('permission refusal stays distinct from a missing session', async ({ page }) => {
  await page.route('**/api/**', (route) => route.fulfill({
    status: 403,
    contentType: 'application/json',
    body: JSON.stringify({ error: { code: 'PERMISSION_DENIED', message: 'Your IRIS account does not have permission for this action.' } }),
  }));
  await page.goto('/#investigations');
  await expect(page.getByRole('heading', { name: 'Your role cannot open this view' })).toBeVisible();
  await expect(page.locator('.welcome')).toHaveCount(0);
  await expect(page.locator('.queue-item')).toHaveCount(0);
  await page.getByRole('button', { name: 'Switch IRIS account', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Connect to native IRIS' })).toBeVisible();
});
