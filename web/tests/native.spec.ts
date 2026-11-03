import { expect, request, test } from "@playwright/test";
import type { APIRequestContext, Page, TestInfo } from "@playwright/test";
import { existsSync } from "node:fs";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { z } from "zod";
import {
  CaseSchema,
  CasesSchema,
  EvaluationsSchema,
  HealthSchema,
  OverviewSchema,
  PoliciesSchema,
  ReviewsSchema,
  ScenariosSchema,
} from "../src/schema";
import type { Health, Investigation } from "../src/schema";

// This opt-in Playwright suite uses real HTTP reads, without route
// interception or mocks. Interactive browser verification is recorded separately.
// No request body or authorization header is written to test output.
const webDirectory = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const environmentFile = path.resolve(webDirectory, "../.env");
if (existsSync(environmentFile)) process.loadEnvFile(environmentFile);

function credentialPair(role: "VIEWER" | "IRIS") {
  const username = process.env[`SILENTSHIFT_${role}_USERNAME`];
  const password = process.env[`SILENTSHIFT_${role}_PASSWORD`];
  if (!username || !password)
    throw new Error(
      `Missing SILENTSHIFT_${role}_USERNAME or SILENTSHIFT_${role}_PASSWORD. Values are not logged.`,
    );
  return { username, password };
}

const viewer = credentialPair("VIEWER");
const reviewer = credentialPair("IRIS");
const apiBase = process.env.SILENTSHIFT_API_URL;
if (!apiBase || !/^https?:\/\//.test(apiBase))
  throw new Error("SILENTSHIFT_API_URL must name the actual IRIS API.");

const observations = new WeakMap<
  Page,
  {
    pageErrors: string[];
    consoleErrors: string[];
    writes: string[];
    authenticated: boolean;
  }
>();
let api: APIRequestContext;
let reviewerApi: APIRequestContext;
let health: Health;
let selected: Investigation;

function parse<T>(payload: unknown, schema: z.ZodType<T>): T {
  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    const paths = parsed.error.issues
      .map((issue) => issue.path.join("."))
      .join(", ");
    throw new Error(
      `Actual native response did not satisfy the UI contract at: ${paths}. Response contents suppressed.`,
    );
  }
  return parsed.data;
}

async function read<T>(endpoint: string, schema: z.ZodType<T>, asReviewer = false): Promise<T> {
  const response = await (asReviewer ? reviewerApi : api)
    .get(`${apiBase!.replace(/\/$/, "")}${endpoint}`)
    .catch(() => {
      // API transport call logs can include request headers on a timeout.
      throw new Error(
        `Native GET ${endpoint} failed; sensitive transport details suppressed.`,
      );
    });
  expect(response.status(), `Actual native GET ${endpoint} must succeed`).toBe(
    200,
  );
  return parse(await response.json(), schema);
}

function label(value: string) {
  return value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/^./, (letter) => letter.toUpperCase());
}

async function openNavigation(page: Page) {
  const toggle = page.getByRole("button", { name: "Navigation", exact: true });
  if (await toggle.isVisible()) {
    if ((await toggle.getAttribute("aria-expanded")) !== "true") {
      await toggle.focus();
      await page.keyboard.press("Enter");
    }
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
  }
}

async function login(page: Page, credentials = viewer) {
  await expect(
    page.getByRole("button", { name: "Connect", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Connect", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Connect to native IRIS" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByLabel("IRIS username")).toBeFocused();
  try {
    await dialog.getByLabel("IRIS username").fill(credentials.username);
    await dialog
      .getByLabel("Password", { exact: true })
      .fill(credentials.password);
  } catch {
    // A failing Playwright fill can include its value in the default call log.
    // Replace that exception so a credential can never reach the reporter.
    throw new Error(
      "Credential entry failed; sensitive call details suppressed.",
    );
  }
  await dialog
    .getByRole("button", { name: "Connect session", exact: true })
    .click();
  await expect(dialog).toHaveCount(0);
  await expect(
    page.getByText("Native API connected", { exact: true }),
  ).toBeVisible();
  const state = observations.get(page)!;
  state.authenticated = true;
  state.consoleErrors.length = 0;
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
    })),
  ).toEqual({ local: 0, session: 0 });
}

async function assertHealthyRenderedPage(page: Page) {
  await expect(page.locator("vite-error-overlay")).toHaveCount(0);
  await expect(
    page.getByText("API contract needs attention", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Native API offline", { exact: true }),
  ).toHaveCount(0);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth + 1,
    ),
    "Viewport must not overflow horizontally",
  ).toBe(true);
}

