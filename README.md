# SilentShift

**Catch wrong business meaning before delivery.**

An order arrives as `20 CASE`. Its approved contract says `240 EA`. The JSON is valid, but no approved conversion explains the change. SilentShift holds the order before the included destination simulator accepts it, then gives the integration operator the message, contract and reason in one investigation.

The same incoming value can be legitimate: an effective approved amendment authorizing `20 CASE` lets the order proceed. SilentShift makes that distinction using independent reference records, a native IRIS AI Hub investigation and deterministic Embedded Python policy.

**[Try the operator walkthrough](docs/JUDGE_GUIDE.md)** · [Public source](https://github.com/himanshu748/silentshift) · [Native setup](#native-build-154-setup) · [Verification ledger](docs/BUILD_STATUS.md)

**Demo video:** [Watch the walkthrough](https://youtu.be/a4dOcqu89EA) · **Open Exchange application:** [SilentShift on Open Exchange](https://openexchange.intersystems.com/package/SilentShift)

The public video plays at 1080p with English captions. Open Exchange is **awaiting review**; the two [technical articles](docs/articles/overview.md) are submitted for moderation. [Submission status and remaining steps](docs/SUBMISSION_CHECKLIST.md).

## Follow the evidence to a decision

Open an investigation to compare the original partner payload with its immutable reference snapshot. Inspect what the agent actually read, why policy held or released the message, and whether the simulator recorded a delivery. A trace ID connects that investigation to its native IRIS production session.

The agent proposes through four read-only, case-scoped evidence tools: current message, approved contracts, related records and similar precedents. Server policy owns the route: missing evidence, conflicting authority, malformed answers and timeouts cannot justify automatic delivery. A reviewer can resolve an eligible hold with a reason, version and idempotency key; critical contradictions retain their release veto. Native Workflow preserves the human task, including a recorded decision whose completion needs to be resumed.

![An approved amendment inspected in the working local application, with one simulator delivery](docs/assets/native-approved-delivery.png)

The native chain is Business Service → Business Process → reference/AI Operations → Embedded Python policy → destination or quarantine Operation. IRIS persists the payload, references, audit, review state and unique simulator receipt. The workbench provides eight API-backed views, including the native Review queue, raw payload inspection and a Scenario Lab with five labeled synthetic experiments.

**Verified boundary:** the core ran on official ARM64 Community AI Hub `2026.3.0AI.154.0` (`154U`), including a fresh-volume repeat. The destination is an IRIS simulator. The [evidence appendix](docs/JUDGE_GUIDE.md#evidence-appendix) retains passing and failed trials, baseline results and measurement limits. No public deployment, external ERP/bank delivery or contest registration is claimed.

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

## Native build 154 setup

**Runtime availability:** SilentShift is verified on **2026.3.0AI.154.0** and its build guard intentionally requires that version. The November 3 [organizer clarification](https://community.intersystems.com/node/590306) permits the newer **2027.1.0AI.109.0** after older kits were removed from the portal, and says judges will use an entry's declared build. SilentShift has not been verified on 109. These instructions require an authorized build 154 kit already obtained from InterSystems; contact the official program if it is no longer listed. This repository cannot redistribute the kit.

1. Sign in to the [official AI Hub EAP portal](https://evaluation.intersystems.com/Eval/early-access/AIHub). Download Community **2026.3.0AI.154.0** for the Docker host's architecture. The [official template](https://github.com/intersystems-community/ai-hub-dev-template/tree/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7) documents local image loading. No EAP software is bundled here.
2. Start Docker with a modern Compose CLI and enough host storage for its VM, EAP image and persistent manager volume. Setup detects either `docker compose` or standalone `docker-compose` version 2+. A remote Docker context may be used with a source checkout on that host; ordinary remote Docker bind mounts do not upload the local repository. Do not create a paid host or subscription without authorization.
3. Load the official archive outside this repository:

   ```sh
   docker load -i "/absolute/path/to/official-build154-docker.tar.gz"
   docker images
   ```

4. Copy `.env.example` to `.env` and restrict it with `chmod 600 .env`. Set `IRIS_IMAGE` to the exact loaded tag. Supply distinct viewer/reviewer account names and unique passwords, plus a gateway password. Use literal `KEY=value` entries; single-quote values containing `$` or `#`. Do not add inline comments or shell commands. Existing accounts are preserved by setup; their configured credentials must actually match.
5. Configure the local Ollama model `qwen3-silentshift:4b-instruct` and its IRIS-reachable `SILENTSHIFT_LLM_BASE_URL`. The provider gateway rejects other models and remote routes. It issues a short-lived capability for each native investigation; no external provider key is required.
6. Run:

   ```sh
   uv run --env-file .env python scripts/doctor.py
   uv run --env-file .env python scripts/bootstrap.py
   ```

Bootstrap validates the image and credentials, renders ignored `.local/gateway/CSP.ini`, starts the preloaded IRIS image, creates the `SILENTSHIFT` interoperability namespace, loads/compiles classes, seeds independent references and starts the production and separate Web Gateway. It does not inject cases or invoke a model. The optional Dockerfile is local-only; Compose uses the preloaded image directly. Never push EAP or derived runtime images.

The gateway binds to `127.0.0.1:52773`; native 1972 is internal. The IRIS manager volume retains SQL state. **Do not run `docker compose down -v` on retained evidence.** Use ordinary stop/start for recovery testing. Read `.local/bootstrap.log` locally after a bootstrap failure; do not publish diagnostics containing secrets.

### Local Ollama configuration

The verified local option preserves Qwen3's tool template with an explicit 8192-token context and temperature 0.2. The base 4B instruct model is about 2.5 GB. These commands download weights and create an alias; they do not invoke inference or a paid provider:

```sh
ollama pull qwen3:4b-instruct
ollama create qwen3-silentshift:4b-instruct -f config/Ollama.4b.Modelfile
```

Set `SILENTSHIFT_MODEL=qwen3-silentshift:4b-instruct` and, for Colima, `SILENTSHIFT_LLM_BASE_URL=http://host.lima.internal:11434/v1/`. Verify reachability from the IRIS container; this address reaches the existing host loopback service. For Docker Desktop use its documented host address. The model adapter uses build 154's `extra_params` for `reasoning_effort=none`; strict parsing never repairs a model answer. The live transport accepts only this local model and known local Ollama hostnames. The earlier 1.7B configuration is retained for reproducing failed trials and is not the verified default.

The native process wait defaults to 60 seconds. Set `SILENTSHIFT_AGENT_WAIT_SECONDS=120` before bootstrap for the tested resource-constrained local 4B configuration; only integers from 10 through 120 are accepted. One later adapter investigation took 117.491 seconds and completed within that explicit 120-second wait. Earlier 60-second attempts timed out and stayed held. A longer wait changes the local request deadline, not release policy, and a timeout does not establish provider cancellation.

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

Every local provider HTTP call produces typed interoperability request and response messages in the original case session. The retained approved-amendment case in session 374 made four calls (headers 381–388), then delivered once. The explicit SDK failure probe in session 316 recorded a real Ollama HTTP 400 and stayed quarantined with zero deliveries. Current four-tool runs made two exchanges per case. [Successful trace](docs/assets/provider-success-visual-trace.png) · [failure trace](docs/assets/provider-failure-visual-trace.png).

```sh
uv run python scripts/verify_native_provider.py --inspect-case CASE_ID
```

The [native AI Hub guide](docs/NATIVE_AI_HUB.md) maps each field, reproduces the failure and compares the scope with Langfuse. Unknown provider retries and billing cost stay null; actual HTTP response usage is distinct from session totals. Historical invocation/tool evidence remains in [AI_TRACING.md](docs/AI_TRACING.md). [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) is the implemented idea; organizer acceptance is unconfirmed.

Held transactions now enter a native IRIS Workflow worklist. Connect as the configured reviewer and open **Review** to inspect pending tasks, their original case evidence and policy. A critical contradiction permits rejection; approval remains blocked. Completed tasks leave the pending worklist, while the case keeps the reason, original version, idempotency key and native task receipt. Historical holds are readable and require a new investigation before a new review decision.

```sh
uv run python scripts/verify_native_review_queue.py --allow-new-synthetic-cases
```

The [54-check receipt](docs/evidence/review-queue.json) includes reviewer-only task listing, rejection, two concurrent identical approvals, one review receipt, one native completion response and one simulator delivery. The workbench also completed [actual approve and reject actions](docs/evidence/review-ui.json), shown in the [native worklist](docs/assets/review-native-worklist.png). These isolated synthetic cases skip LLM inference at the evidence-budget guard; existing procedural retrieval can use local embeddings. They do not alter the five evaluation cases.

The earlier controlled postcommit HTTP 503 recovery remains documented in [the Workflow receipt](docs/evidence/workflow.json) and [engineering story](docs/articles/engineering.md). Resume the original recorded request after an uncertain outcome; changing its reason, version or key creates a different decision and is rejected.

## Optional local intake and procedural guidance

### Accept partner JSON from a ready-file inbox

The custom native inbound adapter is dormant by default. Set `SILENTSHIFT_PARTNER_FILES_ENABLED=1` before bootstrap to opt in. Bootstrap creates `.local/partner-inbox` with mode `0700`; Compose mounts it at the adapter's fixed `/var/opt/silentshift/partner-inbox` path. Keep it owned for the trusted operator and container `irisowner`; partner payloads cannot choose a directory.

Write the raw UTF-8 partner **message** JSON to `<name>.json.part`, close it, then atomically rename it to `<name>.json.ready` on the same filesystem. Do not wrap it in a Scenario Lab request. Names contain 1–80 ASCII letters, digits, hyphens or underscores and begin with a letter or digit. The same server validation and reference authority apply as at `POST /messages`.

The adapter claims `.work`, retains the exact input bytes in `.done` or `.hold`, and writes `<name>.json.ack.json` from the persisted outcome. The acknowledgment includes its input SHA-256, case/trace IDs, policy result and simulator receipt. It preserves the first observed outcome: a later review decision changes the case, while its earlier held acknowledgement stays unchanged. Inspect the acknowledgement's timestamp and delivery count, then follow the case for current state. Uncertain dispatches and exhausted retries need operator inspection. Keep fewer than 256 active files per suffix and plan retention explicitly; the adapter deletes no input or archive.

The [file walkthrough](docs/PARTNER_INBOX.md) shows actual ready-file delivery and critical quarantine, with native Visual Trace screenshots. All 82 adapter assertions passed, including acknowledgement recovery and replay without another receipt. The [verification driver](scripts/verify_native_adapter.py) documents activation, bounded test calls and read-only `--inspect-file` use. Earlier failed attempts remain retained separately.

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

The first seed indexed 15 actual resolved demo cases and one approved amendment. New completed cases are indexed through the production. The current five-case run passed 5/5 with all four reads; a retrieved past delivery could not release a critical current order. See [the precedent walkthrough](docs/PRECEDENTS.md) for commands, screenshots, the misleading-history test and exact runtime limits. The successful repeat used a warmed local model and serialized execution; cold or loaded attempts that timed out are retained separately.

### Package the native backend with IPM

Follow the [IPM guide](docs/IPM.md) for a verified clean installation of the 43-class, nine-asset backend. IPM 0.10.10 installed it from a local filesystem repository on a fresh build-154 instance with no source mount. Installed Python origins and empty application tables passed; after explicit setup, the real API repeated all five final outcomes with four native tools. The package does not configure credentials, start the production or call a model merely by being installed. Public-registry installation and publication remain user-managed and unverified.

## API and data boundaries

All endpoints are under `/silentshift/api`, protected by IRIS password authentication plus `SSView`. Reviews require `SSReview`. Browser credentials live only in memory. Use TLS outside loopback. `SSApplication` grants database permissions during the REST application only; end-user roles have no permanent database write privilege.

| Endpoint | Behavior |
|---|---|
| `GET /health`, `/overview`, `/cases`, `/cases/:id` | Actual production/configuration, counts and evidence; bounded pagination |
| `GET /reviews` | Reviewer-only pending native Workflow tasks, case versions and recorded completion recovery |
| `POST /messages` | Strict partner JSON only; server selects reference authority; exact decimal strings or integers for business numbers |
| `GET /scenarios`, `POST /scenarios/:id/run` | Synthetic fixed-clock replay; required stable UUID `run_id` |
| `POST /cases/:id/review` | `APPROVE`/`REJECT`, reason, expected version and idempotency key; critical contradictions cannot be bypassed |
| `GET /policies` | Current enforced policy rules/version |
| `GET /evaluations`, `POST /evaluations` | Measured reports reconstructed from five persisted native case IDs; capture never invokes a model |

Unknown references, malformed agent output, evidence gaps and dependency failures hold the message. No auto-repair transformation is applied. Source/event IDs deduplicate ingestion; changed content under the same key conflicts. Transactions and unique receipts protect only the included IRIS simulator; an external destination would need its own idempotency protocol.

## Documentation and submission

[PRD](PRD.md) · [Design](DESIGN.md) · [Architecture](ARCHITECTURE.md) · [Native SDK evidence](docs/NATIVE_AI_HUB.md) · [Test plan](docs/TEST_PLAN.md) · [Security](SECURITY.md) · [Contest compliance](docs/CONTEST_COMPLIANCE.md) · [Submission ledger](docs/SUBMISSION_CHECKLIST.md) · [Open Exchange copy](docs/OPEN_EXCHANGE_COPY.md) · [Demo script](docs/DEMO_SCRIPT.md)

The verified deadline is November 8 at 23:59:59 EST / November 9 at 10:29:59 IST. The demo is public on YouTube. Open Exchange version 0.1.0 has been sent for approval with the contest option, Package Manager option and dedicated DPI-I-689 link saved. Both Developer Community articles are submitted for moderation. The contest Apply dialog still requires a published application, so registration is unconfirmed. Public IPM availability and installation remain unverified; the questionnaire already has a submitted receipt. No organizer award is claimed. See the [remaining submission steps](docs/SUBMISSION_CHECKLIST.md).

## License and attribution

SilentShift source is [MIT](LICENSE). The proprietary InterSystems EAP runtime is separately licensed and excluded. Native patterns derive from the MIT-licensed official AI Hub development template and community interoperability examples; gateway configuration derives from [webgateway-examples](https://github.com/intersystems-community/webgateway-examples/tree/923316d36da1b7ee8382f7faaf145139996f243d/demo-compose). Manrope and IBM Plex Mono font license notices ship in `web/public/licenses/`; Lucide icons use ISC licensing. Product branding is original to this source implementation; no claim of market novelty or production readiness is made.
