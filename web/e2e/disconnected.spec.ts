import { expect, test } from '@playwright/test';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';

const routes = [
  ['investigations', 'Investigations'], ['scenarios', 'Scenario Lab'],
  ['overview', 'Overview'], ['messages', 'Message Explorer'],
  ['evaluations', 'Evaluations'], ['policies', 'Policies'], ['health', 'System Health'],
] as const;

for (const [route, heading] of routes) {
  test(`${heading} renders an honest disconnected state`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await page.goto(`/#${route}`);
    await expect(page).toHaveTitle(`${heading} · SilentShift`);
    await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
    await expect(page.getByText('Native API offline', { exact: true })).toBeVisible();
    await expect(page.getByText('The native IRIS API could not be reached.', { exact: false }).first()).toBeVisible();
    await expect(page.locator('.case-list-item')).toHaveCount(0);
    await expect(page.locator('vite-error-overlay')).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
    expect(errors).toEqual([]);
  });
}

test('login failure preserves native unavailability and Escape restores focus', async ({ page }) => {
  await page.goto('/#investigations');
  const connect = page.getByRole('button', { name: 'Connect', exact: true });
  await connect.click();
  const dialog = page.getByRole('dialog', { name: 'Connect to native IRIS' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByLabel('IRIS username')).toBeFocused();
  await dialog.getByLabel('IRIS username').fill('synthetic-test-user');
  await dialog.getByLabel('Password', { exact: true }).fill('synthetic-test-password');
  await dialog.getByRole('button', { name: 'Connect session', exact: true }).click();
  await expect(dialog.getByText('The native IRIS API could not be reached.', { exact: false })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);
  await expect(connect).toBeFocused();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
});

test('keyboard skip link reaches the main workspace', async ({ page }) => {
  await page.goto('/#investigations');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
});

test('navigation remains usable with reduced motion and captures actual UI', async ({ page }, testInfo) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/#investigations');
  await expect(page.getByText('Native API offline', { exact: true })).toBeVisible();
  const animation = await page.locator('.nav-item').first().evaluate((node) => ({
    animation: getComputedStyle(node).animationName,
    transition: getComputedStyle(node).transitionDuration,
  }));
  expect(animation.animation).toBe('none');
  expect(animation.transition.split(',').every((duration) => parseFloat(duration) === 0)).toBe(true);
  const directory = path.resolve('..', 'evidence', 'browser');
  await mkdir(directory, { recursive: true });
  await page.screenshot({ path: path.join(directory, `${testInfo.project.name}.png`), fullPage: true });
  const navigation = page.getByRole('button', { name: 'Navigation', exact: true });
  if (await navigation.isVisible()) {
    await navigation.focus();
    await page.keyboard.press('Enter');
    await expect(navigation).toHaveAttribute('aria-expanded', 'true');
  }
  await page.getByRole('link', { name: 'Scenario Lab', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Scenario Lab', exact: true })).toBeVisible();
});
