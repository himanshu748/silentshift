#!/usr/bin/env node
// Explicit native browser write test. No request mocking, traces or videos;
// credentials stay in the host environment and the browser's password field.
import { chromium } from "../web/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const outputArgument = args.indexOf("--output-directory");
if (
  !args.includes("--execute") ||
  outputArgument === -1 ||
  !args[outputArgument + 1]
) {
  throw new Error(
    "Use --execute --output-directory <new-private-directory>; this runs two real local-model CSV investigations.",
  );
}
const output = path.resolve(args[outputArgument + 1]);
if (existsSync(output))
  throw new Error(
    "Use a new output directory; existing evidence is preserved.",
  );
const reuseArgument = args.indexOf("--reuse-input-directory");
const reuse =
  reuseArgument === -1 ? null : path.resolve(args[reuseArgument + 1] ?? "");
if (reuseArgument !== -1 && !args[reuseArgument + 1])
  throw new Error("Supply the previous synthetic run directory.");
process.loadEnvFile(path.join(root, ".env"));
const web = new URL(process.env.SILENTSHIFT_WEB_URL ?? "http://127.0.0.1:5173");
const api = new URL("http://127.0.0.1:52773/silentshift/api");
if (!["127.0.0.1", "localhost"].includes(web.hostname))
  throw new Error("Only the local workbench is supported.");
const pair = (kind) => {
  const username = process.env[`SILENTSHIFT_${kind}_USERNAME`];
  const password = process.env[`SILENTSHIFT_${kind}_PASSWORD`];
  if (!username || !password)
    throw new Error(
      `Missing SILENTSHIFT_${kind}_USERNAME or SILENTSHIFT_${kind}_PASSWORD`,
    );
  return { username, password };
};
const viewer = pair("VIEWER"),
  importer = pair("IRIS");
const headers = {
  Authorization:
    "Basic " +
    Buffer.from(`${importer.username}:${importer.password}`).toString("base64"),
};
let stage = "preflight",
  browser;
const checks = {},
  writes = [],
  pageErrors = [];
