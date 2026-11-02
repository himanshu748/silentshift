# Verification contract

Local functions, browser failure paths, native integrations and external submission each need their own evidence.

| Layer | Required cases | Command / acceptance |
|---|---|---|
| Pure semantic engine | Quantity/unit, currency/scale, product/business unit, effective amendment, conflicts, no refs, stale/future/time semantics, invalid decimals | `uv run pytest -q` |
| Policy properties | Critical release veto, missing coverage, malformed/extra JSON, unknown evidence, duplicate effects, uncertainty | Hypothesis tests included in pytest |
| Evaluation | Checksum, missing/partial native data, wrong build, invalid tools, routing disagreement and null metrics | Pytest evaluation tests; `python -m silentshift.evaluation` |
| Frontend static | Strict types and production bundle | `npm --prefix web run check` and `npm --prefix web run build` |
| Browser failure path | Seven screens, native disconnection, no invented data, login failure, keyboard, mobile, reduced motion | Browser test command and actual screenshots; not native success evidence |
| Native vertical slice | Service → process → native agent/tools → policy → persisted route | `uv run python scripts/verify_native.py --allow-model-calls` with configured runtime and authorized inference |
| Native safety | All five scenarios, idempotent retry and critical manual-release veto | Verification script, SQL receipts and Visual Trace |
| Permission isolation | Anonymous denied; viewer review denied; reviewer safe approval/rejection | Separate viewer/reviewer credentials and actual REST calls |
| Failures and recovery | Agent timeout/malformed output, late response, missing refs, restart, unknown delivery result | Controlled native tests; compare final state/receipts, never agent self-report |
| Clean install | Official image load on154, source compile/bootstrap, fresh namespace, documented setup | Run README from a clean runtime; record build/image and output |
| Release | Relevant diff/ignore/secret audit, no runtime binaries, public repo and OEX/contest receipts | Manual/automated audit plus actual external confirmation URLs |

Current passing evidence belongs in `BUILD_STATUS.md`. Model usage/cost remains unavailable unless actually recorded. No API interception, fixture model proposal or static screenshot counts as a native agent run.