async function evidence(page: Page, testInfo: TestInfo, name: string) {
  const directory = path.resolve(webDirectory, "../evidence/browser/connected");
  await mkdir(directory, { recursive: true });
  await expect(
    page.getByRole("dialog", { name: "Connect to native IRIS" }),
  ).toHaveCount(0);
  const dismiss = page.getByRole("button", {
    name: "Dismiss notification",
    exact: true,
  });
  if (await dismiss.count()) await dismiss.click();
  await page.screenshot({
    path: path.join(directory, `${testInfo.project.name}-${name}.png`),
    fullPage: false,
  });
}

test.beforeAll(async () => {
  api = await request.newContext({
    extraHTTPHeaders: {
      Authorization: `Basic ${Buffer.from(`${viewer.username}:${viewer.password}`).toString("base64")}`,
    },
    timeout: 20_000,
  });
  reviewerApi = await request.newContext({
    extraHTTPHeaders: {
      Authorization: `Basic ${Buffer.from(`${reviewer.username}:${reviewer.password}`).toString("base64")}`,
    },
    timeout: 20_000,
  });
  health = await read("/health", HealthSchema);
  expect(health.build).toMatch(/2026\.3\.0AI.*154/);
  expect(health.production.running).toBe(true);
  expect(health.permissions?.review).toBe(false);
  const cases = await read("/cases?limit=50&offset=0", CasesSchema);
  const critical = cases.items.filter(
    (item) =>
      item.assessment?.critical &&
      item.policy &&
      item.references.length > 0 &&
      item.events.length > 0 &&
      item.trace_id !== null &&
      item.routing === "QUARANTINED",
  );
  // Currency cases contain both amount and amount_scale; verify exact field
  // matching even when one field name is a substring of another.
  const candidate = critical.find((item) => item.scenario_id === "currency-scaling") ?? critical[0];
  if (!candidate)
    throw new Error(
      "Prepare an existing persisted critical native case with references, policy, audit events and trace before running this read-only suite. No fixture will be injected by these tests.",
    );
  selected = candidate;
});

test.afterAll(async () => {
  await api?.dispose();
  await reviewerApi?.dispose();
});

test.beforeEach(async ({ page }) => {
  const state = {
    pageErrors: [] as string[],
    consoleErrors: [] as string[],
    writes: [] as string[],
    authenticated: false,
  };
  observations.set(page, state);
  page.on("pageerror", (error) => state.pageErrors.push(error.name));
  page.on("console", (message) => {
    if (state.authenticated && message.type() === "error")
      state.consoleErrors.push(
        `Browser console error at line ${message.location().lineNumber ?? "unknown"}; message body suppressed.`,
      );
  });
  page.on("request", (browserRequest) => {
    if (!["GET", "HEAD", "OPTIONS"].includes(browserRequest.method()))
      state.writes.push(
        `${browserRequest.method()} ${new URL(browserRequest.url()).pathname}`,
      );
  });
});

test.afterEach(async ({ page }) => {
  const state = observations.get(page)!;
  expect(
    state.writes,
    "Connected browser coverage must remain strictly read-only",
  ).toEqual([]);
  expect(state.pageErrors, "No client runtime exceptions").toEqual([]);
  expect(
    state.consoleErrors,
    "No relevant browser console errors after authentication",
  ).toEqual([]);
});

