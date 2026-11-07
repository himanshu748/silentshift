# SilentShift features and technical reference

For setup, use **[INSTALL.md](../INSTALL.md)**. This file explains the installed application's behavior, optional capabilities, API and developer checks.

Start with a [guided investigation](JUDGE_GUIDE.md), or use the sections below to inspect how evidence, policy and native messages fit together. All supplied examples are synthetic and deliver only to the included IRIS simulator.

## Community Idea DPI-I-689: LLM tracing with Interoperability

SilentShift implements [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) by turning each admitted AI Hub provider exchange into an actual `CallRequest` / `CallResponse` pair in the original business-case session. A queued Business Operation records the model, provider, prompt version, elapsed operation time, returned tool names, HTTP outcome and available response-token counts. Deterministic policy still authorizes delivery; a trace is evidence of execution, not permission to release an order.

**Inspect the implementation:** [keyless replay](#see-it-in-visual-trace) · [native metadata screenshot](#native-provider-metadata) · [Langfuse comparison](#silentshift-iris-interoperability-vs-langfuse). **Bonus status: Pending, organizer-unconfirmed.** The November 6 signed-out check shows the description link but no dedicated **Ideas to the app** association. Open Exchange support has been contacted; no award is asserted.

### See it in Visual Trace

First complete [installation](../INSTALL.md). For a recorded run without a model, use the optional replay section in that same guide. The replay executes the native agent and all four tools with recorded assistant responses; it makes no new inference.

Open the printed Visual Trace URL with a local IRIS portal account. Follow intake through `Partner → Semantic`, evidence through the reference/precedent operations, and investigation through `Semantic → Investigator`. Each `ProviderIngress → ProviderForwarder` request/response pair represents one provider exchange in the same case session. Select **Body** to inspect its metadata. `AITrace` records tool execution; `Quarantine` and `ReviewCoordinator → ReviewWorklist` show the hold and task.

The standard reviewer can view the graph. Message bodies additionally require administrator-managed `%Ens_MessageContent:USE` and SQL `SELECT` on `Ens.MessageHeader`. [Permission details](NATIVE_AI_HUB.md#viewing-native-message-properties).

### Native provider metadata

Earlier fresh-source replay: session **24**, five recorded exchanges, four executed tools, zero deliveries. [Replay evidence](evidence/idea-replay-load.json). The screenshot below shows a separate **live** call in session **1667**, selected in the native Visual Trace **Body** panel: model, prompt version, provider, timing, tool-call metadata and returned token counts are physical message properties.

![Native Visual Trace Body panel: live session 1667, model qwen3-silentshift:4b-instruct, 37125 ms, HTTP 200 and 877 input plus 70 output tokens](assets/provider-success-body-safari.png)

That call returned HTTP **200**, **877** input tokens and **70** output tokens in **37,125 ms** of forwarding-operation time. The quantity contradiction still left the case **QUARANTINED**, with zero deliveries. The [failure Body screenshot](assets/provider-failure-body-safari.png) shows session **1807**, HTTP **400**, `UPSTREAM_HTTP_ERROR` and **160 ms** for the intentional invalid-format diagnostic; it also stayed quarantined. Billing cost remains unknown in both. These are unedited portal captures of retained live records, not replay screenshots. Long IDs/tool JSON are clipped by the native panel; the [capture receipt and complete selected metadata](evidence/provider-body-captures.json) preserve their values and record restoration of both temporary read grants.

**Recorded fields:** case/session/invocation/call IDs; provider, model and prompt **version**; request/response times, operation duration, byte counts, offered tools and returned tool-call IDs/names; finish reason; safe error code and HTTP status; zero application retries and false fallback. Live response token counts are recorded only when returned. Raw prompts, tool arguments and raw provider bodies are omitted. Billing cost, SDK/provider retry count and session-token totals remain unknown. Replay marks `execution_mode=recorded-replay`, keeps upstream status/usage null and records its fixture ID. [Exact field map and failure recipe](NATIVE_AI_HUB.md).

### SilentShift (IRIS Interoperability) vs Langfuse

| Dimension | SilentShift in IRIS | Langfuse |
| --- | --- | --- |
| Where traces live | Native message headers/bodies in the case's interoperability session | LLM traces and observations in Langfuse Cloud or a self-hosted service |
| Per-call data | Metadata-only request/response messages; case evidence stored separately | Instrumented inputs/outputs, model parameters, relationships and metadata |
| Prompt versioning | Version string in source and each message; no prompt registry or content hash | Versioned prompts, labels and prompt-to-trace links |
| Tokens and cost | Actual response usage when present; unknown counts/cost null; replay usage null | Ingested usage/cost, with supported inference from model/token/pricing definitions |
| Latency | Forwarding-operation duration, including validation, I/O and parsing | Observation/trace latency and generation timing when instrumented |
| Tool calls | Returned IDs/names plus distinct native execution events; arguments omitted | Nested tool observations with instrumented content and timing |
| Human review | Native Workflow task creation in the intake trace; later review requests have their own sessions and persisted links | Instrument custom application/review spans and attach scores or annotations |
| Replay and resend | Frozen recorded-provider example, event idempotency and native message navigation; resend permission is not granted to reviewers | Dataset experiments and prompt playground workflows; business-message redelivery needs application integration |
| Retention and audit | Persistent IRIS messages and case audit; operator controls purge/retention. No automatic retention guarantee is asserted | Depends on Cloud plan or self-hosted retention/deletion configuration |
| Setup and dependencies | Licensed AI Hub build 154, interoperability production and local Ollama for live mode; no Langfuse service | SDK/OpenTelemetry integration and Cloud or self-hosted Langfuse infrastructure |
| When to choose it | An IRIS operator needs to connect one model exchange to a held/delivered business transaction | Choose Langfuse for dedicated evals, experiments, dashboards, prompt management and cross-application LLM observability |

Comparison based on Langfuse's [observability](https://langfuse.com/docs/observability/overview), [prompt management](https://langfuse.com/docs/prompt-management/overview), [token/cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking) and [datasets/experiments](https://langfuse.com/docs/evaluation/experiments/datasets) documentation. This is a comparison of implemented scope, not feature parity.

## Follow the evidence to a decision

Open an investigation to compare the original partner payload with its immutable reference snapshot. Inspect what the agent actually read, why policy held or released the message, and whether the simulator recorded a delivery. A trace ID connects that investigation to its native IRIS production session.

The agent proposes through four read-only, case-scoped evidence tools: current message, approved contracts, related records and similar precedents. Server policy owns the route: missing evidence, conflicting authority, malformed answers and timeouts cannot justify automatic delivery. A reviewer can resolve an eligible hold with a reason, version and idempotency key; critical contradictions retain their release veto. Native Workflow preserves the human task, including a recorded decision whose completion needs to be resumed.

![An approved amendment inspected in the working local application, with one simulator delivery](assets/native-approved-delivery.png)

The native chain is Business Service → Business Process → reference/AI Operations → Embedded Python policy → destination or quarantine Operation. IRIS persists the payload, references, audit, review state and unique simulator receipt. The workbench provides eight API-backed views, including the native Review queue, raw payload inspection and a Scenario Lab with five labeled synthetic experiments.

**Verified boundary:** the core ran on official ARM64 Community AI Hub `2026.3.0AI.154.0` (`154U`), including a fresh-volume repeat. The destination is an IRIS simulator. The [evidence appendix](JUDGE_GUIDE.md#evidence-appendix) retains passing and failed trials, baseline results and measurement limits. No public deployment or external ERP/bank delivery is claimed.

The five-case demonstration is only the starting point. Separate native checks exercise [misleading precedents, concurrent approvals, interrupted review completion and file retries](JUDGE_GUIDE.md#check-failure-and-recovery-behavior). Each has its own recorded outcome and scope; these checks are not combined into an AI accuracy score.

## Interface walkthrough

Open the root page to explore the unsupported order and effective amendment. The interactive illustration changes the approved evidence and explains each stage; it sends no API request and is clearly labeled synthetic. **Open workbench** leads to the real authenticated application. Use **⌘K / Ctrl+K** to find a view or open a complete case ID. Detail transitions respect reduced motion. [UI study and verification](UI_REVIEW.md).

![Interactive landing page with the held-order comparison](assets/ui-final-landing-desktop.jpg)

There is **no hosted live demo**. The displayed EAP agreement restricts the downloaded runtime to internal evaluation and explicitly excludes demonstrations. We did not deploy it or claim the online-demo bonus. [Hosting decision and primary terms](HOSTING_REVIEW.md).

## Local checks without IRIS

Requirements: Python 3.10+ with [uv](https://docs.astral.sh/uv/), Node 22.12+ and npm. The Python runtime library has no dependencies. Development versions are locked by `uv.lock` and `web/package-lock.json`.

```sh
uv sync --locked
uv run pytest -q
PYTHONPATH=python uv run python -m silentshift.evaluation \
  --dataset fixtures/v1/scenarios.json --output evidence/local-policy.json
npm --prefix web ci
npm --prefix web run check
npm --prefix web run build
```

For browser checks, install the locked Playwright Chromium if it is not already installed, then run the suite:

```sh
cd web
npx playwright install chromium
npm run test:e2e
```

The browser suite starts its own loopback Vite server with an intentionally unreachable upstream. It tests genuine failure states at 1440×960 and 390×844, all eight workbench routes, keyboard focus, login failure and reduced motion. It does **not** prove connected cases or native integration. Screenshots are saved under `evidence/browser/`.

With the real native stack and an existing critical case running, opt into the separate read-only browser suite:

```sh
SILENTSHIFT_NATIVE_E2E=1 npm --prefix web run test:e2e:native
```

It authenticates using the private local configuration, checks actual evidence/trace data, reviewer permissions and mobile keyboard scrolling. It sends no scenario or review mutations and uses no network mocks.

Start the workbench separately:

```sh
npm --prefix web run dev -- --port 5173 --strictPort
```

Open `http://127.0.0.1:5173`. Until the native stack is available, records and metrics stay unavailable. The static build requires an API reverse proxy when hosted; Vite's proxy is development-only. Do not publish a disconnected static build as a working native demo.

## Runtime setup

Use [INSTALL.md](../INSTALL.md) for image loading, local credentials, Ollama, startup and the workbench. This reference assumes that installation is complete.

## Prove the native journey

Use the reviewer account for the complete safety gate. The following command invokes five native investigations, plus idempotent retries that must reuse the same case/receipt. This command invokes the configured local model:

```sh
uv run --env-file .env python scripts/verify_native.py --allow-model-calls
```

It checks actual build 154/production status, anonymous denial, all four native evidence reads, nonempty trace IDs, expected policy/routing, one or zero simulator receipts, safe replay, critical reviewer-release denial and persisted evaluation agreement. Evidence goes to ignored `evidence/native/latest.json`. The Evaluations view reads the server-persisted report. A viewer-only execution cannot pass the critical reviewer-policy gate.

Inspect Visual Trace in IRIS using the recorded session ID and an appropriately privileged portal account. Actual checks also cover viewer denial, critical-release veto, typed/blank review reasons, rejection resolution, concurrent approval with one receipt, and restart/recreation persistence. Reference-limit integration tests invoke no model and preserve their isolated synthetic rows:

```sh
uv run --env-file .env python scripts/verify_native_boundaries.py
```

Use `--context`/`--container` when your Docker naming differs. Network-loss recovery, provider cancellation, real external delivery and broader stochastic trials remain unverified; a process timeout does not prove provider cancellation.

Every local provider HTTP call produces typed interoperability request and response messages in the original case session. The retained approved-amendment case in session 374 made four calls (headers 381–388), then delivered once. The explicit SDK failure probe in session 316 recorded a real Ollama HTTP 400 and stayed quarantined with zero deliveries. Current four-tool runs made two exchanges per case. [Successful trace](assets/provider-success-visual-trace.png) · [failure trace](assets/provider-failure-visual-trace.png).

```sh
uv run python scripts/verify_native_provider.py --inspect-case CASE_ID
```

The [native AI Hub guide](NATIVE_AI_HUB.md) maps each field, reproduces the failure and compares the scope with Langfuse. Unknown provider retries and billing cost stay null; actual HTTP response usage is distinct from session totals. Historical invocation/tool evidence remains in [AI_TRACING.md](AI_TRACING.md). [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) is the implemented idea; organizer acceptance is unconfirmed.

Held transactions now enter a native IRIS Workflow worklist. Connect as the configured reviewer and open **Review** to inspect pending tasks, their original case evidence and policy. A critical contradiction permits rejection; approval remains blocked. Completed tasks leave the pending worklist, while the case keeps the reason, original version, idempotency key and native task receipt. Historical holds are readable and require a new investigation before a new review decision.

```sh
uv run python scripts/verify_native_review_queue.py --allow-new-synthetic-cases
```

The [54-check receipt](evidence/review-queue.json) includes reviewer-only task listing, rejection, two concurrent identical approvals, one review receipt, one native completion response and one simulator delivery. The workbench also completed [actual approve and reject actions](evidence/review-ui.json), shown in the [native worklist](assets/review-native-worklist.png). These isolated synthetic cases skip LLM inference at the evidence-budget guard; existing procedural retrieval can use local embeddings. They do not alter the five evaluation cases.

The earlier controlled postcommit HTTP 503 recovery remains documented in [the Workflow receipt](evidence/workflow.json) and [engineering story](articles/engineering.md). Resume the original recorded request after an uncertain outcome; changing its reason, version or key creates a different decision and is rejected.

## Optional local intake and procedural guidance

### Evaluate a bounded CSV order feed

The separate [CSV pilot](../pilot/README.md) accepts incoming order lines and an independently supplied approved-reference export. A trusted local operator imports immutable reference revisions; each line then uses the existing native investigation and deterministic delivery policy. The verifier checks holds, a simulator delivery, repeat submissions and transactional rollback. Samples are synthetic; there is no X12 parser, whole-order delivery guarantee or customer-data qualification. The pilot is source-only and is not included in public IPM 0.2.0. [Current verification](BUILD_STATUS.md).

### Accept partner JSON from a ready-file inbox

The custom native inbound adapter is dormant by default. Set `SILENTSHIFT_PARTNER_FILES_ENABLED=1` before bootstrap to opt in. Bootstrap creates `.local/partner-inbox` with mode `0700`; Compose mounts it at the adapter's fixed `/var/opt/silentshift/partner-inbox` path. Keep it owned for the trusted operator and container `irisowner`; partner payloads cannot choose a directory.

Write the raw UTF-8 partner **message** JSON to `<name>.json.part`, close it, then atomically rename it to `<name>.json.ready` on the same filesystem. Do not wrap it in a Scenario Lab request. Names contain 1–80 ASCII letters, digits, hyphens or underscores and begin with a letter or digit. The same server validation and reference authority apply as at `POST /messages`.

The adapter claims `.work`, retains the exact input bytes in `.done` or `.hold`, and writes `<name>.json.ack.json` from the persisted outcome. The acknowledgment includes its input SHA-256, case/trace IDs, policy result and simulator receipt. It preserves the first observed outcome: a later review decision changes the case, while its earlier held acknowledgement stays unchanged. Inspect the acknowledgement's timestamp and delivery count, then follow the case for current state. Uncertain dispatches and exhausted retries need operator inspection. Keep fewer than 256 active files per suffix and plan retention explicitly; the adapter deletes no input or archive.

The [file walkthrough](PARTNER_INBOX.md) shows actual ready-file delivery and critical quarantine, with native Visual Trace screenshots. All 82 adapter assertions passed, including acknowledgement recovery and replay without another receipt. The [verification driver](../scripts/verify_native_adapter.py) documents activation, bounded test calls and read-only `--inspect-file` use. Earlier failed attempts remain retained separately.

### Retrieve procedures without changing contract authority

Optional procedural retrieval embeds five synthetic runbooks using local `all-minilm:22m` and searches their real 384-dimensional IRIS vectors with `VECTOR_COSINE`. Set `SILENTSHIFT_EMBED_BASE_URL` to the IRIS-reachable local Ollama base address, for example `http://host.lima.internal:11434` with Colima, and `SILENTSHIFT_EMBED_MODEL=all-minilm:22m`. Only the explicit local Ollama port 11434 route is accepted. Ensure the model is installed locally before opting in; bootstrap does not download it or seed embeddings.

Seed the procedures and run six authored retrieval probes explicitly:

```sh
uv run python scripts/verify_native_runbooks.py --allow-local-embedding-calls
```

This performs local embedding calls but creates no LLM investigation. The workbench preserves the top two retrieved procedures; the current prompt passes at most one 400-character excerpt through `GetRelatedRecords`. Procedures guide investigation and never authorize a conversion, amendment or release. This is procedural guidance, not a verified search over previous investigations or a relevance benchmark.

### Find a precedent without borrowing its authority

The **Similar precedents** panel shows up to three real resolved cases or approved amendments with source IDs, outcomes and cosine scores. Local `all-minilm:22m` produces 384-dimensional embeddings stored in a native IRIS `VECTOR` column. The production retrieves them before the native agent's fourth read-only tool, `find_similar_precedents`. Current contracts and deterministic policy remain the release authority.

```sh
uv run python scripts/verify_native_precedents.py --seed --allow-local-embedding-calls
```

The first seed indexed 15 actual resolved demo cases and one approved amendment. New completed cases are indexed through the production. The November 4 live five-case run passed 5/5 with all four reads; a retrieved past delivery could not release a critical current order. See [the precedent walkthrough](PRECEDENTS.md) for commands, screenshots, the misleading-history test and exact runtime limits. The successful repeat used a warmed local model and serialized execution; cold or loaded attempts that timed out are retained separately.

### Package the native backend with IPM

The public native package is **0.2.0**. Use [INSTALL.md](../INSTALL.md) for installation and its optional public-package verification. [Package maintenance](IPM.md) documents manifest hooks, publishing and retained package evidence.

## API and data boundaries

All endpoints are under `/silentshift/api`, protected by IRIS password authentication plus `SSView`. Reviews require `SSReview`. Browser credentials live only in memory. Use TLS outside loopback. `SSApplication` grants database permissions during the REST application only; end-user roles have no permanent database write privilege.

| Endpoint | Behavior |
| --- | --- |
| `GET /health`, `/overview`, `/cases`, `/cases/:id` | Actual production/configuration, counts and evidence; bounded pagination |
| `GET /reviews` | Reviewer-only pending native Workflow tasks, case versions and recorded completion recovery |
| `POST /messages` | Strict partner JSON only; server selects reference authority; exact decimal strings or integers for business numbers |
| `GET /scenarios`, `POST /scenarios/:id/run` | Synthetic fixed-clock replay; required stable UUID `run_id` |
| `POST /cases/:id/review` | `APPROVE`/`REJECT`, reason, expected version and idempotency key; critical contradictions cannot be bypassed |
| `GET /policies` | Current enforced policy rules/version |
| `GET /evaluations`, `POST /evaluations` | Measured reports reconstructed from five persisted native case IDs; capture never invokes a model |

Unknown references, malformed agent output, evidence gaps and dependency failures hold the message. No auto-repair transformation is applied. Source/event IDs deduplicate ingestion; changed content under the same key conflicts. Transactions and unique receipts protect only the included IRIS simulator; an external destination would need its own idempotency protocol.

## Developer Community articles

Both technical articles are publicly readable and link back to the Open Exchange application:

- [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production)
- [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery)

The articles describe their recorded experiments; those historical counts are separate from later verification runs.

## Documentation and submission

[PRD](../PRD.md) · [Design](../DESIGN.md) · [Architecture](../ARCHITECTURE.md) · [Native SDK evidence](NATIVE_AI_HUB.md) · [Test plan](TEST_PLAN.md) · [Security](../SECURITY.md) · [Contest compliance](CONTEST_COMPLIANCE.md) · [Submission ledger](SUBMISSION_CHECKLIST.md) · [Open Exchange copy](OPEN_EXCHANGE_COPY.md) · [Demo script](DEMO_SCRIPT.md)

The verified deadline is November 8 at 23:59:59 EST / November 9 at 10:29:59 IST. The demo is public on YouTube, SilentShift appears in contest 49, and the dedicated DPI-I-689 link and Package Manager option are saved in Open Exchange. Both Developer Community articles are publicly readable and link the application. The questionnaire already has a submitted receipt. Current release and registry-install results are in the [submission checklist](SUBMISSION_CHECKLIST.md); no organizer award is claimed.

## License and attribution

SilentShift source is [MIT](../LICENSE). The proprietary InterSystems EAP runtime is separately licensed and excluded. Native patterns derive from the MIT-licensed official AI Hub development template and community interoperability examples; gateway configuration derives from [webgateway-examples](https://github.com/intersystems-community/webgateway-examples/tree/923316d36da1b7ee8382f7faaf145139996f243d/demo-compose). Manrope and IBM Plex Mono font license notices ship in `web/public/licenses/`; Lucide icons use ISC licensing. Product branding is original to this source implementation; no claim of market novelty or production readiness is made.
