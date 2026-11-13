// Run after npm --prefix web ci. Static landing checks only; never starts IRIS.
const fs = require("fs");
const path = require("path");
const { chromium } = require(
  path.resolve(__dirname, "../web/node_modules/playwright"),
);
const output = process.argv[3] || ".local/landing-check";
const baseURL = process.argv[2] || "http://127.0.0.1:5197/";
const result = {
  checked_at: new Date().toISOString(),
  target: baseURL,
  driver: "Playwright Chromium via Node CLI; Chrome channel",
  scope: "Static landing only; no native run or deployment",
  checks: [],
  errors: [],
  failures: [],
};
function check(name, value, detail) {
  result.checks.push({
    name,
    passed: !!value,
    ...(detail === undefined ? {} : { detail }),
  });
  if (!value) throw new Error(name);
}
(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  try {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      permissions: ["clipboard-read", "clipboard-write"],
    });
    const page = await context.newPage();
    page.setDefaultTimeout(15000);
    page.on("pageerror", (e) => result.errors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error") result.errors.push(m.text());
    });
    const failedRequests = [];
    page.on("requestfailed", (r) =>
      failedRequests.push({ url: r.url(), error: r.failure()?.errorText }),
    );
    await page.goto(result.target);
    await page.waitForTimeout(1300);
    check(
      "Correct document title",
      (await page.title()).startsWith("SilentShift"),
    );
    check(
      "Hosted replay disclosure is visible beside the CTA",
      await page.locator(".demo-status").isVisible() &&
        (await page.locator(".demo-status").innerText()).includes("Recorded proposal") &&
        (await page.locator(".demo-status").innerText()).includes("native IRIS policy") &&
        (await page.locator(".demo-status").innerText()).includes("No fresh model inference"),
    );
    const hostedReplay = "https://34.239.152.223.sslip.io/demo/";
    const primaryCTA = page.locator(".hero-actions .primary");
    check("Primary CTA links to the separately hosted replay",
      await primaryCTA.getAttribute("href") === hostedReplay &&
        (await primaryCTA.innerText()).includes("Try hosted replay"));
    check("Hosted CTA precedes the historical benchmark",
      await primaryCTA.evaluate((e) => !!(e.compareDocumentPosition(document.querySelector(".heldout-summary")) & Node.DOCUMENT_POSITION_FOLLOWING)));
    await primaryCTA.focus();
    check("Hosted CTA has visible keyboard focus",
      await primaryCTA.evaluate((e) => e === document.activeElement && getComputedStyle(e).outlineStyle !== "none"));
    await page.keyboard.press("Tab");
    check("Keyboard continues to the recorded fallback",
      await page.getByRole("link", { name: "Explore recorded cases" }).evaluate((e) => e === document.activeElement));
    check("Recorded fallback remains available",
      await page.getByRole("link", { name: "Explore recorded cases" }).getAttribute("href") === "evidence-tour.html");
    await page.getByRole("button", { name: "Replay scope" }).click();
    check(
      "Replay dialog discloses the fixed sample and recorded proposal",
      (await page.getByRole("dialog").isVisible()) &&
        (await page.getByRole("dialog").innerText()).includes("one fixed synthetic quantity mismatch") &&
        (await page.getByRole("dialog").innerText()).includes("No fresh model inference") &&
        (await page.getByRole("dialog").innerText()).includes("22 November 2026, 12:30 PM IST"),
    );
    check("Replay dialog preserves admission limits",
      (await page.getByRole("dialog").innerText()).includes("30 runs per host boot") &&
        (await page.getByRole("dialog").innerText()).includes("two per address"));
    check("Replay dialog links to the same hosted application",
      await page.getByRole("link", { name: "Open hosted replay" }).getAttribute("href") === hostedReplay);
    await page.keyboard.press("Escape");
    check(
      "Escape closes dialog",
      !(await page.getByRole("dialog").isVisible()),
    );
    check(
      "Dialog focus returns to opener",
      await page
        .getByRole("button", { name: "Replay scope" })
        .evaluate((e) => e === document.activeElement),
    );
    await page.locator("[data-copy]").click();
    check(
      "Install command copied exactly",
      (await page.evaluate(() => navigator.clipboard.readText())) ===
        'zpm "install silentshift"',
    );
    check(
      "Copy result announced",
      (await page.getByRole("status").innerText()) ===
        "Install command copied to clipboard.",
    );
    const tabs = page.getByRole("tab");
    for (let i = 0; i < 4; i++) {
      await tabs.nth(i).click();
      await page.locator("#tour-image").evaluate((i) => i.decode());
      check(
        `Gallery tab ${i + 1} selects actual capture`,
        (await tabs.nth(i).getAttribute("aria-selected")) === "true" &&
          (await page
            .locator("#tour-image")
            .evaluate((i) => i.naturalWidth > 0)),
      );
      const href = await page.locator("#tour-original").getAttribute("href");
      const response = await context.request.get(
        new URL(href, result.target).href,
      );
      check(`Gallery original ${i + 1} resolves`, response.status() === 200);
    }
    await tabs.nth(3).focus();
    await page.keyboard.press("Home");
    check(
      "Tab Home selects first",
      (await tabs.nth(0).getAttribute("aria-selected")) === "true",
    );
    await page.keyboard.press("ArrowRight");
    check(
      "Tab ArrowRight selects next",
      (await tabs.nth(1).getAttribute("aria-selected")) === "true",
    );
    await page.keyboard.press("End");
    check(
      "Tab End selects last",
      (await tabs.nth(3).getAttribute("aria-selected")) === "true",
    );
    await tabs.nth(0).click();
    const brokenAnchors = await page.evaluate(() =>
      [...document.querySelectorAll('a[href^="#"]')]
        .filter((a) => !document.getElementById(a.hash.slice(1)))
        .map((a) => a.hash),
    );
    check(
      "Every in-page anchor resolves",
      brokenAnchors.length === 0,
      brokenAnchors,
    );
    const story = await page.locator(".story-shell").boundingBox();
    await page.evaluate(
      (y) => scrollTo({ top: y, behavior: "instant" }),
      story.y + (await page.evaluate(() => scrollY)) + 100,
    );
    await page.waitForTimeout(800);
    check(
      "Desktop scroll story pins",
      (await page.locator(".pin-spacer").count()) === 1,
    );
    await page.evaluate(() => {
      const t = ScrollTrigger.getAll().find((t) => t.vars.pin);
      scrollTo({ top: t.start + (t.end - t.start) * 0.5, behavior: "instant" });
    });
    await page.waitForTimeout(800);
    check(
      "Pinned evidence step becomes visible",
      await page
        .locator("#step-evidence")
        .evaluate((e) => Number(getComputedStyle(e).opacity) > 0.9),
    );
    await page.evaluate(() => {
      const t = ScrollTrigger.getAll().find((t) => t.vars.pin);
      scrollTo({ top: t.end - 30, behavior: "instant" });
    });
    await page.waitForTimeout(800);
    check(
      "Pinned route step becomes visible",
      await page
        .locator("#step-route")
        .evaluate((e) => Number(getComputedStyle(e).opacity) > 0.9),
    );
    await page.locator("[data-motion-toggle]").click();
    check(
      "Manual motion pause removes pinning",
      (await page.locator(".pin-spacer").count()) === 0 &&
        (await page.locator("html").getAttribute("data-motion")) === "paused",
    );
    check(
      "All story steps readable after pause",
      await page
        .locator(".story-panel")
        .evaluateAll((es) =>
          es.every(
            (e) =>
              getComputedStyle(e).opacity === "1" &&
              e.getBoundingClientRect().height > 0,
          ),
        ),
    );
    await page.locator("[data-motion-toggle]").click();
    check(
      "Manual motion resume restores one pin",
      (await page.locator(".pin-spacer").count()) === 1,
    );
    for (const width of [360, 768, 1280, 1920]) {
      await page.setViewportSize({ width, height: width < 800 ? 900 : 1080 });
      await page.waitForTimeout(500);
      check(
        `No horizontal overflow at ${width}px`,
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        await page.evaluate(() => ({
          viewport: innerWidth,
          content: document.documentElement.scrollWidth,
        })),
      );
      check(`Hosted CTA stays readable and touch-sized at ${width}px`,
        await primaryCTA.evaluate((e) => {
          const rect = e.getBoundingClientRect();
          return rect.width > 0 && rect.left >= 0 && rect.right <= innerWidth && rect.height >= 44;
        }));
      if (width === 360) {
        await tabs.nth(0).focus();
        await page.keyboard.press("End");
        check(
          "Mobile keyboard selection remains visible",
          await tabs.nth(3).evaluate((e) => {
            const a = e.getBoundingClientRect(),
              b = e.parentElement.getBoundingClientRect();
            return a.left >= b.left && a.right <= b.right;
          }),
        );
        await tabs.nth(0).click();
      }
      check(
        `Responsive pin count at ${width}px`,
        (await page.locator(".pin-spacer").count()) === (width >= 960 ? 1 : 0),
      );
    }
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.waitForFunction(
      () => document.documentElement.dataset.motion === "paused",
    );
    check(
      "OS reduced motion disables animation",
      (await page.locator("html").getAttribute("data-motion")) === "paused" &&
        (await page.locator(".pin-spacer").count()) === 0,
    );
    check(
      "Reduced motion keeps three story steps visible",
      await page
        .locator(".story-panel")
        .evaluateAll((es) =>
          es.every(
            (e) =>
              getComputedStyle(e).opacity === "1" &&
              e.getBoundingClientRect().height > 0,
          ),
        ),
    );
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.waitForFunction(
      () => document.documentElement.dataset.motion === "enabled",
    );
    check(
      "Restoring OS motion has no duplicate pins",
      (await page.locator(".pin-spacer").count()) === 1,
    );
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.evaluate(() => scrollTo({ top: 0, behavior: "instant" }));
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(output, "desktop-hero.png") });
    await page.locator("#workbench").scrollIntoViewIfNeeded();
    await page.waitForTimeout(900);
    await page.screenshot({ path: path.join(output, "desktop-workbench.png") });
    await page.locator("footer").scrollIntoViewIfNeeded();
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(output, "desktop-footer.png") });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => scrollTo({ top: 0, behavior: "instant" }));
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(output, "mobile-hero.png") });
    await page
      .locator(".tour")
      .evaluate((e) =>
        scrollTo({
          top: e.getBoundingClientRect().top + scrollY - 20,
          behavior: "instant",
        }),
      );
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(output, "mobile-workbench.png") });
    await page.locator("footer").scrollIntoViewIfNeeded();
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(output, "mobile-footer.png") });
    await page.locator("[data-load-film]").click();
    await page.locator("video").scrollIntoViewIfNeeded();
    await page.locator("video").evaluate((v) => {
      v.muted = true;
      return v.play();
    });
    await page.waitForTimeout(1500);
    check(
      "Existing MP4 plays without sign-in",
      await page
        .locator("video")
        .evaluate((v) => v.currentTime > 0 && !v.error),
      await page
        .locator("video")
        .evaluate((v) => ({
          duration: v.duration,
          currentTime: v.currentTime,
          width: v.videoWidth,
          height: v.videoHeight,
        })),
    );
    check(
      "English captions load",
      await page
        .locator("video")
        .evaluate((v) =>
          [...v.textTracks].some(
            (t) => t.language === "en" && t.cues?.length > 0,
          ),
        ),
    );
    await page.locator("video").evaluate((v) => v.pause());
    check(
      "No browser console or page errors",
      result.errors.length === 0,
      result.errors,
    );
    check(
      "No failed network requests",
      failedRequests.length === 0,
      failedRequests,
    );
    const noJS = await browser.newContext({
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    });
    const plain = await noJS.newPage();
    await plain.goto(result.target);
    check(
      "No-JS product story remains visible",
      (await plain.locator("h1").isVisible()) &&
        (await plain.locator("#step-route").isVisible()),
    );
    check(
      "No-JS install and video fallbacks available",
      (await plain.locator("#install").isVisible()) &&
        (await plain
          .locator('a[href="https://youtu.be/a4dOcqu89EA"]')
          .last()
          .isVisible()),
    );
    check("No-JS hosted replay remains a normal usable link",
      await plain.locator(".hero-actions .primary").isVisible() &&
        await plain.locator(".hero-actions .primary").getAttribute("href") === hostedReplay &&
        (await plain.locator(".demo-status").innerText()).includes("No fresh model inference"));
    await plain.keyboard.press("Tab");
    check(
      "Keyboard exposes skip link",
      await plain
        .locator(".skip-link")
        .evaluate((e) => e === document.activeElement),
    );
    await plain.keyboard.press("Enter");
    check(
      "Skip link reaches main content",
      await plain.evaluate(() => location.hash === "#main"),
    );
    check(
      "No-JS page has no horizontal overflow",
      await plain.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await noJS.close();
    await context.close();
  } catch (e) {
    result.failures.push(e.stack);
    process.exitCode = 1;
  } finally {
    await browser.close();
    result.passed = result.failures.length === 0;
    result.pass_count = result.checks.filter((c) => c.passed).length;
    result.check_count = result.checks.length;
    fs.writeFileSync(
      path.join(output, "browser.json"),
      JSON.stringify(result, null, 2) + "\n",
    );
    console.log(JSON.stringify(result, null, 2));
  }
})();
