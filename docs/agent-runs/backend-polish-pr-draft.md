# Draft PR prepared — not opened

**Title:** `chore: prepare native 0.3.1 and finish the verified judge path`

**Base:** `main` · **Head:** `backend-polish-nov10` · **State:** Draft

Opening this PR is the next single gated action. No merge, closure/comment on another PR, release or publication is included.

---

SilentShift's public native package remains 0.3.0, while the voting-week provider/workbench and backend maintenance work has lived on separate branches. This draft consolidates that work into an unpublished native 0.3.1 candidate and gives judges a source Compose path that starts the real workbench and proves the keyless native trace.

The backend changes add redacted host/setup diagnostics, compact internal acknowledgments, shared evidence/configuration helpers, bounded host settings and compiler-exported Storage. The inherited provider/cited-prose path retains the deterministic veto: cited evidence may add containment, never release a rule hold. The source frontend remains separately versioned at 0.2.1. The changelog separates package changes from source-only UI and tooling.

The latest finish fixes a real shallow-history CI failure, aligns the connected test with the actual prompt version, produces missing cases through the real Scenario Lab operator path, and repairs fresh-clone Compose initialization. It does not modify the native execution code or frozen routing engine to make the finish pass.

## Verified

Native target: legally loaded **2026.3.0AI.154.0 Community / 154U ARM64** only. All cases are synthetic; delivery is to the simulator.

- [x] Hosted main rerun actually executes and passes: [42569241885](https://github.com/himanshu748/silentshift/actions/runs/42569241885).
- [x] Candidate code snapshot `7b3d5efafb07fd54530c912f6b9cdbb710462020` passes hosted pytest/types/build and 54 browser checks: [42818397027](https://github.com/himanshu748/silentshift/actions/runs/42818397027). The final docs/evidence commit is separate from that native source snapshot.
- [x] Fresh GitHub candidate clone: `uv run pytest -q` — **393 passed in 31.29s**; `npm run check && npm run build` pass. Existing nonfatal dependency directive warnings remain.
- [x] `uv run python scripts/verify_bonus_release.py --source load --version 0.3.1 --execution-mode recorded-replay ... --execute` — new isolated container, no application source mounts, explicit startup, **7 native classes / 22 methods**, first replay **12/12**. [Exact command and output](https://github.com/himanshu748/silentshift/blob/backend-polish-nov10/docs/evidence/voting-finish-nov10/candidate-031-command.txt).
- [x] `uv run python scripts/trace_example.py ...` — repeat **12/12**, sessions **24 / 58** across both recorded runs, held with no deliveries.
- [x] `uv run python scripts/verify_ipm_clean.py --archive ... --execute` — actual exported package installed from a local-filesystem repository in a second pristine container; empty/stopped application confirmed. This is not public-registry 0.3.1 installation.
- [x] Fresh source live `scripts/verify_native.py --allow-model-calls` through the real Scenario Lab API — **5/5 final routes**, raw proposals **3/5**, local Ollama and local embeddings. No fabricated delivered/precedent states.
- [x] `SILENTSHIFT_NATIVE_E2E=1 ... npm --prefix web run test:e2e:native` — **16/16**, desktop/mobile, real delivered amendment, vector/tool evidence and review permissions. Exact prompt assertion remains strict.
- [x] Fresh GitHub clone: `./scripts/judge-compose.sh --project silentshift-judge-finish-fixed-nov10 --api-port 53033 --web-port 5193` — actual native production + workbench, replay **12/12**, session **2**, real browser login and case readback.
- [x] Native Destination/Quarantine compact XML bodies and routing Event Logs captured. Temporary read grants restored exactly.
- [x] Ruff reduced from **83 to 40** safe findings; every remainder has a file/line/rule/reason in `docs/RUFF_REMAINING.md`. No blanket ignores or clean-lint claim.

[Current scoped verification](https://github.com/himanshu748/silentshift/blob/backend-polish-nov10/docs/JUDGE_VERIFICATION.md#voting-week-finish--fresh-github-clones) · [aggregate receipt](https://github.com/himanshu748/silentshift/blob/backend-polish-nov10/docs/evidence/voting-finish-nov10/candidate-031-summary.json) · [failure history](https://github.com/himanshu748/silentshift/blob/backend-polish-nov10/docs/evidence/voting-finish-nov10/compose-failures.json) · [native source identity](https://github.com/himanshu748/silentshift/blob/backend-polish-nov10/docs/evidence/voting-finish-nov10/candidate-031-source-identity.json).

## Limits and owner decisions

- [ ] Review before merge; do not merge/publish from this draft approval alone.
- [ ] Public native IPM/OEX stay **0.3.0** until a separate approved publication and anonymous clean registry verification. The existing public-package replay launcher intentionally stays pinned to 0.3.0.
- [ ] Close superseded PR #3 and ImgBot PR #2 only with separate owner approvals.
- [ ] Submit the public-0.3.0 OEX description/logo/capture correction separately, preserving contest/IPM/idea/video/MP4/articles. Never cancel a pending approval.
- [ ] Merge, v0.3.1 tag/release, IPM publication, OEX version update and optional static Pages publishing each remain gated. See `docs/IPM.md`.
- [ ] Protected uncommitted UI/article/social edits and partial sealed-benchmark results are excluded. Earlier CSV browser and approval/concurrency receipts retain their original scope; they were not rerun here.
- [ ] Other model providers are configuration/protocol-tested, not live-qualified. No hosted demo, x64/109 test, accuracy uplift, award or bonus qualification is claimed.

No spending, EAP/model redistribution, main push, duplicate bug/questionnaire, OEX save, external message or publication occurred in the finish. Existing native instances and failed receipts are retained; the documented temporary pauses addressed a constrained local VM without deleting data.
