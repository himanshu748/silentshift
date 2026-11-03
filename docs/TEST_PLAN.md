# Verification contract

Local functions, browser failure paths, native integrations and external submission each need their own evidence.

| Layer | Required cases | Command / acceptance |
|---|---|---|
| Pure semantic engine | Quantity/unit, currency/scale, product/business unit, effective amendment, conflicts, no refs, stale/future/time semantics, invalid decimals | `uv run pytest -q` |
| Policy properties | Critical release veto, missing coverage, malformed/extra JSON, unknown evidence, duplicate effects, uncertainty | Hypothesis tests included in pytest |
| Evaluation | Checksum, missing/partial native data, wrong build, invalid tools, routing disagreement and null metrics | Pytest evaluation tests; `python -m silentshift.evaluation` |
| Frontend static | Strict types and production bundle | `npm --prefix web run check` and `npm --prefix web run build` |
| Browser failure path | Eight workbench screens, native disconnection, no invented data, login failure, keyboard, mobile, reduced motion | `npm --prefix web run test:e2e`; not native success evidence |
| Connected browser reads | Actual cases/evidence/policy/timeline/precedents, native Review queue, permissions, eight routes, mobile keyboard scroll, reduced motion | `SILENTSHIFT_NATIVE_E2E=1 npm --prefix web run test:e2e:native`; no mocks or mutations |
| Native vertical slice | Service → process → native agent/tools → policy → persisted route | `uv run python scripts/verify_native.py --allow-model-calls` with configured runtime and authorized inference |
| Native safety | All five scenarios, idempotent retry and critical manual-release veto | Verification script, SQL receipts and Visual Trace |
| Permission isolation | Anonymous denied; viewer review denied; reviewer safe approval/rejection | Separate viewer/reviewer credentials and actual REST calls |
| Provider calls | Actual paired messages in the original session, success/failure, bounded transport | `scripts/verify_native_provider.py`; separate local SDK failure probe |
| Native Workflow | Real pending tasks, reasons/versions/keys, approve/reject/concurrent one receipt | `scripts/verify_native_review_queue.py --allow-new-synthetic-cases`; no LLM inference |
| Vector precedents | Actual resolved sources and approved amendment, native vector metadata/search, four tools, misleading-history veto | `scripts/verify_native_precedents.py`; see `PRECEDENTS.md` for mutation/read-only flags |
| Custom adapter | Actual file intake, one/zero receipts, ack recovery, replays and invalid inputs | `scripts/verify_native_adapter.py --allow-local-model-calls`; two synthetic investigations |
| Failures and recovery | Agent timeout/malformed output, late response, missing refs, restart, unknown delivery result | Controlled native tests; compare final state/receipts, never agent self-report |
| Clean install | Official build 154, fresh namespace, source bootstrap or real IPM install, installed asset origins | Run README / IPM guide; record actual install command, archive hash and native gate |
| Release | Relevant diff/ignore/secret audit, no runtime binaries, public repo and OEX/contest receipts | Manual/automated audit plus actual external confirmation URLs |

Current passing evidence belongs in `BUILD_STATUS.md`. Model usage/cost remains unavailable unless actually recorded. No API interception, fixture model proposal or static screenshot counts as a native agent run.
