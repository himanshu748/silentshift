# Build status

Updated 2026-11-02 IST. **Overall: source and local verification delivered; mandatory native runtime gate BLOCKED. The full product is incomplete.**

## Observed checks

| Check | Result | Scope |
|---|---|---|
| `uv run pytest -q` | **107 passed** (6.42s observed) | Semantic/policy, evaluation, decimal regression and verification-client tests, including Hypothesis |
| Frozen scenario policy regression | **5/5** | Fixed test recommendations; no model invoked. Rule-only baseline also 5/5; no measured AI uplift |
| Native evaluation without export | `NOT_RUN`, null metrics, denominator 0 | No fixture proposals substituted for native results |
| Strict TypeScript / Vite build | Passed | API workbench source; build alone is not native behavior |
| Playwright browser suite | **20 passed** (34.2s initial run) | Genuine disconnected upstream, 1440×960 and 390×844, seven screens, login failure, keyboard/focus, reduced motion; no page errors/overflow |
| Browser screenshots | Captured and inspected | `evidence/browser/desktop-disconnected.png`, `mobile-disconnected.png`; no connected cases shown |
| Bootstrap Python/shell | Syntax and missing-config preflight passed | No container or model invoked |
| Native verification preflight | Correctly exits BLOCKED | Missing IRIS account environment; no native execution |
| Secret scan | Staged known-pattern check passed | 0 findings, 0 omitted; no history or unknown-format guarantee |
| GitHub Actions | Source prepared | Pinned official actions; no remote CI run |

## Implemented source

- PRD, design, architecture, concise Codex instructions and milestone gates.
- Embedded-Python-ready semantic engine, strict policy, five frozen synthetic scenarios, checksum and independent ground-truth rationales.
- Native AI Hub adapter with three scoped read-only tools, bounded reads and strict discovery allowlist.
- Native service/process/operations production; SQL cases, references, audit, reviews, delivery and evaluations; immutable snapshots and idempotency guards.
- Authenticated REST with viewer/reviewer resources, application-scoped database permission, constrained human proposals and final delivery policy recheck.
- Seven workbench views, API schemas, memory-only login, scenario/review controls, JSON/evidence/timeline and measured-metric rendering.
- Local-image Compose, separate gateway, safe bootstrap, environment doctor and actual-native verification/export command.
- Submission copy, verified rules/deadline, separate publication/OEX/contest ledger, bonus requirements and truthful demo walkthrough.

## Review repairs

Independent source review identified and the implementation repaired JSON float rounding/underflow masking business differences, credential forwarding through redirects, silent reference truncation, excessive viewer database rights, inconsistent build detection, empty trace/receipt checks, missing reviewer-policy coverage and evaluation-persistence agreement. Python regression tests cover applicable defects. Native repairs still need IRIS permission/concurrency/routing verification.

## Required runtime and external gates

- Official Community AI Hub **2026.3.0AI.154.0** kit unavailable; evaluation portal requires login. No kit download, license acceptance or restricted image publication occurred.
- Docker CLI installed, configured Colima daemon stopped. Compose v2 is not discoverable by `docker compose`. No installation/runtime startup attempted while disk is constrained.
- No supported provider key present. Installed Ollama gemma3:4b reports completion/vision, not required function calling. No model downloaded or provider charged.
- Disk remains constrained and volatile while the user frees space. This task removed only its reproducible `work/research` clones and `work/uv-cache`; no preexisting user files, source, evidence or credentials were deleted.
- Docker cloud left aside at the user's request; no paid host, subscription or billing change.
- **Unverified:** ObjectScript compilation, actual native tools, gateway/clean installation, five native routes, direct viewer database denial, separate viewer/reviewer access, restart/concurrency/timeout/late results, real external destination, connected browser journey and native metrics.
- **Unpublished/unsubmitted:** no public repository URL, deployment, YouTube video, Open Exchange application or contest confirmation. No bonuses marked earned.

## Resume here

Read README native setup and `docs/NATIVE_AI_HUB.md`. Make the official kit, sufficient Docker-host space, Compose and a tool-capable model available. Bootstrap; repair compile/runtime-specific issues. Run the reviewer native gate with local inference or an explicitly authorized budget, inspect Visual Trace/SQL receipts, execute remaining recovery/permission checks and verify the connected UI. Then proceed to recording and public source/OEX/contest completion. Official deadline evidence is in `CONTEST_COMPLIANCE.md`.
