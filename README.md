# SilentShift

**Catch the lies hidden inside successful integrations.**

SilentShift compares technically valid orders and payments with independent business contracts, asks a native IRIS AI Hub agent to investigate the evidence, and constrains its recommendation with deterministic policy before delivery or quarantine.

**Native core verified on Community AI Hub build154U.** All five frozen synthetic scenarios passed through the real Business Service, Business Process, native agent/tools, Embedded Python policy and routing Operations. A fresh-volume installation repeated the5/5 result. Public source/submission preparation remains in progress; no public deployment or contest confirmation is claimed. See [build status](docs/BUILD_STATUS.md) for evidence and remaining gates.

## What is implemented

- Native Business Service → Business Process → reference/AI/destination/quarantine Operations, with SQL-backed case snapshots, append-only audit and idempotent simulator receipts.
- A native `%AI.Agent` with three case-scoped read-only evidence tools, structured recommendations and bounded iterations/tokens. It never controls routing directly.
- An Embedded Python semantic and safety engine for units, currency scales, products, business units, effective amendments, conflicting authority and event-time semantics.
- Seven API-backed workbench views, authenticated reviews, raw message inspection, scenario replay and measured evaluation records. Offline state contains no operational seed data.
- Five frozen synthetic scenarios, independent ground-truth rationales and a checksum. Scenario E visibly injects a hostile validator input **after** a native reply; it preserves the actual model response separately.

The destination is an IRIS-persisted simulator. The first passing native run had4/5 correct model proposals and5/5 final decisions; the fresh-volume repeat had5/5 proposals and5/5 final decisions, with zero unsafe deliveries in both. These are two runs of five synthetic examples. The deterministic baseline also solves all five, so there is no demonstrated AI accuracy uplift or general performance claim. Session token totals and billing cost remain unavailable.

**Start with the [judge walkthrough](docs/JUDGE_GUIDE.md)** for the actual held/delivered pair, native reproduction steps and [all four trial results](docs/evidence/native-summary.json), including failed attempts.

![A real currency investigation held by deterministic policy](docs/assets/native-currency-quarantine.png)

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

The browser suite starts its own loopback Vite server with an intentionally unreachable upstream. It tests genuine failure states at 1440×960 and 390×844, all seven routes, keyboard focus, login failure and reduced motion. It does **not** prove connected cases or native integration. Screenshots are saved under `evidence/browser/`.

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