test("existing evidence, policy, audit and native trace agree with actual IRIS records", async ({
  page,
}, testInfo) => {
  const actual = await read(
    `/cases/${encodeURIComponent(selected.id)}`,
    CaseSchema,
  );
  await page.goto(`/#investigations/${encodeURIComponent(actual.id)}`);
  await login(page);
  await expect(page).toHaveTitle("Investigations · SilentShift");
  await expect(page.locator(".case-detail-heading")).toContainText(actual.id);
  await expect(page.locator(".detail-source")).toContainText(actual.source);
  await expect(page.locator(".detail-source")).toContainText(actual.event_id);
  await expect(page.locator(".decision-strip strong")).toHaveText(
    label(actual.policy!.decision),
  );
  for (const reason of actual.policy!.reasons)
    await expect(page.locator(".policy-reasons")).toContainText(reason);
  await expect(page.locator(".decision-strip")).toContainText(
    "Held from the downstream destination.",
  );
  await expect(page.locator(".evidence-table tbody tr")).toHaveCount(
    actual.assessment!.findings.length,
  );
  for (const finding of actual.assessment!.findings) {
    const row = page
      .locator(".evidence-table tbody tr")
      .filter({ has: page.getByText(finding.field, { exact: true }) });
    await expect(row).toContainText(finding.explanation);
    await expect(row.locator("td").nth(1)).toContainText(
      typeof finding.observed === "string"
        ? finding.observed
        : JSON.stringify(finding.observed),
    );
  }
  const comparison = page.getByRole("region", {
    name: "Semantic comparison",
    exact: true,
  });
  await comparison.focus();
  await page.keyboard.press("ArrowRight");
  await expect(comparison).toBeFocused();
  const outline = await comparison.evaluate((node) => ({
    style: getComputedStyle(node).outlineStyle,
    width: parseFloat(getComputedStyle(node).outlineWidth),
  }));
  expect(outline.style).toBe("solid");
  expect(outline.width).toBeGreaterThanOrEqual(2);
  if (testInfo.project.name === "mobile-native") {
    expect(await comparison.evaluate((node) => node.scrollWidth <= node.clientWidth + 1)).toBe(true);
    for (const row of await page.locator(".evidence-table tbody tr").all()) {
      await row.scrollIntoViewIfNeeded();
      await expect(row.locator("td").nth(1)).toBeInViewport();
      await expect(row.locator("td").nth(2)).toBeInViewport();
    }
  }
  const firstReference = actual.references[0]!;
  const reference = page
    .locator(".reference-record")
    .filter({ hasText: String(firstReference.id) })
    .first();
  await reference.locator("summary").click();
  await expect(reference.locator("pre")).toContainText(
    String(firstReference.id),
  );
  await expect(page.locator(".trace-box .copy-row code")).toHaveText(
    String(actual.trace_id),
  );
  if (actual.trace_url)
    await expect(
      page.getByRole("link", { name: "Open IRIS Visual Trace" }),
    ).toHaveAttribute("href", actual.trace_url);
  if (actual.workflow?.task_id) {
    await expect(page.getByRole("button", { name: "Approve release", exact: true })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Reject transaction", exact: true })).toBeDisabled();
    await expect(page.getByText("Review actions require IRIS reviewer permission", { exact: false })).toBeVisible();
  } else {
    await expect(page.getByRole("button", { name: "Approve release", exact: true })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Reject transaction", exact: true })).toHaveCount(0);
    await expect(page.getByText("Critical contradictions require a corrected event or reference and a new investigation.", { exact: true })).toBeVisible();
  }

  const evidenceTab = page.getByRole("tab", { name: "Evidence", exact: true });
  await evidenceTab.focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("tab", { name: /^Timeline/ })).toHaveAttribute(
    "aria-selected",
    "true",
  );
  await expect(page.locator(".timeline > li")).toHaveCount(
    actual.events.length,
  );
  for (const event of actual.events.filter((entry) =>
    /fail|error|unavailable/i.test(entry.kind),
  ))
    await expect(page.locator(".timeline")).toContainText(label(event.kind));
  await page.keyboard.press("End");
  await expect(
    page.getByRole("tab", { name: "Agent", exact: true }),
  ).toBeFocused();
  if (actual.agent)
    await expect(page.getByRole("tabpanel")).toContainText(
      String(actual.agent.mode),
    );
  else
    await expect(
      page.getByText("No agent execution recorded", { exact: true }),
    ).toBeVisible();
  await page.getByRole("tab", { name: "Evidence", exact: true }).click();
  await page.locator(".case-detail-heading").scrollIntoViewIfNeeded();
  await assertHealthyRenderedPage(page);
  await evidence(page, testInfo, "evidence-viewer");
});

test("a delivered amendment shows its actual evidence and simulator outcome", async ({ page }, testInfo) => {
  const cases = await read("/cases?limit=50&offset=0", CasesSchema);
  const delivered = cases.items.find((item) => item.scenario_id === "approved-amendment" && item.routing === "DELIVERED" && item.policy?.decision === "ALLOW");
  if (!delivered) throw new Error("An existing delivered amendment is required; this suite never injects a fixture.");
  const actual = await read(`/cases/${encodeURIComponent(delivered.id)}`, CaseSchema);
  expect(actual.delivery_count).toBe(1);
  expect(actual.delivery_receipt).toBeTruthy();
  await page.goto(`/#investigations/${encodeURIComponent(actual.id)}`);
  await login(page);
  await expect(page.locator(".case-detail-heading")).toContainText(actual.id);
  await expect(page.locator(".decision-strip strong")).toHaveText("Allow");
  await expect(page.locator(".decision-strip")).toContainText("destination simulator");
  await expect(page.locator(".trace-box .copy-row code")).toHaveText(String(actual.trace_id));
  await expect(page.getByRole("button", { name: "Approve release", exact: true })).toHaveCount(0);
  await expect(page.getByRole("group", { name: "Reference snapshot", exact: true }).locator(".reference-record")).toHaveCount(actual.references.length);
  await assertHealthyRenderedPage(page);
  await evidence(page, testInfo, "approved-delivery");
});

test("precedent evidence matches real case-scoped vector results and recorded tool reads", async ({ page }, testInfo) => {
  const cases = await read("/cases?limit=50&offset=0", CasesSchema);
  const candidate = cases.items.find((item) => item.precedent_context?.status === "retrieved" && item.precedent_context.matches.length > 0 && (item.agent?.tool_reads?.precedents ?? 0) > 0);
  if (!candidate) throw new Error("Prepare an actual native case with retrieved precedents and an observed fourth tool read; this suite never creates one.");
  const actual = await read(`/cases/${encodeURIComponent(candidate.id)}`, CaseSchema);
  const context = actual.precedent_context!;
  expect(context.implementation).toBe("IRIS VECTOR_COSINE");
  expect(context.model).toBe("all-minilm:22m");
  expect(context.dimensions).toBe(384);
  expect(context.decision_authority).toBe(false);
  expect(context.matches.length).toBeLessThanOrEqual(3);
  expect(actual.agent?.prompt_version).toBe("silentshift-investigator/1.3.1");
  await page.goto(`/#investigations/${encodeURIComponent(actual.id)}`);
  await login(page);
  await expect(page.locator(".case-detail-heading")).toContainText(actual.id);
  const precedents = page.getByRole("region", { name: "Similar precedents", exact: true });
  await expect(precedents).toBeVisible();
  await expect(precedents).toContainText("No release authority");
  await expect(precedents.locator(".precedent-match")).toHaveCount(context.matches.length);
  for (const precedent of context.matches) {
    expect(precedent.decision_authority).toBe(false);
    expect(Number.isFinite(precedent.similarity)).toBe(true);
    expect(precedent.similarity).toBeGreaterThanOrEqual(-1);
    expect(precedent.similarity).toBeLessThanOrEqual(1);
    const row = precedents.locator(".precedent-match").filter({ hasText: precedent.precedent_id });
    await expect(row).toContainText(precedent.source_id);
    await expect(row).toContainText(precedent.summary);
    await expect(row).toContainText(label(precedent.outcome));
    await expect(row.locator(".precedent-similarity")).toHaveText(`Cosine similarity ${precedent.similarity.toFixed(3)}`);
    await expect(row.getByText("Synthetic source", { exact: true })).toHaveCount(precedent.synthetic === true ? 1 : 0);
    await expect(row.getByText("Source label not recorded", { exact: true })).toHaveCount(precedent.synthetic === null ? 1 : 0);
    if (precedent.source_type === "resolved_case") {
      expect(precedent.source_id).not.toBe(actual.id);
      await expect(row.getByRole("link", { name: precedent.source_id, exact: true })).toHaveAttribute("href", `#investigations/${encodeURIComponent(precedent.source_id)}`);
    } else await expect(row).toContainText("Approved amendment");
    expect(await row.evaluate((node) => node.scrollWidth <= node.clientWidth + 1)).toBe(true);
  }
  await page.getByRole("tab", { name: "Agent", exact: true }).click();
  await expect(page.getByRole("region", { name: "Evidence tool reads", exact: true })).toBeVisible();
  await expect(page.locator('[data-tool-read="precedents"]')).toHaveText(String(actual.agent!.tool_reads!.precedents));
  await page.getByRole("tab", { name: "Evidence", exact: true }).click();
  await precedents.scrollIntoViewIfNeeded();
  await assertHealthyRenderedPage(page);
  await evidence(page, testInfo, "precedent-evidence");
});

test("all eight routes expose real read-only state or reviewer permission", async ({
  page,
}, testInfo) => {
  await page.goto("/#overview");
  await login(page);
  const routes = [
    ["investigations", "Investigations", "/api/cases"],
    ["scenarios", "Scenario Lab", "/api/scenarios"],
    ["overview", "Overview", "/api/overview"],
    ["messages", "Message Explorer", "/api/cases"],
    ["reviews", "Review", null],
    ["evaluations", "Evaluations", "/api/evaluations"],
    ["policies", "Policies", "/api/policies"],
    ["health", "System Health", null],
  ] as const;
  for (const [route, heading, endpoint] of routes) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await openNavigation(page);
    const pending = endpoint
      ? page.waitForResponse(
          (response) =>
            new URL(response.url()).pathname === endpoint &&
            response.request().method() === "GET" &&
            response.status() === 200,
        )
      : null;
    await page.getByRole("link", { name: heading, exact: true }).click();
    const response = pending ? await pending : null;
    await expect(page).toHaveTitle(`${heading} · SilentShift`);
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
    await expect(
      page.getByRole("heading", { name: heading, exact: true }),
    ).toBeVisible();
    if (route === "investigations") {
      const actual = parse(await response!.json(), CasesSchema);
      await expect(page.locator(".case-list-item")).toHaveCount(
        actual.items.length,
      );
    } else if (route === "scenarios") {
      const actual = parse(await response!.json(), ScenariosSchema);
      await expect(page.locator(".scenario-choice")).toHaveCount(
        actual.scenarios.length,
      );
      await expect(page.locator(".scenario-list-header")).toContainText(
        actual.version,
      );
      await expect(
        page.getByRole("button", { name: "Inject into IRIS", exact: true }),
      ).toBeVisible();
    } else if (route === "overview") {
      const actual = parse(await response!.json(), OverviewSchema);
      await expect(page.locator(".metric-number")).toHaveText(
        [
          actual.processed,
          actual.contradictions,
          actual.pending_reviews,
          actual.quarantined,
        ].map((value) => value.toLocaleString("en-US")),
      );
    } else if (route === "messages") {
      const actual = parse(await response!.json(), CasesSchema);
      await expect(
        page
          .getByRole("combobox", { name: "Select message" })
          .locator("option"),
      ).toHaveCount(actual.items.length);
      await expect(
        page.locator(".message-preview .panel-header"),
      ).toContainText(actual.items[0]!.event_id);
    } else if (route === "evaluations") {
      const actual = parse(await response!.json(), EvaluationsSchema);
      if (!actual.items.length)
        await expect(
          page.getByRole("heading", {
            name: "No measured runs recorded",
            exact: true,
          }),
        ).toBeVisible();
      else
        for (const run of actual.items)
          await expect(page.locator(".evaluation-runs")).toContainText(run.id);
    } else if (route === "policies") {
      const actual = parse(await response!.json(), PoliciesSchema);
      await expect(page.locator(".rules-list > li")).toHaveCount(
        actual.rules.length,
      );
      if (actual.rules[0])
        await expect(page.locator(".rules-list")).toContainText(
          actual.rules[0].description,
        );
    } else if (route === "reviews") {
      await expect(page.getByRole("heading", { name: "Reviewer permission required", exact: true })).toBeVisible();
      await expect(page.locator(".review-task")).toHaveCount(0);
    } else {
      await expect(page.locator(".build-number")).toHaveText(health.build);
      await expect(page.locator(".health-status").first()).toContainText(
        "Running",
      );
      await expect(page.locator(".health-status").nth(1)).toContainText(
        "Configuration does not prove a model invocation.",
      );
    }
    await assertHealthyRenderedPage(page);
  }
  await evidence(page, testInfo, "health");
});

