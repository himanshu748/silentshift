import { defineConfig } from '@playwright/test';

// This suite exercises a genuine unavailable-upstream path. It never fabricates
// connected records and does not count as native IRIS integration evidence.
export default defineConfig({
  testDir: './e2e',
  timeout: 20_000,
  expect: { timeout: 7_000 },
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5189',
    browserName: 'chromium',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'desktop-disconnected', use: { viewport: { width: 1440, height: 960 } } },
    { name: 'mobile-disconnected', use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: {
    command: 'npm run dev -- --port 5189 --strictPort',
    url: 'http://127.0.0.1:5189',
    env: { IRIS_API_ORIGIN: 'http://127.0.0.1:9' },
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
