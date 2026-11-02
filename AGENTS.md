# SilentShift engineering contract

SilentShift catches semantic contradictions in technically successful integrations. Read `PRD.md`, `ARCHITECTURE.md`, and `DESIGN.md` before changing the journey.

- The core runs in IRIS Community AI Hub **2026.3.0AI.154.0**: real Business Service → Business Process → native `%AI.Agent` → deterministic Embedded Python policy → Business Operations. An outside-IRIS pipeline does not satisfy this contract.
- The agent proposes; server policy authorizes. Evidence tools are read-only and case-scoped. Missing evidence, malformed results, timeouts, and conflicting references never justify automatic release. Critical contradictions cannot be manually bypassed.
- Keep original payloads, immutable reference snapshots, audit events, correlation IDs, native trace IDs, decisions, and delivery receipts. Idempotency must survive restarts. Never deliver a quarantined case.
- Use strict TypeScript and validate API boundaries. Use Python Decimal for business arithmetic. Keep dependencies and abstractions small. Synthetic fixtures must be labeled; never seed them as measured operational history.
- Follow Signal / Substance typography and colors. Controls must work, have accessible names and focus, and fit mobile. Respect reduced motion. Health, metrics and case records come from the real API; show disconnected/empty states when unavailable.
- Run `uv run pytest`, `npm --prefix web run check`, `npm --prefix web run build`, and `npm --prefix web run test:e2e` as applicable. `python scripts/verify_native.py` exercises the actual IRIS endpoint; local unit/browser checks do not replace it.
- Credentials belong outside Git. Never log keys, publish EAP binaries or push derived runtime images. No paid calls, infrastructure purchases or billing changes without authorization. Narration uses Deepgram only.
- Before completion inspect the diff, run the real entry point and relevant failure paths, and update `docs/BUILD_STATUS.md`. Distinguish source implemented, locally tested, native verified, published, and submitted. No invented screenshots, usage, benchmarks or external confirmations.
- Submission and bonuses follow `docs/CONTEST_COMPLIANCE.md`. Keep repository, Open Exchange and contest states separate. Stop at credential/identity or legal-acceptance gates requiring the user; do independent authorized work meanwhile.