function check(name, passed) {
  checks[name] = Boolean(passed);
  if (!passed) throw new Error("Check failed: " + name);
}
async function native(endpoint) {
  const response = await fetch(api.href + endpoint, {
    headers,
    redirect: "error",
    signal: AbortSignal.timeout(20000),
  });
  if (!response.ok) throw new Error("Native read failed");
  return response.json();
}
async function login(page, credentials) {
  await page.getByRole("button", { name: /^(Connect|IRIS session)$/ }).click();
  const dialog = page.getByRole("dialog", { name: "Connect to native IRIS" });
  await dialog.getByLabel("IRIS username").fill(credentials.username);
  await dialog
    .getByLabel("Password", { exact: true })
    .fill(credentials.password);
  await dialog
    .getByRole("button", { name: "Connect session", exact: true })
    .click();
  await dialog.waitFor({ state: "hidden" });
  const dismiss = page.getByRole("button", {
    name: "Dismiss notification",
    exact: true,
  });
  if (await dismiss.isVisible()) await dismiss.click();
}
async function preview(page) {
  await page
    .getByRole("button", {
      name: /^(Preview files|Preview persisted state again)$/,
    })
    .click();
  await page.getByRole("region", { name: "Validated CSV preview" }).waitFor();
}
async function consent(page) {
  await page
    .getByLabel("Approved source note")
    .fill("Synthetic independently approved buyer export for UI verification.");
  await page
    .getByRole("checkbox", {
      name: "I am authorized to import this independently approved reference export.",
    })
    .check();
}
async function resultDownload(page, name) {
  const pending = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download results", exact: true })
    .click();
  const download = await pending;
  const target = path.join(output, name);
  await download.saveAs(target);
  return JSON.parse(await readFile(target, "utf8"));
}
try {
  const health = await native("/health");
  check(
    "native_154_running",
    health.build.includes("Build 154U") && health.production.running,
  );
  check("explicit_importer_permission", health.permissions.csv_import === true);
  if (reuse) {
    const files = await Promise.all(
      ["orders.csv", "approved.csv"].map((name) =>
        readFile(path.join(reuse, name)),
      ),
    );
    if (files.some((bytes) => bytes.length > 131072))
      throw new Error("Input limit exceeded");
    const response = await fetch(api.href + "/imports/csv/preview", {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      redirect: "error",
      body: JSON.stringify({
        orders_csv: files[0].toString("utf8"),
        approved_csv: files[1].toString("utf8"),
      }),
      signal: AbortSignal.timeout(20000),
    });
    if (!response.ok) throw new Error("Existing-case preflight failed");
    const preview = await response.json();
    check(
      "reuse_only_existing_terminal_cases",
      preview.records.length === 2 &&
        preview.records.every(
          (row) =>
            row.existing_case && row.existing_case.routing !== "PROCESSING",
        ),
    );
    await mkdir(output, { mode: 0o700 });
    await Promise.all(
      files.map((bytes, index) =>
        writeFile(
          path.join(output, index === 0 ? "orders.csv" : "approved.csv"),
          bytes,
          { mode: 0o600, flag: "wx" },
        ),
      ),
    );
  } else {
    // Creates the new private directory and refuses an existing one.
    execFileSync("uv", ["run", "python", "pilot/make_sample.py", output], {
      cwd: root,
      stdio: "pipe",
    });
  }
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 },
    acceptDownloads: true,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  page.on("pageerror", () => pageErrors.push("browser-error"));
  page.on("request", (request) => {
    if (request.method() === "POST")
      writes.push(new URL(request.url()).pathname);
  });
  stage = "viewer preview";
  console.log("Checking viewer preview and upload validation...");
  await page.goto(web.href + "#imports");
  await login(page, viewer);
  await page
    .getByText("Reference-import permission required", { exact: true })
    .waitFor();
  const picker = page.getByRole("button", {
    name: "Choose order feed",
    exact: true,
  });
  await picker.focus();
  const chooser = page.waitForEvent("filechooser");
  await page.keyboard.press("Enter");
  await (
    await chooser
  ).setFiles({
    name: "oversized.csv",
    mimeType: "text/csv",
    buffer: Buffer.alloc(131073, 65),
  });
  await page.getByRole("alert").filter({ hasText: "128 KiB" }).waitFor();
  check(
    "oversized_file_rejected_before_api",
    !writes.includes("/api/imports/csv/preview"),
  );
  await page
    .getByLabel("Order feed", { exact: true })
    .setInputFiles(path.join(output, "orders.csv"));
  await page
    .getByLabel("Approved reference export", { exact: true })
    .setInputFiles(path.join(output, "approved.csv"));
  await preview(page);
  check(
    "viewer_can_preview",
    (await page.locator(".csv-table tbody tr").count()) === 2,
  );
  check(
    "viewer_cannot_import",
    await page
      .getByRole("button", {
        name: "Import references and investigate",
        exact: true,
      })
      .isDisabled(),
  );
  check(
    "preview_did_not_dispatch_or_commit",
    !writes.includes("/api/messages") &&
      !writes.includes("/api/imports/csv/commit"),
  );
  await page.screenshot({
    path: path.join(output, "viewer-preview.png"),
    fullPage: true,
  });

  stage = "importer validation";
  await login(page, importer);
  await page
    .getByText("Reference-import permission required", { exact: true })
    .waitFor({ state: "hidden" });
  const bad = (await readFile(path.join(output, "orders.csv"), "utf8")).replace(
    ",20,CASE,",
    ",NaN,CASE,",
  );
  await page
    .getByLabel("Order feed", { exact: true })
    .setInputFiles({
      name: "invalid-quantity.csv",
      mimeType: "text/csv",
      buffer: Buffer.from(bad),
    });
  const response = page.waitForResponse((r) =>
    r.url().endsWith("/api/imports/csv/preview"),
  );
  await page
    .getByRole("button", { name: "Preview files", exact: true })
    .click();
  check(
    "invalid_csv_rejected_by_native_server",
    (await response).status() === 422,
  );
  await page.getByRole("alert").waitFor();
  check(
    "invalid_preview_has_no_commit_action",
    (await page
      .getByRole("button", {
        name: "Import references and investigate",
        exact: true,
      })
      .count()) === 0,
  );
  await page
    .getByLabel("Order feed", { exact: true })
    .setInputFiles(path.join(output, "orders.csv"));
  await preview(page);
  check(
    "consent_required",
    await page
      .getByRole("button", {
        name: "Import references and investigate",
        exact: true,
      })
      .isDisabled(),
  );
  await consent(page);

  stage = "offline interruption";
  await context.setOffline(true);
  await page
    .getByRole("button", {
      name: "Import references and investigate",
      exact: true,
    })
    .click();
  await page.getByRole("alert").waitFor();
  check(
    "uncertain_import_stops_before_rows",
    !writes.includes("/api/messages"),
  );
  check(
    "uncertain_import_requires_repreview",
    await page
      .getByRole("button", {
        name: "Import references and investigate",
        exact: true,
      })
      .isDisabled(),
  );
  await context.setOffline(false);
  await preview(page);
  await consent(page);

  stage = "two native investigations";
  console.log(
    reuse
      ? "Reopening persisted cases through the UI; no new dispatch permitted..."
      : "Importing through the UI and running two native local-model cases...",
  );
  const commitResponse = page.waitForResponse((r) =>
    r.url().endsWith("/api/imports/csv/commit"),
  );
  await page
    .getByRole("button", {
      name: "Import references and investigate",
      exact: true,
    })
    .click();
  check(
    "ui_reference_import_http_200",
    (await commitResponse).status() === 200,
  );
  if (reuse)
    await page.getByText("Processing complete", { exact: true }).waitFor();
  await page
    .locator('nav[aria-label="Main navigation"]')
    .getByRole("link", { name: "Overview", exact: true })
    .click();
  if (reuse) {
    await page
      .locator('nav[aria-label="Main navigation"]')
      .getByRole("link", { name: "CSV Import", exact: true })
      .click();
  } else {
    await page
      .getByText("CSV import is in progress.", { exact: false })
      .waitFor();
    await page
      .getByRole("link", { name: "Return to import", exact: true })
      .click();
  }
  check(
    "navigation_preserves_selected_files",
    (await page.locator(".csv-filename").first().innerText()) === "orders.csv",
  );
  await page
    .getByText("Processing complete", { exact: true })
    .waitFor({ timeout: 300000 });
  const first = await resultDownload(page, "first-results.json");
  const cases = first.records.map((row) => first.results[row.message.event_id]);
  check(
    "critical_line_held",
    cases[0].routing === "QUARANTINED" && cases[0].delivery_count === 0,
  );
  check(
    "matching_line_delivered_once",
    cases[1].routing === "DELIVERED" && cases[1].delivery_count === 1,
  );
  check(
    reuse ? "references_reused_in_ui" : "references_created_in_ui",
    first.import.created === (reuse ? 0 : 2) &&
      first.import.reused === (reuse ? 2 : 0),
  );
  check("original_sources_retained", first.import.source_retained === true);
  check(
    "order_limits_visible",
    first.atomic_order_delivery === false &&
      first.order_completeness === "not_verified",
  );
  const nativeCases = [];
  for (const record of cases) {
    const actual = await native("/cases/" + encodeURIComponent(record.id));
    check(
      "native_four_tools_" + record.id,
      actual.agent.status === "returned" &&
        ["message", "contracts", "related", "precedents"].every(
          (tool) => actual.agent.tool_reads[tool] >= 1,
        ),
    );
    nativeCases.push({
      case_id: actual.id,
      trace_id: actual.trace_id,
      routing: actual.routing,
      delivery_count: actual.delivery_count,
      agent_status: actual.agent.status,
      tool_reads: actual.agent.tool_reads,
    });
  }
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.screenshot({
    path: path.join(output, "results-desktop.png"),
    fullPage: true,
  });
  await page
    .getByRole("link", { name: "Open case", exact: true })
    .first()
    .click();
  await page
    .getByRole("heading", { name: "Investigations", exact: true })
    .waitFor();
  check(
    "case_link_opens_native_investigation",
    page.url().endsWith("#investigations/" + cases[0].id),
  );
  await page
    .locator('nav[aria-label="Main navigation"]')
    .getByRole("link", { name: "CSV Import", exact: true })
    .click();
  await page.getByText("Processing complete", { exact: true }).waitFor();

  stage = "duplicate recovery";
  const writesBefore = writes.filter((url) => url === "/api/messages").length;
  await preview(page);
  await consent(page);
  await page
    .getByRole("button", {
      name: "Import references and investigate",
      exact: true,
    })
    .click();
  await page.getByText("Processing complete", { exact: true }).waitFor();
  const repeat = await resultDownload(page, "repeat-results.json");
  const outcomes = (data) =>
    data.records.map((row) => {
      const record = data.results[row.message.event_id];
      return [
        record.id,
        record.routing,
        record.trace_id,
        record.delivery_count,
      ];
    });
  check(
    "repeat_reuses_cases_and_receipts",
    JSON.stringify(outcomes(repeat)) === JSON.stringify(outcomes(first)),
  );
  check(
    "repeat_reuses_reference_revisions",
    repeat.import.created === 0 && repeat.import.reused === 2,
  );
  check(
    "repeat_reads_cases_without_new_dispatch",
    writes.filter((url) => url === "/api/messages").length === writesBefore,
  );

  stage = "mobile and reduced motion";
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  check(
    "mobile_has_no_page_overflow",
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  );
  check(
    "reduced_motion_no_panel_animation",
    await page
      .locator(".csv-preview")
      .evaluate((el) => getComputedStyle(el).animationName === "none"),
  );
  await page.screenshot({
    path: path.join(output, "results-mobile.png"),
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Choose order feed", exact: true })
    .focus();
  check(
    "file_picker_keyboard_focus",
    await page
      .getByRole("button", { name: "Choose order feed", exact: true })
      .evaluate((el) => el === document.activeElement),
  );
  await page.setViewportSize({ width: 320, height: 740 });
  check(
    "compact_has_no_page_overflow",
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  );
  check(
    "credentials_not_in_browser_storage",
    await page.evaluate(
      () => localStorage.length === 0 && sessionStorage.length === 0,
    ),
  );
  check("no_browser_exceptions", pageErrors.length === 0);
  if (reuse)
    check("reuse_made_zero_message_posts", !writes.includes("/api/messages"));
  const report = {
    passed: Object.values(checks).every(Boolean),
    build: health.build,
    reused_existing_cases: Boolean(reuse),
    scope:
      "Actual browser uploads and native production with synthetic CSVs; simulator only. Offline failure deliberately injected at the browser transport. Existing-case reuse, when selected, makes no fresh inference claim.",
    checks,
    cases: nativeCases,
    ui_import_receipt: {
      id: first.import.receipt.id,
      imported_by: first.import.receipt.imported_by,
      imported_at: first.import.receipt.imported_at,
    },
    writes,
  };
  await writeFile(
    path.join(output, "verification.json"),
    JSON.stringify(report, null, 2) + "\n",
    { mode: 0o600 },
  );
  console.log(
    JSON.stringify({
      passed: report.passed,
      checks: Object.keys(checks).length,
      cases: nativeCases,
    }),
  );
} catch {
  // Playwright errors may contain locator values or request headers. Never
  // dump them, or take automatic login screenshots/traces, on failure.
  await mkdir(output, { recursive: true, mode: 0o700 });
  await writeFile(
    path.join(output, "failure.json"),
    JSON.stringify({ passed: false, stage, checks }, null, 2) + "\n",
    { mode: 0o600 },
  );
  console.error(
    "CSV UI verification stopped at " +
      stage +
      "; sensitive diagnostics withheld.",
  );
  process.exitCode = 1;
} finally {
  await browser?.close();
}
