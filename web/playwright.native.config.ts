import { defineConfig } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Never join the normal disconnected suite accidentally. Running this file
// requires an explicit opt-in and an already running real native stack.
if (process.env.SILENTSHIFT_NATIVE_E2E !== "1") {
  throw new Error(
    "Opt in with SILENTSHIFT_NATIVE_E2E=1 npm run test:e2e:native. This suite reads an actual IRIS production; it never injects scenarios or submits reviews.",
  );
}

const webDirectory = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  testDir: "./tests",
  testMatch: "native.spec.ts",
  timeout: 60_000,
  expect: { timeout: 12_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  forbidOnly: Boolean(process.env.CI),
  reporter: "list",
  outputDir: path.resolve(
    webDirectory,
    "../evidence/browser/connected/test-results",
  ),
  use: {
    baseURL: process.env.SILENTSHIFT_WEB_URL ?? "http://127.0.0.1:5173",
    browserName: "chromium",
    locale: "en-US",
    // Login credentials must never appear in automatic traces, video, or
    // failure screenshots. Explicit screenshots are taken after authentication.
    trace: "off",
    video: "off",
    screenshot: "off",
  },
  projects: [
    { name: "desktop-native", use: { viewport: { width: 1440, height: 960 } } },
    {
      name: "mobile-native",
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
});