1. Sign in to the [official AI Hub EAP portal](https://evaluation.intersystems.com/Eval/early-access/AIHub). Download Community **2026.3.0AI.154.0** for the Docker host's architecture. The [official template](https://github.com/intersystems-community/ai-hub-dev-template/tree/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7) documents local image loading. No EAP software is bundled here.
2. Start Docker with a modern Compose CLI and enough host storage for its VM, EAP image and persistent manager volume. Setup detects either `docker compose` or standalone `docker-compose` version 2+. A remote Docker context may be used with a source checkout on that host; ordinary remote Docker bind mounts do not upload the local repository. Do not create a paid host or subscription without authorization.
3. Load the official archive outside this repository:

   ```sh
   docker load -i "/absolute/path/to/official-build154-docker.tar.gz"
   docker images
   ```

4. Copy `.env.example` to `.env` and restrict it with `chmod 600 .env`. Set `IRIS_IMAGE` to the exact loaded tag. Supply distinct viewer/reviewer account names and unique passwords, plus a gateway password. Use literal `KEY=value` entries; single-quote values containing `$` or `#`. Do not add inline comments or shell commands. Existing accounts are preserved by setup; their configured credentials must actually match.
5. Configure a supported tool-capable model. The native SDK supports an OpenAI-compatible provider, including local Ollama. Its model must support function calling and be reachable from IRIS. Set `SILENTSHIFT_MODEL`, `SILENTSHIFT_LLM_BASE_URL` and `SILENTSHIFT_LLM_API_KEY` explicitly for local inference. An existing cloud key does not grant permission to spend. No provider charges are authorized by this setup.
6. Run:

   ```sh
   uv run --env-file .env python scripts/doctor.py
   uv run --env-file .env python scripts/bootstrap.py
   ```

Bootstrap validates the image and credentials, renders ignored `.local/gateway/CSP.ini`, starts the preloaded IRIS image, creates the `SILENTSHIFT` interoperability namespace, loads/compiles classes, seeds independent references and starts the production and separate Web Gateway. It does not inject cases or invoke a model. The optional Dockerfile is local-only; Compose uses the preloaded image directly. Never push EAP or derived runtime images.

The gateway binds to `127.0.0.1:52773`; native 1972 is internal. The IRIS manager volume retains SQL state. **Do not run `docker compose down -v` on retained evidence.** Use ordinary stop/start for recovery testing. Read `.local/bootstrap.log` locally after a bootstrap failure; do not publish diagnostics containing secrets.

### Local Ollama configuration

The verified local option preserves Qwen3's tool template with an explicit8192-token context and temperature0.2. The base4B instruct model is about2.5GB. These commands download weights and create an alias; they do not invoke inference or a paid provider:

```sh
ollama pull qwen3:4b-instruct
ollama create qwen3-silentshift:4b-instruct -f config/Ollama.4b.Modelfile
```

Set `SILENTSHIFT_MODEL=qwen3-silentshift:4b-instruct`, `SILENTSHIFT_LLM_API_KEY=ollama` and, for Colima, `SILENTSHIFT_LLM_BASE_URL=http://host.lima.internal:11434/v1/`. Verify reachability from the IRIS container; this address reaches the existing host loopback service. For Docker Desktop use its documented host address. The adapter uses build154's `extra_params` for `reasoning_effort=none`; strict parsing never repairs a model answer. Other supported providers remain configurable. The earlier1.7B configuration is retained for reproducing failed trials and is not the verified default.

## Prove the native journey

Use the reviewer account for the complete safety gate. The following command invokes five native investigations, plus idempotent retries that must reuse the same case/receipt. Run it only with local inference or an explicitly authorized provider budget:

```sh
uv run --env-file .env python scripts/verify_native.py --allow-model-calls
```

It checks actual build 154/production status, anonymous denial, all three native evidence reads, nonempty trace IDs, expected policy/routing, one or zero simulator receipts, safe replay, critical reviewer-release denial and persisted evaluation agreement. Evidence goes to ignored `evidence/native/latest.json`. The Evaluations view reads the server-persisted report. A viewer-only execution cannot pass the critical reviewer-policy gate.

Inspect Visual Trace in IRIS using the recorded session ID and an appropriately privileged portal account. Actual checks also cover viewer denial, critical-release veto, typed/blank review reasons, rejection resolution, concurrent approval with one receipt, and restart/recreation persistence. Reference-limit integration tests invoke no model and preserve their isolated synthetic rows:

```sh
uv run --env-file .env python scripts/verify_native_boundaries.py
```

Use `--context`/`--container` when your Docker naming differs. Network-loss recovery, provider cancellation, real external delivery and broader stochastic trials remain unverified; a process timeout does not prove provider cancellation.

## API and data boundaries

All endpoints are under `/silentshift/api`, protected by IRIS password authentication plus `SSView`. Reviews require `SSReview`. Browser credentials live only in memory. Use TLS outside loopback. `SSApplication` grants database permissions during the REST application only; end-user roles have no permanent database write privilege.

| Endpoint | Behavior |
|---|---|
| `GET /health`, `/overview`, `/cases`, `/cases/:id` | Actual production/configuration, counts and evidence; bounded pagination |
| `POST /messages` | Strict partner JSON only; server selects reference authority; exact decimal strings or integers for business numbers |
| `GET /scenarios`, `POST /scenarios/:id/run` | Synthetic fixed-clock replay; required stable UUID `run_id` |
| `POST /cases/:id/review` | `APPROVE`/`REJECT`, reason, expected version and idempotency key; critical contradictions cannot be bypassed |
| `GET /policies` | Current enforced policy rules/version |
| `GET /evaluations`, `POST /evaluations` | Measured reports reconstructed from five persisted native case IDs; capture never invokes a model |

Unknown references, malformed agent output, evidence gaps and dependency failures hold the message. No auto-repair transformation is applied. Source/event IDs deduplicate ingestion; changed content under the same key conflicts. Transactions and unique receipts protect only the included IRIS simulator; an external destination would need its own idempotency protocol.

## Documentation and submission

[PRD](PRD.md) · [Design](DESIGN.md) · [Architecture](ARCHITECTURE.md) · [Native SDK evidence](docs/NATIVE_AI_HUB.md) · [Test plan](docs/TEST_PLAN.md) · [Security](SECURITY.md) · [Contest compliance](docs/CONTEST_COMPLIANCE.md) · [Submission ledger](docs/SUBMISSION_CHECKLIST.md) · [Demo script](docs/DEMO_SCRIPT.md)

The verified deadline is November 8 at 23:59:59 EST / November 9 at 10:29:59 IST. Official rules and organizer clarifications are linked in the compliance document. A public repository alone is not a contest entry. Open Exchange and contest confirmation remain separate blocked milestones. No bonuses are marked earned from source inspection.

## License and attribution

SilentShift source is [MIT](LICENSE). The proprietary InterSystems EAP runtime is separately licensed and excluded. Native patterns derive from the MIT-licensed official AI Hub development template and community interoperability examples; gateway configuration derives from [webgateway-examples](https://github.com/intersystems-community/webgateway-examples/tree/923316d36da1b7ee8382f7faaf145139996f243d/demo-compose). Manrope and IBM Plex Mono font license notices ship in `web/public/licenses/`; Lucide icons use ISC licensing. Product branding is original to this source implementation; no claim of market novelty or production readiness is made.