test("selecting another queued case returns to its visible disposition", async ({ page }) => {
  const cases = await read("/cases?limit=50&offset=0", CasesSchema);
  const target = cases.items.find((item) => item.id !== selected.id && item.policy && item.routing !== "PROCESSING");
  if (!target) throw new Error("A second persisted native case is needed for case-navigation verification.");
  await page.goto(`/#investigations/${encodeURIComponent(selected.id)}`);
  await login(page);
  await expect(page.locator(".case-detail-heading")).toContainText(selected.id);
  const toggle = page.getByRole("button", { name: "Expand investigation queue", exact: true });
  if (await toggle.isVisible()) {
    await toggle.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("button", { name: "Collapse investigation queue", exact: true })).toHaveAttribute("aria-expanded", "true");
  }
  await page.locator(".case-list-item").filter({ hasText: target.id }).click();
  await expect(page.locator(".case-detail-heading")).toContainText(target.id);
  await expect(page.locator(".case-detail-heading")).toBeInViewport();
  await expect(page.locator(".decision-strip strong")).toHaveText(label(target.policy!.decision));
  await expect(page.locator(".decision-strip")).toBeInViewport();
  if (await toggle.isVisible()) await expect(toggle).toHaveAttribute("aria-expanded", "false");
  await assertHealthyRenderedPage(page);
});

