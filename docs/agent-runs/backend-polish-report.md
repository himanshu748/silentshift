# Backend polish and voting-week finish

Checked **2026-11-10 18:27:28 IST**. Work is pushed only to `backend-polish-nov10`. Remote main remains `a10de3f61e1d809b374832a4db67761318bc16ea`. Candidate native **0.3.1** is prepared and locally clean-install verified, **not published**. Public native IPM/OEX remain **0.3.0**; React remains **0.2.1**.

## Gate results

| Requested work | Result | Evidence |
| --- | --- | --- |
| Restore hosted CI | Main and backend execute and pass. The first real backend failure was a shallow-history lookup; `fetch-depth: 0` preserves the frozen assertion. No billing/settings change or skipped check. | [Main run](https://github.com/himanshu748/silentshift/actions/runs/42569241885), [candidate run](https://github.com/himanshu748/silentshift/actions/runs/42818397027), [failure/success metadata](../evidence/voting-finish-nov10/ci-restored.json) |
| Real connected setup | Fresh live Scenario Lab submissions produced the delivered amendment and retrieved precedents. Updated only the stale exact prompt-version expectation. Full desktop/mobile connected suite **16/16 in 46.6s**. | [Connected receipt](../evidence/voting-finish-nov10/connected-final.json), [live 5/5](../evidence/voting-finish-nov10/fresh-live-five.json) |
| Native captures | Destination session **86**, Quarantine session **30**, both compact bodies and routing Event Logs captured. Temporary role/table reads restored exactly. | [Native UI receipt](../evidence/voting-finish-nov10/native-ui.json), [restoration](../evidence/voting-finish-nov10/permissions-restored.json) |
| Ruff | **40** remain, from **83**. Each has a file/line/rule/reason; no blanket ignores or clean-lint claim. This uses the owner's permitted explicit-exception option. | [Every finding](../RUFF_REMAINING.md), [receipt](../evidence/voting-finish-nov10/ruff-remaining.json) |
| One-command Compose | Fresh GitHub source stack starts IRIS + real React workbench, passes **12/12**, session **2**, in **35.451s**. Real same-origin browser login loaded the case and recorded-agent view. Read-only source, dedicated writable frontend volume, existing-instance guard. | [Receipt](../evidence/voting-finish-nov10/compose-final.json), [guide](../JUDGE_COMPOSE.md) |
| Prepare native 0.3.1 | Fresh GitHub source `7b3d5efafb07fd54530c912f6b9cdbb710462020`: clean source load, explicit startup, **7 classes / 22 methods**, two **12/12** replays. Real exported archive installed successfully into a second pristine 154U ARM64 container, with the application empty/stopped. No public-registry 0.3.1 claim. | [Candidate summary](../evidence/voting-finish-nov10/candidate-031-summary.json), [archive install](../evidence/voting-finish-nov10/candidate-031-install.json) |
| Local / hosted checks | Fresh candidate **393 pytest in 31.29s**, TypeScript/build pass. Hosted candidate **393 pytest in 23.17s** and **54 browser checks in 1.1m** pass. | [Local output](../evidence/voting-finish-nov10/candidate-031-pytest.txt), [hosted output](../evidence/voting-finish-nov10/candidate-031-ci-output.txt) |

The native live gate used local Qwen and embeddings; final routes passed **5/5**, while raw agent proposals matched **3/5**. No broader accuracy claim follows. Only the module version differs among package files between that live snapshot and the prepared candidate; [identity](../evidence/voting-finish-nov10/candidate-031-source-identity.json). Earlier CSV-browser and approve/reject/concurrency receipts retain their original scopes; neither was rerun or relabeled here. Sealed evaluation remains unfinished and untouched.

## Failures and changes retained

[Exact new commit inventory](../evidence/voting-finish-nov10/branch-inventory.json). New finish commits fix CI checkout history, make verification CLIs/check handling explicit, match the existing native prompt version, add and repair the source Compose launcher, and prepare the 0.3.1 manifest/project/changelog. No native runtime or deterministic policy edit was made in this finish; the branch already contained earlier provider/cited-prose and backend changes.

The connected run's transport interruption and first Compose OOM are retained, as is the fresh-clone read-only nested-mount failure. Verification then ran serially. The Compose repair moved writes into a dedicated frontend volume and added a guard instead of weakening checks or stopping arbitrary instances. [Failures](../evidence/voting-finish-nov10/compose-failures.json). No data, image, model or volume was deleted. Temporary pauses/restarts involved completed verification instances only; resource state is recorded in the running log.

The earlier body-capture crash recovered after native memory recovery and a fresh sign-in. [Delivered body](../assets/voting-finish-nov10/delivered-destination-body.jpg) · [held body](../assets/voting-finish-nov10/held-quarantine-body.jpg) · [delivered Event Log](../assets/voting-finish-nov10/delivered-event-log.jpg) · [held Event Log](../assets/voting-finish-nov10/held-event-log.jpg). The old metadata-exporter failure remains historical failed evidence.

## Public state and preserved work

The OEX correction bundle still targets **public native 0.3.0 / React 0.2.1**, not this unpublished candidate. The known public body has stale native 0.2.0/source-only CSV wording; dedicated DPI-I-689 is publicly visible, qualification unconfirmed. Existing gallery URLs read anonymously. The latest organizer thread has no new reply to the November 10 queue-check email. No email, OEX form save/Send, video upload, questionnaire or bug action ran. The broken OEX Categories asset remains an OEX-side issue; no report was sent.

Protected uncommitted UI/social/article work and partial sealed results remain outside the pushed candidate. No online-demo, Embedded Python, Java/.NET PEX, award or ranking claim changed. Static Pages and release copy remain drafts.

## Exact next gates

**A — awaiting exact `submit`: open one draft PR `backend-polish-nov10` → `main`, with [the prepared title/body](backend-polish-pr-draft.md). Do only that one action. Do not merge, close another PR, comment or submit OEX.**

Then stop for each later action:

1. Close superseded PR **#3**, with its one-line explanation; separate approval.
2. Close ImgBot PR **#2**, with its one-line explanation; separate approval.
3. Prepare the single public-0.3.0 OEX description/logo/capture bundle in the owner form, preserve idea/contest/IPM/video/MP4/articles, screenshot, then stop. One approval permits the exact save + Send for approval action once; never cancel pending approval.
4. Phase 2 proof is now complete using the explicit Ruff inventory option. Merge, v0.3.1 tag/release, IPM publication and OEX version update still require separate owner decisions. [Prepared owner runbook](../IPM.md#owner-only-031-publication-runbook).
5. Optional static Pages publication has its own gate. It is not a hosted native demo.

No public action may be bundled into the draft-PR approval. The public-change freeze remains **November 16, 07:00 IST**.