test("native Review worklist matches actual tasks and preserves dialog keyboard safety", async ({ page }, testInfo) => {
  const denied = await api.get(`${apiBase!.replace(/\/$/, "")}/reviews?limit=50&offset=0`).catch(() => {
    throw new Error("Viewer worklist permission check failed; sensitive transport details suppressed.");
  });
  expect(denied.status()).toBe(403);
  const tasks = await read("/reviews?limit=50&offset=0", ReviewsSchema, true);
  if (!tasks.items.length) throw new Error("Prepare an actual pending native review task; this read-only suite never creates one.");
  const target = tasks.items[0]!;
  const actual = await read(`/cases/${encodeURIComponent(target.case_id)}`, CaseSchema, true);
  expect(String(actual.workflow?.task_id)).toBe(target.task_id);
  await page.goto(`/#reviews/${encodeURIComponent(target.case_id)}`);
  await login(page, reviewer);
  await expect(page.getByRole("heading", { name: "Review", exact: true })).toBeVisible();
  await expect(page.locator(".review-task")).toHaveCount(tasks.items.length);
  expect(await page.locator(".review-task").evaluateAll((nodes) => nodes.map((node) => node.getAttribute("data-task-id")))).toEqual(tasks.items.map((task) => task.task_id));
  await expect(page.locator(".review-worklist-heading")).toContainText(String(tasks.total));
  await expect(page.locator(".case-detail-heading")).toContainText(target.case_id);
  await expect(page.locator(".review-task.selected")).toContainText(target.task_id);
  await expect(page.locator(".review-task.selected")).toContainText(`v${target.case_version}`);
  await expect(page.locator(".case-provenance")).toContainText("Native review task");
  const reject = page.getByRole("button", { name: "Reject transaction", exact: true });
  await expect(reject).toBeEnabled();
  if (actual.assessment?.critical) await expect(page.getByRole("button", { name: "Approve release", exact: true })).toBeDisabled();
  await reject.click();
  const dialog = page.getByRole("dialog", { name: "Reject this transaction", exact: true });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByLabel("Reason", { exact: false })).toBeFocused();
  await expect(dialog.getByRole("button", { name: "Reject transaction", exact: true })).toBeDisabled();
  await page.keyboard.press("Shift+Tab");
  await expect(dialog.getByRole("button", { name: "Close dialog", exact: true })).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(dialog.getByRole("button", { name: "Cancel", exact: true })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(dialog.getByRole("button", { name: "Close dialog", exact: true })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect(reject).toBeFocused();
  await assertHealthyRenderedPage(page);
  await evidence(page, testInfo, "native-review-worklist");
});

test("critical quarantines retain the reviewer release veto", async ({ page }) => {
  await page.goto(`/#investigations/${encodeURIComponent(selected.id)}`);
  await login(page, reviewer);
  await expect(page.locator(".case-detail-heading")).toContainText(selected.id);
  if (selected.workflow?.task_id) {
    await expect(page.getByRole("button", { name: "Approve release", exact: true })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Reject transaction", exact: true })).toBeEnabled();
  } else {
    await expect(page.getByRole("button", { name: "Approve release", exact: true })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Reject transaction", exact: true })).toHaveCount(0);
  }
  await expect(page.getByText("Critical contradictions require a corrected event or reference and a new investigation.", { exact: true })).toBeVisible();
  await assertHealthyRenderedPage(page);
});

test("keyboard navigation, reduced motion and memory-only session lifecycle remain usable", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(`/#investigations/${encodeURIComponent(selected.id)}`);
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
  await login(page);
  await openNavigation(page);
  await page.getByRole("link", { name: "Scenario Lab", exact: true }).focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Scenario Lab", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".scenario-choice").first()).toBeVisible();
  const motion = await page
    .locator(".nav-item")
    .first()
    .evaluate((node) => ({
      animation: getComputedStyle(node).animationName,
      transition: getComputedStyle(node).transitionDuration,
    }));
  expect(motion.animation).toBe("none");
  expect(
    motion.transition
      .split(",")
      .every((duration) => parseFloat(duration) === 0),
  ).toBe(true);
  await assertHealthyRenderedPage(page);
  observations.get(page)!.authenticated = false;
  await page.reload();
  await expect(
    page.getByText("Session required", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Connect", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
    })),
  ).toEqual({ local: 0, session: 0 });
});
