# 0.3.3 candidate — resumed runtime gate, November 12, 2026 (IST)

Source **`823ea8abbcc0130d5d480ca6308cfeecedab539e`** completed the runtime extension on the **same retained instance** that had independently installed the real local 0.3.3 archive in a pristine **154U ARM64** container. This is a resumed local-archive gate after the earlier disk stop, **not** a new clean clone, uninterrupted install, public-registry install, live five-case run or model-quality evaluation.

Actual results: API startup **HTTP 200**, production running, **8 native classes / 28 methods passed**, and **two 12/12 recorded API replays**, sessions **56** and **92**, both quarantined with no simulator delivery. Resumption took **17.38 seconds**, excluding earlier build/install and the paused interval. Native code and fixtures remain byte-identical to v0.3.2; no new inference or evaluation. Public IPM/OEX and the latest tag remain **0.3.2** until separately approved publication.

[Original pristine offline install](evidence/release-033-nov12/clean-install.json) · [resumed runtime receipt](evidence/release-033-runtime-nov12/summary.json) · [native output](evidence/release-033-runtime-nov12/native-suite.txt) · [first replay](evidence/release-033-runtime-nov12/replay-1.json) · [second replay](evidence/release-033-runtime-nov12/replay-2.json). The first local resumption attempt stopped on a duplicate private log filename before runtime validation; that runner error and its correction are retained with the receipt. Earlier namespace/disk failures remain in their original records.

## Earlier checkpoints

# Current public-package launcher — November 11, 2026 (IST)

A fresh GitHub clone of launcher fix `3edf75a9021fb3aa1dc679f1f58107ca2d0c1584` installed **public native 0.3.2** using literal `zpm "install silentshift"` in a new **154U ARM64** container with no source mounts. Production startup, **8 native classes / 28 methods** and **two 12/12 recorded replays** passed in **146.23 seconds**. The release assertion source is pinned to v0.3.2's commit `cfc4c27`. No fresh inference or live five-case rerun is implied. [Receipt](evidence/voting-nov11-judge/summary.json) · [native output](evidence/voting-nov11-judge/native-tests.txt) · [exact launcher output](evidence/voting-nov11-judge/command-output.txt).

The first attempt stopped at the unchanged disk guard after installation; its output is retained. Only the task-created container was stopped and the local VM disk expanded without deletion before the successful fresh-container retry. Host JUnit initially found an unconfigured Java launcher; selecting the already installed Homebrew JDK passed **7 tests**. **394 pytest**, TypeScript/build and **54 browser tests** passed. These setup failures are preserved, not relabeled as successful runs. Earlier public/archive/source checkpoints below retain their original scope.

# Public native 0.3.2 — November 11, 2026 (IST)

OEX now publicly shows **0.3.2**, and the public IPM archive downloads without authentication with manifest **0.3.2**. Its receipt-mode source matches the tested GitHub tag. [Publication and retained-link receipt](evidence/ipm-032-publication-nov11/publication.json) · [owner release screenshot](evidence/ipm-032-publication-nov11/oex-032-published.png).

The check below verified a fresh **offline** native archive installation. This publication readback inspected the separate public registry archive; it did **not** install that public artifact into another container. GitHub source/tag remains `cfc4c27`. No new model run, organizer-qualified bonus or award is claimed. Saved listing-body version wording was left unchanged. These notes remain local pending a separately authorized source push.

## Earlier checkpoint

# Fresh tagged 0.3.2 archive installation — November 11, 2026 (IST)

A clean GitHub clone of **v0.3.2**, commit **`cfc4c279853886a72772a92ad70c2e2c5eae3819`**, generated a new real IPM archive including the receipt-mode fix. The archive installed in a second pristine **154U ARM64** container with **no application source mounts or network during installation**. Checks passed: **5 deterministic cases**, **10 invalid-path rejections**, **4 Python module origins**, and **10 empty application tables**. The newly installed receipt-mode helper returned the correct persisted/legacy modes and rejected invalid metadata. Application production stayed stopped; no model calls were made.

[Current receipt](evidence/ipm-032-final-nov11/summary.json) · [package receipt](evidence/ipm-032-final-nov11/package.json) · [fresh-install receipt](evidence/ipm-032-final-nov11/install.json) · [commands/output](evidence/ipm-032-final-nov11/output.txt). This is an offline archive install, not a public-registry install or another live scenario/API run. **At this earlier archive checkpoint, GitHub v0.3.2 was released and IPM/OEX publication had not yet been performed; the newer publication readback above supersedes that state.** These verification notes are local pending a separately authorized push.

## Earlier checkpoint

# Receipt provenance follow-up — November 11, 2026 (IST)

The unpublished **0.3.2** source fix preserves saved investigation mode when a receipt is rebuilt under another deployment setting. On retained **154U ARM64**, the new regression failed against `50477f8`, then the fixed source passed **8 native classes / 28 methods**, **7 JUnit**, **394 pytest**, TypeScript/build and **54 browser checks**. Two separate IRIS sessions using replay/live process settings returned the same signed bytes and one receipt file for one unit-arranged synthetic persisted case. This is a same-instance native check, not a fresh clone, full container restart, new live model investigation or another archive install.

[Scoped receipt](evidence/receipt-mode-nov11/summary.json) · [commands and outputs](evidence/receipt-mode-nov11/output.txt). Policy, store, routing operations, investigator and frozen fixtures are unchanged. Earlier source/archive checks retain their named revisions below. Updated PR CI is pending the branch update; public 0.3.1 and unpublished 0.3.2 remain distinct.

## Earlier checkpoint

# Citation follow-up — November 11, 2026 (IST)

The missing-citation failure is fixed in the unpublished **0.3.2** source candidate. The policy, assessment bridge, routing store/process and frozen inputs remain byte-identical. Three predeclared sets passed **15/15**, followed by a final **5/5** after message-storage checks. All **20** signed receipts verified independently. Native **8 classes / 26 methods**, **394 pytest**, TypeScript/build and **54** browser checks passed. The regenerated archive installed in a pristine offline container; application tables stayed empty and production stopped. Live checks are a retained-instance upgrade, not a fresh archive model run. Hosted branch CI is still pending the gated push.

[Fix and limitations](CITATION_COMPLETENESS.md) · [new receipt](evidence/citation-fix-nov11/summary.json). **0.3.2 remains unpublished; public 0.3.1 is unchanged.** The earlier failed run below remains history and is not rewritten as passing.

## Earlier checkpoint

# Java PEX candidate — November 11, 2026 (IST)

Branch `feat/java-pex-nov11` prepares native **0.3.2**, not current-main/public-package verification. Main remains `1c92e095dcc2e9bc7493f1ad5e4a9b9355d78ec1`; public IPM/OEX remain **0.3.1**. Runtime code was cloned locally at `ddd01add213db99167444bbd742485ed12dbdeea` before the source Compose run; later changes are verification harness/tests and documentation. [New receipt and exact scopes](evidence/bonus-claims-nov11/java-pex.json) · [policy/fixture identity](evidence/bonus-claims-nov11/java-pex-policy-identity.json).

**Historical release-gate failure, superseded by the citation follow-up:** the API five-case run passed 5/5, but an explicit ObjectScript repeat passed 4/5. The approved-amendment model output omitted required citations; the unchanged `EVIDENCE_COMPLETE` gate held it for review. All ten cases produced valid Java receipt responses. The failing assertion is retained, not weakened. No further model retry or policy/prompt change was made; the second fresh archive install and hosted branch CI remain unverified. [Failure](evidence/bonus-claims-nov11/java-pex-objectscript-repeat.json).

Fresh local source Compose passed two 12/12 recorded replays and 8 native classes / 25 methods. A separately pristine, no-source-mount IPM source load passed startup and the same native suite. Its API five-case local-Ollama run passed 5/5; all five exported receipts passed independent OpenSSL verification. The subsequent direct ObjectScript repeat produced five valid Java receipts but failed its routing expectation as detailed above. No failed run is presented as passing. The exported archive was inspected; a second fresh archive installation did not run after the failure.

## Earlier verified checkpoints

# Backend-polish verification — November 10, 2026 (UTC)

## Voting-week finish — fresh GitHub clones

**November 10, 2026 (IST).** The prepared native **0.3.1** source snapshot is **`7b3d5efafb07fd54530c912f6b9cdbb710462020`**, on `backend-polish-nov10`. Main and public native IPM/OEX remain **0.3.0**, React **0.2.1**. No merge, PR action, tag/release, registry publication, OEX save/approval, Pages deployment or external message ran in this finish. Later documentation commits preserve this code snapshot; they are not additional native runs.

| Executed check | Actual result and scope | Receipt / output |
| --- | --- | --- |
| Hosted main rerun | Passed; real steps executed at `a10de3f`, not a billing-lock annotation | [Run metadata](evidence/voting-finish-nov10/ci-restored.json), [main run](https://github.com/himanshu748/silentshift/actions/runs/42569241885) |
| Hosted backend candidate | Passed at `7b3d5ef`; **393 pytest in 23.17s**, types/build, **54 browser checks in 1.1m** | [CI metadata](evidence/voting-finish-nov10/candidate-031-ci.json), [complete output](evidence/voting-finish-nov10/candidate-031-ci-output.txt), [run](https://github.com/himanshu748/silentshift/actions/runs/42818397027) |
| Fresh GitHub source load, native suite, explicit startup | **0.3.1**, **7 classes / 22 methods**, build **154U ARM64**, no application source mounts; **68.371s** for this load/suite/first-replay driver | [Candidate summary](evidence/voting-finish-nov10/candidate-031-summary.json), [load receipt](evidence/voting-finish-nov10/candidate-031-load.json), [native assertions](evidence/voting-finish-nov10/candidate-031-native-tests.txt) |
| Two recorded API replays in that candidate | **12/12 twice**, sessions **24 / 58**, quarantined with no deliveries and no LLM inference | [First](evidence/voting-finish-nov10/candidate-031-replay-1.json), [repeat](evidence/voting-finish-nov10/candidate-031-replay-2.json) |
| Exported archive installed in a second fresh container | Passed actual local-filesystem repository install; **80.522s**, pristine namespace and empty application checked. Production intentionally remains stopped there. Not public-registry installation or a second API run. | [Archive inspection](evidence/voting-finish-nov10/candidate-031-archive.json), [clean install](evidence/voting-finish-nov10/candidate-031-install.json), [command](evidence/voting-finish-nov10/candidate-031-install-command.txt), [output](evidence/voting-finish-nov10/candidate-031-install-output.txt) |
| Fresh source live Scenario Lab run | **5/5 final routes**, local Qwen and local embeddings, at `da2e9e9`; **3/5 raw proposals** matched the labels. This is five synthetic scenarios, not general accuracy. | [Live receipt](evidence/voting-finish-nov10/fresh-live-five.json), [native load](evidence/voting-finish-nov10/fresh-native.json), [output](evidence/voting-finish-nov10/fresh-live-five-output.txt) |
| Fresh-clone connected browser reads | **16/16 in 46.6s**, desktop and mobile, at client `daead01` against that real native case set | [Receipt](evidence/voting-finish-nov10/connected-final.json), [full output](evidence/voting-finish-nov10/connected-final-output.txt) |
| Fresh GitHub source Compose command | Native production + real workbench; **12/12**, session **2**, **35.451s**, at `2dc0e92`. Browser login loaded the actual case and labeled recorded mode. | [Receipt](evidence/voting-finish-nov10/compose-final.json), [replay](evidence/voting-finish-nov10/compose-replay.json), [startup](evidence/voting-finish-nov10/compose-up.txt) |
| Fresh candidate Python / web | **393 pytest in 31.29s**; `npm run check` and `npm run build` passed locally, with nonfatal dependency directives reported | [Python output](evidence/voting-finish-nov10/candidate-031-pytest.txt), [summary](evidence/voting-finish-nov10/candidate-031-summary.json); hosted web output linked above |
| Ruff | **40 remaining**, down from **83**; each file/line/rule has a reason. No blanket ignores, check deletion or clean-lint claim. | [Inventory](RUFF_REMAINING.md), [machine receipt](evidence/voting-finish-nov10/ruff-remaining.json) |
| Actual native reply bodies and Event Log | Delivered session **86**, quarantine session **30**, both compact bodies and routing INFO events captured; exact temporary permissions restored | [Capture receipt](evidence/voting-finish-nov10/native-ui.json), [restoration](evidence/voting-finish-nov10/permissions-restored.json) |

### How the missing connected cases were produced

The live verifier submitted the five synthetic cases through the authenticated **Scenario Lab API → Partner Service → Semantic Process → native AI Hub → policy → operations** path. It did not insert a delivered case, recommendation, vector result or Workflow task to satisfy the UI. The isolated driver separately administrator-indexed the installed synthetic approved-amendment catalog through native `IndexAmendments`; delivery's normal Precedents operation indexed the resolved case. [Catalog receipt](evidence/voting-finish-nov10/amendment-index.json) · [reproduction guide](CONNECTED_CHECKS.md).

Only `module.xml` differs among native package files between the live/connected native snapshot and the versioned candidate; executable classes, Python assets, fixture and replay bytes match. [Exact package identity](evidence/voting-finish-nov10/candidate-031-source-identity.json). Fresh candidate load/replays establish the new package identity separately. Protected pre-existing UI edits and unfinished sealed-benchmark results are outside these commits. The earlier CSV browser and approve/reject receipts retain their dated scope; they were not relabeled as new runs.

### Native body captures

- [Destination acknowledgment](assets/voting-finish-nov10/delivered-destination-body.jpg): case `C553F4BE-DCFF-11F1-994E-21106723194A`, header **110**, body **91**, `routing=DELIVERED`.
- [Quarantine acknowledgment](assets/voting-finish-nov10/held-quarantine-body.jpg): case `915AB958-DCFF-11F1-994E-21106723194A`, header **54**, body **43**, `routing=QUARANTINED`.
- [Delivered routing Event Log](assets/voting-finish-nov10/delivered-event-log.jpg), [held routing Event Log](assets/voting-finish-nov10/held-event-log.jpg).

Each acknowledgment's `BodyJSON` contains only `case_id`, `routing` and its operation-time `version`; empty recommendation/metadata properties carry no full case. Later Workflow/audit updates can increment the persisted case version. The complete case remains in the Partner response and API. These are native UI screenshots, not generated trace illustrations.

### Failures retained and corrected

The first hosted backend rerun really failed because a shallow clone lacked frozen baseline commit `d1d752c`. Full-history checkout fixed access to that baseline without changing the assertion. [Failure](evidence/voting-finish-nov10/ci-backend-initial-failure.txt). The first fresh connected run then found the stale exact prompt assertion `1.3.1`; source/runtime already used `1.4.2`. [Failure](evidence/voting-finish-nov10/connected-initial-failure.txt). The exact assertion was updated, not relaxed.

Concurrent native instances exhausted the existing **2 GiB** VM: connected reads lost transport, and the first Compose startup received signal 9. Completed test instances were stopped without deleting data; the affected native instance was restarted and the unchanged full connected suite passed serially. [Interrupted output](evidence/voting-finish-nov10/connected-after-prompt-fix-oom.txt). A serial Compose attempt then found a real read-only `node_modules` mount failure. The launcher now uses a dedicated writable frontend volume and refuses another running build-154 instance. [Both failures](evidence/voting-finish-nov10/compose-failures.json).

Native Contents initially crashed the in-app browser. After native memory recovery and a new sign-in, both compact XML bodies were captured successfully; the informational XSLT deprecation banner was dismissed, no browser security warning bypassed. Both read-permission windows were closed. The candidate's first preflight rejected an already reserved subnet before creating a container; the next invocation selected a disjoint subnet from Docker's actual IPAM snapshot. [Preflight](evidence/voting-finish-nov10/candidate-031-preflight.txt), [executed candidate command](evidence/voting-finish-nov10/candidate-031-command.txt). None of these paths was silently replaced by fixture injection.

---


## Current local branch repeat

**Historical earlier November 10 checkpoint.** The fresh GitHub repeat above supersedes its incomplete connected/capture gates; the original outputs below remain unchanged.

A fresh **local Git clone** of `backend-polish-nov10` at **`76d9ef17f660d3d9ca9aa428257563055111fb51`** loaded source into an isolated, already-licensed **2026.3.0AI.154.0 Community / 154U ARM64** container with **no application source mounts**. It was not a GitHub clone of an unpushed branch. Initial activation failed when Docker default network pools were exhausted; the still-empty installed instance was then activated on an inspected disjoint private /28. No networks were deleted. [Receipt](evidence/backend-polish-nov10/fresh-source.json), [executed resume driver](evidence/backend-polish-nov10/fresh-source-commands.py). Subsequent harness/docs commits preserve the native executable tree: [identity](evidence/backend-polish-nov10/source-identity.json).

| Check | Result from this pass | Evidence |
| --- | --- | --- |
| Source load / production / native suite | Passed; **7 classes / 22 methods** | [Native output](evidence/backend-polish-nov10/fresh-source-native.txt) |
| Recorded API replays | **12/12 twice**, sessions **24 / 58**, held with no deliveries | [First](evidence/backend-polish-nov10/fresh-source-replay-1.json), [second](evidence/backend-polish-nov10/fresh-source-replay-2.json) |
| Fresh source Python | **339 passed in 41.99s** | [Output](evidence/backend-polish-nov10/fresh-source-pytest.txt) |
| TypeScript / production build | Passed | [Types](evidence/backend-polish-nov10/fresh-source-types.txt), [build](evidence/backend-polish-nov10/fresh-source-build.txt) |
| Disconnected/responsive browser suite | **54 passed (2.3m)** | [Output](evidence/backend-polish-nov10/fresh-source-browser.txt) |
| Connected read-only browser suite | **12 passed / 4 failed (44.7s)**; delivered-amendment and retrieved-precedent cases absent in this clean replay instance | [Receipt](evidence/backend-polish-nov10/fresh-connected.json), [full failure output](evidence/backend-polish-nov10/fresh-connected-output.txt) |
| Revised install/network harness | **373 pytest passed in 36.54s** | [Output](evidence/backend-polish-nov10/10-harness-pytest.txt) |
| Fresh local clone of revised shell launcher | Public native **0.3.0** installed; release-matched **5 classes / 12 methods**, both replays **12/12** | [Summary](evidence/backend-polish-nov10/public-shell-summary.json), [command](evidence/backend-polish-nov10/public-shell-command.sh), [output](evidence/backend-polish-nov10/public-shell-output.txt) |
| Native UI readback | Held case, compact References reply, recorded provider metadata and Event Log entries captured | [Capture receipt](evidence/backend-polish-nov10/11-native-ui.json), [permissions restored](evidence/backend-polish-nov10/11-permissions-restored.json) |

**Incomplete acceptance:** no delivered-case Visual Trace/Event Log capture was produced in this fresh instance. The additional review verifier stopped after two environment-preparation errors, before creating cases ([blocked receipt](evidence/backend-polish-nov10/fresh-review-blocked.json)). Earlier same-instance upgrade review passed **26/26 per case**, including one receipt under concurrent approval ([receipt](evidence/backend-polish-nov10/upgrade-review.json)); it is not relabeled as fresh-instance verification. The earlier metadata exporter failed twice and remains [failed evidence](evidence/backend-polish-nov10/08-production-routes.json). Primary native UI readback subsequently proved the held References reply separately.

No fresh model inference or renewed live-five-case/CSV-browser result is claimed by these replay checks. Protected pre-existing uncommitted UI work is outside the fresh-clone snapshot. The shell launcher uses Docker orchestration, **not Compose**; the normal live installation still uses Compose. Public IPM/OEX remain **0.3.0**, React **0.2.1**. **At that earlier checkpoint, 0.3.1 was not prepared** while required readback/connected-data gates remained incomplete. No package/tag/release/push/OEX action occurred.

# Judge verification

## One-command public-package launcher — November 10, 2026 (IST)

The new local `push/top3` launcher, `uv run python scripts/judge_replay.py`, passed a separate clean-container run. It pins verification source to the public 0.3.0 snapshot `a7aa217f1fc8d96f56bac6fd3110618eec21c353`, fetches the checksum-pinned IPM installer, generates private test credentials and never changes the app's `.env`. Current source native tests are deliberately not copied into the older published backend.

Result: public 0.3.0 install/startup, **5 native classes / 12 methods**, two **12/12** recorded replays, sessions **24 / 58**, quarantine and zero deliveries. [Launcher receipt](evidence/voting-week-nov10/judge-wrapper.json) · [exact output and duration](evidence/voting-week-nov10/judge-wrapper-output.txt) · [native assertions](evidence/voting-week-nov10/judge-wrapper-native-tests.txt). This is a local launcher plus fresh pinned-source checkout and isolated registry install, not a fresh GitHub clone of the unpushed final branch or a test of its unpublished runtime changes. No model inference or IRIS image download occurred.

The current local Python suite passed **330 tests in 22.60s**; the launcher-specific tests passed **12 in 0.42s**. TypeScript and the frontend build passed, with existing non-fatal bundler warnings. [Local checks and environment-example coverage](evidence/voting-week-nov10/judge-polish-checks.json). Pre-existing uncommitted UI edits remain separate from this documentation/harness change; these checks are not a new connected-browser or live five-case run.

## Voting-week public main repeat — November 10, 2026 (IST)

A fresh GitHub clone of **main `a10de3f61e1d809b374832a4db67761318bc16ea`** repeated the documented public-package path in a new isolated **2026.3.0AI.154.0 Community / 154U ARM64** container, with no application source mounts. The official runtime and gateway images were already loaded; no new IRIS image or model was downloaded. Private local test credentials were configured without provider keys. This is a **public 0.3.0 install**, not a source upgrade or verification of unpublished `push/top3` runtime changes.

| Executed check | Observed result | Evidence |
| --- | --- | --- |
| Literal public `zpm "install silentshift"`, version check and explicit production start | Native 0.3.0, passed | [Receipt](evidence/voting-week-nov10/judge-main-nov10.json) |
| Full release-matched native suite | **5 classes / 12 methods; All PASSED** | [Complete assertion output](evidence/voting-week-nov10/judge-main-native-tests.txt) |
| First no-key API replay | **12/12**, session **24**, QUARANTINED, **0 deliveries** | [First replay](evidence/voting-week-nov10/judge-main-first-replay.json) |
| Repeat no-key API replay | **12/12**, session **58**, QUARANTINED, **0 deliveries** | [Repeat replay](evidence/voting-week-nov10/judge-main-second-replay.json) |
| Fresh main Python suite | **207 passed in 11.40s** | [Commands and output](evidence/voting-week-nov10/judge-main-commands.txt) |

No fresh inference, embeddings, live five-case scenario run or browser regression suite ran in this repeat. Those earlier receipts retain their original scope. The new test containers are retained stopped; starting them again is needed to inspect their printed local trace URLs. No existing app container or benchmark data was changed. Whole-install wall time was not captured, so no total elapsed claim is made.

Historical sections below remain unchanged. A source-branch harness must not copy newer native tests into this older published package; the separate one-command wrapper pins release-matched verification source.


## November 9: final `push/top3` source checkpoint

The [final checkpoint](evidence/top3-final-checkpoint.json) records **286 Python tests passing in 18.88 seconds** and the normal local production healthy. All **59 native package source files** remain byte-identical to the fresh quality-gate snapshot; [footprint](evidence/top3-final-source.json). The [fresh native replay/live gate](evidence/top3-quality.json) and [multi-page/browser/CSV gate](evidence/top3-multipage.json) retain their recorded scope. The new demo gateway has [two local native cases and printable-trace evidence](evidence/top3-demo-local.json); this does not establish public hosting.

The AWS trial stopped before native installation after transfer failure, and its resources were removed; [closure readback](evidence/top3-aws-trial-result.json). Online demo remains **Not claimed**. Main, native IPM 0.3.0, the listing and video were not changed by this branch. The prepared host installer is not end-to-end cloud-qualified. Historical verification sections below are preserved.


## Voting-week source branch repeat — November 9, 2026 UTC

This pass verifies executable source **`718ec9f65317655379c0194d326f755dccc44a64` on `push/top3`**, not a new main/public-package release. Two newly created official **2026.3.0AI.154.0 Community / 154U ARM64** containers used source loading with **zero application source mounts**. They ran sequentially after the benchmark finished and the normal app was temporarily stopped. This is a fresh-container source gate, not a fresh GitHub-clone installation or a public registry install. No new image was downloaded.

| Check | Observed result | Receipt/output |
| --- | --- | --- |
| Full Python suite after the earlier timing-harness repair | **248 passed in 21.49 seconds** | [Exact output](evidence/top3-quality-pytest.txt) |
| Keyless source install and production startup | Passed | [Source identity and commands](evidence/top3-quality.json) |
| Full native suite, replay instance | **5 classes / 12 methods passed** | [Native assertions](evidence/top3-quality-replay-unit.txt) |
| Two keyless API replays | **12/12 each**, sessions **24 / 58**, quarantined with zero deliveries | [First](evidence/top3-quality-replay-first.json), [second](evidence/top3-quality-replay-second.json) |
| Separate fresh live source instance | Native suite **5 classes / 12 methods**, live scenarios **5/5** | [Native unit output](evidence/top3-quality-live-unit.txt), [actual scenarios](evidence/top3-quality-live-five.json) |
| Frontend connected to that fresh live backend | **16 passed in 16.6 seconds**, no request mocks | [Browser output](evidence/top3-quality-fresh-native-browser.txt) |

Live sessions: **30, 58, 86, 113, 141** in the separate live container. Session numbers belong to their own containers and are not interchangeable. New source gates close the previous default-provider replay/live and full-Python follow-ups; earlier failed attempts remain preserved. External provider services are still unverified. Both test instances were retained stopped, and the normal local app was restored. Subsequent README/design/evidence edits do not change the verified executable snapshot. [Detailed scope and source hashes](evidence/top3-quality.json).

The published-package and main-branch histories below retain their original dates, commits and test scope.

## Public 0.3.0 install — November 8, 2026 (UTC)

**PASSED: fresh public-registry install, not a source upgrade.** A new GitHub clone at **`a7aa217f1fc8d96f56bac6fd3110618eec21c353`** installed the public native package with literal **`zpm "install silentshift"`** in a new **2026.3.0AI.154.0 Community / 154U ARM64** container. Actual installed version: **0.3.0**; application source mounts: **0**. No provider key, new image download or fresh inference was used. [Registry receipt](evidence/ship-030-registry.json) · [pristine state](evidence/ship-030-pristine.txt) · [mounts](evidence/ship-030-mounts.txt).

| Executed check | Result | Receipt |
| --- | --- | --- |
| Public IPM install and explicit production startup | Passed, native **0.3.0**; command **75.801s** including tests and first replay | [Install](evidence/ship-030-install.txt), [version](evidence/ship-030-version.txt), [driver output](evidence/ship-030-registry-install-output.txt) |
| Full native suite | **5 classes / 12 methods; All PASSED** | [Full output](evidence/ship-030-native-tests.txt) |
| First recorded replay | **12/12**, session **24**, QUARANTINED, **0 deliveries** | [Output](evidence/ship-030-first-replay.txt), [metadata](evidence/ship-030-registry.json) |
| Repeated recorded replay | **12/12**, session **58**, QUARANTINED, **0 deliveries**; command **1.051s** | [Output](evidence/ship-030-registry-repeat-output.txt), [metadata](evidence/ship-030-repeat.json) |
| Installed CSV preview API | HTTP **200**, **2** synthetic lines; **21** rows rejected with HTTP **422** | [Receipt](evidence/ship-030-public-csv-preview.json) |
| Public source archive | **474** tracked files match clone `a7aa217`; all **45 classes / 11 assets** and manifest match | [Full source comparison](evidence/ship-030-source-archive.json), [native boundary](evidence/ship-030-public-artifact.json) |

Exact executed blocks, from the privately configured fresh clone:

```sh
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest --version 0.3.0 --execution-mode recorded-replay --container silentshift-bonus-registry-public-030-nov8 --api-port 52943 --execute
uv run python scripts/trace_example.py --api http://127.0.0.1:52943/silentshift/api --context colima-silentshift --container silentshift-bonus-registry-public-030-nov8 --output <retained-checkout>/.local/ship-030/registry-repeat.json
```

The output placeholder above replaces a private local path; it is not shell syntax to paste literally. [Original sanitized install command](evidence/ship-030-registry-install-command.sh) · [repeat command](evidence/ship-030-registry-repeat-command.sh). Each replay records five provider request/response pairs and four executed native evidence tools. No upstream token usage or cost is invented for replay. Visual Trace: `http://127.0.0.1:52943/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=58` (local permitted portal account required; test instance is retained stopped after capture).

The CSV preview probe initially expected HTTP 400 incorrectly; the API correctly returned its documented **422**. Only that private harness assertion changed. [Original failed assertion](evidence/ship-030-public-csv-preview-initial.json) · [corrected probe](evidence/ship-030-csv-probe.py). This preview check performed **no source import, case investigation or browser automation**. Full live **5/5**, review **54**, CSV browser **32**, Python **207**, TypeScript/build and browser **38 + 16** remain the separate candidate results below; they were not rerun or relabeled as public-install checks. [Executable-tree identity from candidate to public-gate clone](evidence/ship-030-source-identity.json).

The live signed-out OEX page shows release **0.3.0** and its archive link. The new description was submitted successfully but has not yet replaced its older public text. The dedicated idea section is still absent anonymously. [Publication and external gates](evidence/ship-030-publication.json). No Git tag, runtime/policy/agent change, questionnaire resubmission or duplicate bug filing occurred. Later evidence/index documentation commits preserve the tested executable snapshot; the hash names the verified clone, not the commit containing this paragraph. [Documentation-only closeout checks](evidence/ship-030-closeout.json) confirm the unchanged executable tree, retained stopped test instances, working app health and unchanged Not claimed rows.

## Final release-candidate source freeze, November 8, 2026 (UTC)

**Historical pre-publication gate: PASSED for native IPM 0.3.0 candidate.** At that checkpoint it was prepared but not published; the later public-install gate above records publication independently. The fresh GitHub checkout is **`c71acdf94f2214316ff510696a2909724c31c416`**. Its runtime, manifest, fixtures, release harness and tests are byte-identical in Git to **`63ec7d901e85d415ed831c866983ca0e4046a937`**, against which the commands below executed. [Final source-identity receipt](evidence/candidate-030-final-snapshot.json) · [complete candidate receipt](evidence/candidate-030.json). Later evidence/index documentation commits preserve that exact executable tree; they do not assert another native run. The checkout hash is a reproducible verification checkpoint, not a self-referential claim about the commit containing this paragraph.

The already loaded official **2026.3.0AI.154.0 Community / 154U ARM64** image was used in two new isolated containers with **no application source mounts**. Both used real IPM **`load` of candidate 0.3.0**, explicit production setup and generated native archives. This is source/package-candidate verification, **not a public registry 0.3.0 installation**. At this historical candidate checkpoint, public native IPM was last independently observed at **0.2.0** and OEX/workbench was **0.2.1**.

| Executed check | Observed result | Commands / receipts |
| --- | --- | --- |
| Fresh source load, production startup and archive | Passed; installed **0.3.0**, **45 classes**; archive boundary passed | [Command](evidence/candidate-030-source-live-command.sh), [output](evidence/candidate-030-source-live-output.txt), [load](evidence/candidate-030-load.txt), [archive](evidence/candidate-030-archive.json) |
| Full native suite | **5 classes / 12 methods passed** in live and replay instances | [Live output](evidence/candidate-030-native-tests.txt), [replay output](evidence/candidate-030-resume-unit-output.txt) |
| Fresh local-model scenarios | **5/5 final routes passed** | [Native receipt](evidence/candidate-030-native.json) |
| Approve/reject/concurrent review | **54 assertions passed** | [Review receipt](evidence/candidate-030-review-ready.json), [command](evidence/candidate-030-review-ready-command.sh) |
| CSV workbench import | **32 browser checks passed** | [Receipt](evidence/candidate-030-csv-verification.json), [command](evidence/candidate-030-csv-ready-command.sh), [first import](evidence/candidate-030-csv-first-results.json), [repeat](evidence/candidate-030-csv-repeat-results.json) |
| Two recorded API replays | **12/12 each**, sessions **46** and **80**, each held with **0 deliveries** | [First](evidence/candidate-030-resume-replay-first.json), [second](evidence/candidate-030-resume-replay-second.json), [resume commands/state](evidence/candidate-030-replay-resume.json) |
| Python | **207 passed in 55.73s** | [Command](evidence/candidate-030-pytest-command.sh), [output](evidence/candidate-030-pytest-output.txt) |
| TypeScript and production build | Both passed | [Types](evidence/candidate-030-types-repaired-output.txt), [build](evidence/candidate-030-build-output.txt) |
| Disconnected / connected browser suites | **38 / 16 passed** | [Disconnected output](evidence/candidate-030-browser-output.txt), [connected output](evidence/candidate-030-connected-output.txt) |

The live driver also ran one separately recorded SDK warmup and one approved-amendment embedding, excluded from the five-case score. The live source-load command took **446.645s**, CSV checks **128.534s**, and connected checks **61.296s**. These are measured command durations on this Mac, not performance promises. Live scenario sessions were **30, 58, 86, 113, 141**. CSV sessions **218 / 246** ended **QUARANTINED / DELIVERED**, with **0 / 1 simulator receipts**. All four native evidence tools were observed for both CSV cases. Raw recommendations matched **4/5** labels while final routes matched **5/5**; no general model-quality or productivity improvement is claimed.

### Preserved failures and setup repairs

The recorded-replay container loaded candidate source and started production, then paused before gateway creation because macOS free space fell below the unchanged storage floor. After authorized cache cleanup, its identity and original creation/image/network receipts were checked and the **same new container** was completed, without another source installation or state reset. Its resumed suite first exposed a missing **test-only inbox directory**; supplying the same prerequisite as the normal driver made the full suite pass. [Original stop](evidence/candidate-030-replay-load-output.txt), [initial failed unit output](evidence/candidate-030-resume-unit-initial-failure-output.txt), [successful resume](evidence/candidate-030-replay-resume.json), [exact resume helper](evidence/candidate-030-resume_replay.py). No runtime class, policy or agent behavior changed to obtain a pass.

Other harness setup failures remain recorded: copied npm launcher symlinks were restored before TypeScript/build/browser success; review inspection test files were copied to the verifier's expected path; the workbench proxy was restarted with its required `/silentshift` path before CSV success. The [aggregate receipt](evidence/candidate-030.json) links the failed attempts as well as the successful results. No earlier failing receipt was relabeled as passing.

Node dependencies were reused by hardlink after exact lockfile comparison, with launcher symlinks then restored; this was **not a fresh npm dependency installation**. uv used its local cache. Browser binaries were available for the actual tests, then the idle headless download cache was removed for disk recovery. Before a future browser run, run `npm --prefix web exec -- playwright install chromium` again. Public logs replace local paths with `<fresh-clone>` or `<retained-checkout>` and strip trailing whitespace; private originals remain retained.

Synthetic examples, per-line simulator delivery, no hosted demo and unverified real-partner/ERP/X12 integration remain explicit limits. Native IPM packages the backend; the React UI runs separately from matching source. No paid provider, new IRIS image, public package, Git release tag, OEX edit, questionnaire submission, bug filing or hosted-CI setting change occurred. Bonus statuses and organizer qualification remain unchanged. [Owner publication and post-publication install commands](IPM.md#owner-only-030-publication-runbook).


## Historical Linux-only candidate preparation, November 8, 2026 (UTC)

**Historical sandbox-only status:** at that earlier Linux check, the full 0.3.0 clean-IRIS acceptance gate was not complete. The later local gate above supersedes that blocker; this historical evidence is retained with its original scope. The **integrated source/documentation release freeze** was checked from a clean Linux clone at [`b6bfdd099d9273fa4134ce34bfbc7269c52f8f6b`](https://github.com/himanshu748/silentshift/commit/b6bfdd099d9273fa4134ce34bfbc7269c52f8f6b), based on the pre-existing mainline 0.3.0 preparation [`63ec7d9`](https://github.com/himanshu748/silentshift/commit/63ec7d901e85d415ed831c866983ca0e4046a937). The integrated gate passed **207 pytest (2.90s), 58-file/45-native-class/11-asset staging, TypeScript/build, 408 local Markdown paths, and an exact staged `docs/IPM.md` comparison**. [Latest dated integrated receipt](evidence/ipm-030-integrated-freeze-nov8.json) · [commands](evidence/ipm-030-integrated-freeze-nov8-commands.sh) · [observed output](evidence/ipm-030-integrated-freeze-nov8-output.txt). Earlier preliminary source checks at [`5e5c8a6`](evidence/ipm-030-candidate-linux-nov8.json) and [`915878fc`](evidence/ipm-030-freeze-nov8.json) were from a **parallel preparation branch with different release-harness code** and are historical, **not** the final integrated candidate. Native application semantics are inherited from the earlier successful [fresh-source clone `35d29e0`](evidence/source-isolated-nov8.json) and the later [same-instance bootstrap fix `e61a961` pass](evidence/final-pass-nov8.json); those tests are separate historical runs.

| 0.3.0 candidate check | Observed result | Scope |
| --- | --- | --- |
| Clean Linux source clone and release staging | **Passed**, manifest `0.3.0`; 58 staged allowlisted files (45 native classes and 11 assets); no registry push | Source-staging check only, **not** a generated/installed IRIS native archive |
| `uv run pytest -q` | **207 passed in 2.90s** in the final integrated candidate | Clean Linux clone at `b6bfdd0`, preserving mainline version-aware packaging and its regression assertions |
| `npm --prefix web run check` / `npm --prefix web run build` | **Both passed** | TypeScript/frontend only; nonfatal existing Lucide bundler warnings |
| `npx playwright install chromium` | **Blocked**, `EAI_AGAIN cdn.playwright.dev` | Browser binaries unavailable; **38 disconnected, 16 connected and 32 CSV UI checks not rerun** |
| Fresh isolated IRIS 2026.3.0AI.154.0 container, no application mounts | **Not run** | Temporary Linux sandbox lacks Docker, licensed IRIS 154U image and local Ollama |
| Native 5 classes / 12 methods, 5/5 live routes, both replays, 54 review assertions and CSV native import | **Not rerun** | Earlier successful 154U receipts below **must not** be relabeled as a new 0.3.0 fresh-source gate |

**Source identity and docs-only freeze discipline:** **`b6bfdd099d9273fa4134ce34bfbc7269c52f8f6b`** is the final *integrated* source/package-document snapshot, preserving mainline release-harness updates from `63ec7d9`. Its checked `module.xml` declares **0.3.0**, and the final packaged `docs/IPM.md` bytes were hash-checked in [the integrated freeze receipt](evidence/ipm-030-integrated-freeze-nov8.json). Subsequent evidence/index docs commits do not alter staged package files. Get the current post-merge `main` SHA using `git rev-parse main` and examine `git diff a37fc8729ec216d7a403190ffe6f13830122e6aa..main --name-only`: no runtime `src/`, `python/`, `web/` or `fixtures/` changes were permitted in this release-preparation work. Only the native manifest version, packaging/verification harness and tests were changed outside docs. Later documentation-only Git commits cannot be treated as fresh native runs or public package installations.

**External release state (as last independently observed):** public native IPM **0.2.0**, current manifest **0.3.0 prepared/unpublished**, OEX/frontend **0.2.1**. The last verified public 0.2.0 install omits CSV; native 0.3.0 stages its new CSV backend/parser, **not the separately built web frontend**. After the owner publishes 0.3.0 through OEX, only a new anonymous registry version check and a fresh public `zpm "install silentshift"` can support the claim that **0.3.0 is live**. [Before/after publication ledger](SUBMISSION_CHECKLIST.md#published-vs-main) · [Owner-only exact commands](IPM.md#owner-only-030-publication-runbook) · [Release notes](../CHANGELOG.md). No OEX edit, package registry publish, Git release tag, hosted demo, billing change, or bonus status change occurred in this candidate-preparation pass. At that earlier sandbox-only checkpoint, fresh-native acceptance was blocked by its unavailable licensed environment; the later local candidate pass above closes that gate.


## Final source pass — November 8, 2026 (UTC)

**All executed local checks passed after the source-installer repair at `e61a961228cdf3d0f4ebc3a274b46ad1894a43b1`.** Normal bootstrap now uses `LoadDir` with compilation enabled for the checked-in source directory. It no longer compiles unrelated diagnostic classes already present in the namespace. In the same instance where the earlier reload failed, the documented bootstrap completed and `SilentShift.Repro.UnderscoreTool` remained present. [Before/after receipt](evidence/bootstrap-scope-fix-nov8.json) · [bootstrap output](evidence/bootstrap-scope-fix-nov8.txt).

This was a **same-instance source upgrade/regression test on 154U ARM64**, not another clean-container or registry install. Application classes, policy, Python, UI and scenario fixtures are unchanged from the earlier fresh source snapshot. The installation harness is the only code change. The earlier clean source/package gates below retain their original scope; the public package was separately downloaded and found byte-identical to its verified archive. [Artifact receipt](evidence/final-pass-nov8-ipm-artifact.json). No image was downloaded, release tagged, package published, OEX edit saved or message posted.

| Executed check | Actual result | Receipt / output |
| --- | --- | --- |
| Normal source bootstrap with the retained diagnostic class | Passed in **6.396s**, without deleting it | [Bootstrap regression](evidence/bootstrap-scope-fix-nov8.json) |
| Full native unit suite | **5 classes / 12 methods passed** | [Native unit output](evidence/final-pass-nov8-unit-output.txt), [executed ObjectScript](evidence/final-pass-nov8-unit-command.cos) |
| Fresh five-case local inference | **5/5 final routes passed** | [Complete receipt](evidence/final-pass-nov8.json), [command](evidence/final-pass-nov8-native-command.sh), [output](evidence/final-pass-nov8-native-output.txt) |
| Approve, reject and concurrent identical approval | **54 assertions passed** | [Review receipt](evidence/final-pass-nov8-review.json), [output](evidence/final-pass-nov8-review-output.txt) |
| Live custom file adapter | Passed with **2 new model cases**, acknowledgement recovery, duplicates and invalid/symlink input checks | [Adapter receipt](evidence/final-pass-nov8-adapter.json) |
| CSV import through the workbench | **32 checks passed** | [CSV observations](evidence/final-pass-nov8.json), [first import](evidence/final-pass-nov8-csv-first.json), [repeat](evidence/final-pass-nov8-csv-repeat.json) |
| Current provider trace metadata and vector evidence | Both read-only inspectors passed for held and delivered cases | [Provider pairs](evidence/final-pass-nov8-provider.json), [native precedents](evidence/final-pass-nov8-precedents.json) |
| Python | **207 passed in 3.89s** | [Output](evidence/final-pass-nov8-pytest-output.txt) |
| TypeScript / production build | Both passed | [Types](evidence/final-pass-nov8-types-output.txt), [build](evidence/final-pass-nov8-build-output.txt) |
| Landing/disconnected browser / connected browser | **38 / 16 passed** | [Disconnected output](evidence/final-pass-nov8-browser-output.txt), [connected output](evidence/final-pass-nov8-connected-output.txt) |

The live native run took **314.465s**; CSV verification took **113.274s**. These are command durations from this Mac, not throughput promises. Raw model recommendations matched **4/5** frozen labels while final routing matched **5/5**. The deterministic baseline also solves the fixed examples; no AI accuracy improvement or generalization result is claimed.

Core native sessions: **2957, 2985, 3013, 3040, 3068**. CSV sessions: **3198, 3226**; the critical line stayed held with **0 deliveries**, and the matching line had **1 simulator receipt**. CSV checks include bounded rejection, required source approval, retained originals, interrupted-request recovery, repeat import without redispatch, mobile, keyboard and reduced motion. No aggregate adapter assertion count is inferred from nested metadata.

A new anonymous browser context returned **200** for OEX, the contest page and both articles. SilentShift remained listed; both articles linked OEX; the listing showed its moderator Works result, video and idea description link. The dedicated idea section was still absent. [Live public readback](evidence/final-pass-nov8-public.json). The downloadable MP4 matched its local file. [Download receipt](evidence/final-pass-nov8-video.json).

**External gates remain:** GitHub's job did not start because the account is locked for billing; [exact annotation](evidence/final-pass-nov8-hosted-ci.json). AI Hub issue #17 remains open with no replies or labels; [readback](evidence/final-pass-nov8-issue.json). Vendor/organizer qualification and the dedicated idea association remain unconfirmed. No hosted CI pass or awarded bonus is claimed. At the moment of this earlier local run, the prepared OEX copy and organizer video note were not yet sent. **Later on November 8**, the OEX description update was approved and the video link sent to the team, as independently recorded in [the OEX owner receipt](evidence/oex-update-nov8.json). No award or idea qualification is inferred.

At the time of this **historical** native run, public native IPM was **0.2.0** and app/OEX was **0.2.1**. CSV and the installer fix were source-only. Subsequent preparation set the source manifest to **unpublished 0.3.0**, without changing the public registry. Synthetic inputs, per-line simulator effects, the absence of a hosted demo and unverified real-partner/ERP integration remain explicit limits. Historical failed attempts below were preserved; the retained-instance reload failure is now resolved by the installer repair above.

## Current-main repeat — isolated source, November 8, 2026 (UTC)

**The then-open fresh-source verification gap was closed for this earlier source snapshot, not for the later 0.3.0 package candidate.** A fresh GitHub clone at **`35d29e0913ea27f4c56dfed214a402418984e5f0`** was loaded into a new **2026.3.0AI.154.0 Community / 154U ARM64** container, using the already loaded official image. The namespace was pristine and the application container had no source mounts. The tracked clone remained clean. The follow-up interval through `7d2cb7e` changed documentation/evidence only. The later source-installer repair is verified separately above.

This run used **IPM `load` of current source**, including the CSV class and parser. It is separate from the earlier successful public `zpm "install silentshift"` gate below. **At this earlier verified snapshot**, the source manifest still declared 0.2.0 and no new native package was published. At the **later release-preparation freeze**, the manifest declares **0.3.0 prepared/unpublished**, while public IPM was last verified as **0.2.0** and app/workbench as **0.2.1**. No provider key, paid service or new IRIS download was used.

| Check | Observed result | Evidence |
| --- | --- | --- |
| Fresh source load and production startup | Passed; **45 declared classes** | [Exact command](evidence/source-isolated-nov8-command.sh), [output](evidence/source-isolated-nov8-output.txt), [load transcript](evidence/source-isolated-nov8-load.txt) |
| Full native `%UnitTest` | **5 classes / 12 methods passed** | [Complete output](evidence/source-isolated-nov8-native-tests.txt) |
| Fresh live native scenarios | **5/5 final routes passed**; all agents returned with all four evidence tools | [Source, provenance and complete native receipt](evidence/source-isolated-nov8.json) |
| Fresh CSV workbench import | **32 browser checks passed**, with new held and delivered cases | [CSV receipt](evidence/csv-isolated-nov8.json), [exact command](evidence/csv-isolated-nov8-command.sh), [output](evidence/csv-isolated-nov8-output.txt) |
| Fresh-clone Python | **207 passed in 11.30s** | [Output](evidence/source-isolated-nov8-pytest.txt) |
| TypeScript and production build | Both passed | [Types](evidence/source-isolated-nov8-types.txt), [build](evidence/source-isolated-nov8-build.txt) |
| Landing/disconnected browser checks | **38 passed** | [Output](evidence/source-isolated-nov8-browser.txt) |
| Connected browser checks | **16 passed**, desktop and mobile; read-only native data | [Receipt](evidence/source-isolated-nov8-connected.json), [output](evidence/source-isolated-nov8-connected.txt) |

The complete source/native command took **359.323 seconds**, including installation, one separate local amendment embedding, an SDK diagnostic and the five-case run. CSV verification took **119.966 seconds**; connected checks took **55.396 seconds**. The [local-check receipt](evidence/source-isolated-nov8-local-checks.json) retains each command's measured wall time and exit code. All these commands exited successfully.

Final routing matched the frozen labels **5/5**; raw model recommendations matched **4/5**. The model proposed quarantine for conflicting references; policy correctly selected review. These synthetic cases establish integration behavior, not general model accuracy or an AI advantage over the deterministic baseline. The SDK diagnostic and amendment indexing are excluded from the five-case score.

Native scenario sessions were **30, 58, 86, 113, 141**. The CSV mismatch was **QUARANTINED**, session **169**, with **0 deliveries**; its matching line was **DELIVERED**, session **197**, with **1 simulator receipt**. Both CSV agents returned and read every tool. The UI checks also exercised bounded file rejection, native invalid-quantity rejection, explicit source approval, viewer restrictions, interrupted-request recovery, repeat import without new dispatch, case navigation, keyboard input, compact layouts and reduced motion. [First import](evidence/csv-isolated-nov8-first.json) · [repeat receipt](evidence/csv-isolated-nov8-repeat.json) · [desktop capture](assets/csv-isolated-nov8-desktop.png) · [mobile capture](assets/csv-isolated-nov8-mobile.png).

The earlier reload failure below is retained unchanged. It was bypassed by testing in a new instance without the untracked diagnostic class; that class was not deleted, and native code/policy/AI behavior were not changed. The only harness change allows an explicitly local API port, with [remote endpoints rejected before credential use](evidence/csv-isolated-nov8-guard.json).

**Hosted CI is blocked separately:** GitHub reports that the job did not start because the account is locked for billing. [Exact annotation](evidence/hosted-ci-nov8.json). The passing checks above are local; no hosted CI pass or billing repair is claimed.

The isolated test containers are retained for inspection. Restart only this pair to inspect these sessions:

```sh
docker --context colima-silentshift start silentshift-bonus-load-main-nov8
docker --context colima-silentshift start silentshift-bonus-load-main-nov8-gateway
```

Its API and trace portal use port **52913**. Opening message bodies requires a permitted account in that instance. CSV remains additive to the README's keyless replay and the JSON-ready-file adapter walkthrough. All inputs remain synthetic; delivery remains the IRIS simulator. No newer build, hosted demo, external ERP integration, package publication or bonus award is claimed.

## Earlier current-main repeat — November 8, 2026 (UTC)

**Public-package gate: passed. Current-main CSV repeat: stopped at failed source-reload preparation.** These are separate results; the released native package does not contain the source-only CSV feature.

The fresh GitHub clone's HEAD was **`df591420c06ed081623f6178804359ceb1686964`**. It includes the CSV runtime changes and the UI finish. The tracked clone stayed clean. Receipt-only follow-up commits through `e4a5573` added documentation and evidence. This hash identifies that executed snapshot; later harness changes are verified separately above.

Installation now lives in [INSTALL.md](../INSTALL.md#optional-check-without-a-model), linked from the README. The two historical README blocks were repeated with only a new container name and port. The already loaded official **2026.3.0AI.154.0 Community / 154U ARM64** image was used; no IRIS image was downloaded and no provider key was supplied.

| Executed check | Observed result | Elapsed |
| --- | --- | ---: |
| Fresh clone, literal `zpm "install silentshift"`, production startup and full native suite | Public native **0.2.0**; **5 classes / 12 methods passed**; initial replay **12/12** | 119.348 s for the complete first block |
| Second API replay | **12/12 passed** | 1.640 s |
| Fresh-clone `uv run pytest -q` | **207 passed in 14.21s** | 16.664 s wall time |

All blocks exited successfully. Replay sessions **24** and **58** each ended **QUARANTINED**, with **0 deliveries** and no fresh inference. [Machine-readable receipt](evidence/judge-current-nov8.json), [installation output](evidence/judge-current-nov8-install.txt), [complete native tests](evidence/judge-current-nov8-native-tests.txt) and [authenticated health](evidence/judge-current-nov8-health.json) preserve the observations.

Exact commands and outputs: [installation block](evidence/judge-current-nov8-command-1.sh) / [output](evidence/judge-current-nov8-command-1.txt), [repeat block](evidence/judge-current-nov8-command-2.sh) / [output](evidence/judge-current-nov8-command-2.txt), [Python block](evidence/judge-current-nov8-command-3.sh) / [output](evidence/judge-current-nov8-command-3.txt). Public logs replace the checkout path with `<fresh-clone>` and strip trailing whitespace. Private originals are retained. The fresh public-package containers were stopped and retained after testing.

### CSV and UI evidence; stopped repeat

Earlier in this same turn, before the fresh-clone gate, the refined CSV workbench completed **32 browser checks** against the retained local production. The synthetic mismatch was held and the matching line delivered once; invalid quantity input was rejected by the native server. [UI receipt](evidence/csv-ui-design-nov8.json), [successful import observations](evidence/csv-ui-nov8-success.json), [bounded-rejection observations](evidence/csv-ui-nov8-rejection.json). These observations are explicitly dated and ordered; they are not a post-gate CSV rerun.

After the fresh-clone gate, source/Python/fixture bytes were compared with that clone, then the documented source bootstrap was attempted in the retained local instance. It exited **1**: `CompilePackage("SilentShift")` also compiled the retained, untracked diagnostic class `SilentShift.Repro.UnderscoreTool`. Its generated `find_similar_precedents` invocation produced **3 compiler errors**, including `MPP5376`. This demonstrates a failed reload in that instance; it does not establish a defect in CSV import or a clean-source-install failure.

**Stopped without retry or native-code changes.** The post-gate CSV success/rejection checks and a fresh full live five-case run were not executed. The previously running production was restarted successfully after the failed reload. [Failure receipt and source hashes](evidence/csv-current-nov8.json), [executed command](evidence/csv-current-nov8-command.sh), [output](evidence/csv-current-nov8-bootstrap.txt), [compiler excerpt](evidence/csv-current-nov8-compiler.txt).

CSV is additive: it does not change the documented keyless replay walkthrough or the JSON-ready-file adapter path in [PARTNER_INBOX.md](PARTNER_INBOX.md). It requires the current source installation and explicit importer permission; public native IPM remains unchanged. No newer build, hosted demo, package publication or organizer award is claimed.

## Current-main repeat — November 5, 09:04–09:09 UTC

A second fresh GitHub clone, at **e8e1e60fded08d688c263bc9485fc7419c10f15b**, passed both README blocks with no provider keys. Only the unused container name (`silentshift-bonus-registry-main-nov5`) and port (`52893`) changed. The tracked clone remained clean. Within the historical `960b6b6` → `e8e1e60` interval, changes were documentation/evidence only. This statement does not cover the later CSV runtime and workbench changes.

**Public native IPM 0.2.0, production startup, all five native test classes / 12 methods, and both 12/12 replays passed on 2026.3.0AI.154.0 / 154U ARM64.** Fresh-clone `uv run pytest -q` returned **174 passed in 15.09s**. No fresh model/embedding call, five-case live rerun or newer build test is claimed.

[Machine-readable receipt and both native traces](evidence/judge-main-clean-clone.json) · [full native test output](evidence/judge-main-native-tests.txt) · [registry installation output](evidence/judge-main-install.txt).

The exact executed shell blocks are preserved as [block 1](evidence/judge-main-command-1.sh) and [block 2](evidence/judge-main-command-2.sh), with [first output](evidence/judge-main-command-1.txt) and [repeat output](evidence/judge-main-command-2.txt). Public logs replace the private checkout path with `<fresh-clone>` and strip trailing whitespace; original logs remain local. Both commands exited **0**. The repeated API journey printed:

```text
execution_mode=recorded-replay; fresh_inference=false
case_id=A56C930B-D8F8-11F1-9B50-2D0E2BB6B2AA; session_id=58
visual_trace_url=http://127.0.0.1:52893/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=58
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

The initial case was `A2778A37-D8F8-11F1-9B50-2D0E2BB6B2AA`, session **24**. These session numbers belong to this new isolated instance, not the earlier instance with the same numbers. Host/VM preflight free space was 7,706,902,528 / 4,274,151,424 bytes; the existing safety floors were unchanged. The new test containers were stopped and retained after verification; the working app was preserved. To inspect these particular traces, restart only this pair:

```sh
docker --context colima-silentshift start silentshift-bonus-registry-main-nov5
docker --context colima-silentshift start silentshift-bonus-registry-main-nov5-gateway
```

## Earlier clean-clone run — 960b6b6

**Verified on November 5, 2026:** a fresh GitHub clone followed both README command blocks without provider keys. The public registry installed native **0.2.0** on **2026.3.0AI.154.0 Community, ARM64 (154U)**. Production startup, the entire native `%UnitTest` suite and two API replays passed. This closes the earlier disk-space and checkout-location gate.

At this earlier snapshot, application/workbench was **0.2.1**. No runtime or feature code changed within that historical documentation interval, and no newer IRIS build was tested. Recorded replay performs no fresh inference; the separate five-case live result below remains dated evidence.

[Machine-readable receipt and native message metadata](evidence/judge-clean-clone.json) · [installation output](evidence/judge-clean-clone-install.txt) · [complete native test output](evidence/judge-clean-clone-native-tests.txt).

## Isolation and prerequisites

- Remote clone: `https://github.com/himanshu748/silentshift.git`, commit `960b6b6445f8b1f0ef7aaaa8c409e7d036b07170`. Its tracked tree remained clean before and after the run. The receipt records the README SHA-256.
- The clone was created beneath the existing Colima-shared directory, under the primary checkout's ignored `.local/judge-verified-20261105/`. No `.env`, source patch, `.local`, virtual environment or database was copied from another checkout.
- The process inherited only `HOME`, `PATH`, `TMPDIR` and locale variables. New local viewer/reviewer/gateway credentials were generated at mode `0600`; no LLM/provider API key was supplied. The checksum-verified public IPM installer was mode `0644`.
- Shared prerequisites: an already licensed, locally loaded official build-154 image, the local Web Gateway image and the existing `colima-silentshift` Docker context. This verifies a fresh source checkout and application container, not a new Mac or fresh EAP download.
- Native application container `silentshift-bonus-registry-judge-nov5` was new, had **no mounts**, and had no `SILENTSHIFT` namespace before installation. Only the separate gateway mounts generated configuration files. The preflight measured **6,822,494,208 host bytes** and **5,206,700,032 VM bytes** free; the 1.8 GiB / 3 GiB guards were unchanged.
- Both README shell blocks ran from script files with stdin closed, preventing the SSH directory check from consuming later shell instructions. Only the unused container name and port changed, as the README permits. Block 1 exited **0** at `2026-11-05T07:56:33Z`; block 2 exited **0** at `07:56:35Z`.

## Exact README commands executed

From an empty parent directory already shared with Colima:

```sh
git clone https://github.com/himanshu748/silentshift.git silentshift-judge
cd silentshift-judge
colima ssh --profile silentshift -- test -d "$PWD"
python3 - <<'PYCONFIG'
import os
from pathlib import Path
import secrets

values = {
    "IRIS_IMAGE": "silentshift-iris:2026.3.0AI.154.0",
    "SILENTSHIFT_IRIS_USERNAME": "ss-judge-reviewer",
    "SILENTSHIFT_VIEWER_USERNAME": "ss-judge-viewer",
    "SILENTSHIFT_IRIS_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_VIEWER_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_GATEWAY_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_PROVIDER_MODE": "recorded-replay",
    "SILENTSHIFT_AGENT_WAIT_SECONDS": "120",
    "SILENTSHIFT_EMBED_BASE_URL": "http://host.lima.internal:11434/v1/",
}
lines = Path(".env.example").read_text().splitlines()
content = "\n".join(
    line.split("=", 1)[0] + "=" + values[line.split("=", 1)[0]]
    if "=" in line and line.split("=", 1)[0] in values else line
    for line in lines
) + "\n"
with os.fdopen(os.open(".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as out:
    out.write(content)
print("Created private local replay configuration; no provider keys.")
PYCONFIG
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
chmod 644 .local/ipm/vendor/zpm-0.10.10.xml
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest \
  --execution-mode recorded-replay --container silentshift-bonus-registry-judge-nov5 \
  --api-port 52883 --execute
```

The driver issued literal `zpm "install silentshift"` against the public community registry, then explicitly ran `SilentShift.Setup.Install()`. The installed version was read back as **0.2.0**. It compiled the repository's test helpers and ran:

```objectscript
set ^UnitTestRoot="/home/irisowner/silentshift-bonus/tests/"
set manager=##class(%UnitTest.Manager).%New()
set passed=manager.RunTest("","/nodelete")
write "SS_UNIT_RESULT=",passed,!
```

From that same fresh clone, the second README block was:

```sh
uv run python scripts/trace_example.py \
  --api http://127.0.0.1:52883/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-registry-judge-nov5
```

## Actual results

Published console logs omit trailing whitespace only; private original logs are retained unchanged.

[Complete setup command output](evidence/judge-clean-clone-command-1.txt):

```text
Creating fresh public-registry verification container...
IPM install silentshift
Starting the installed native production (recorded-replay)...
Running the full native %UnitTest suite...
Running the no-key synthetic playback example...
```

The final JSON result reported `unit_suite_passed: true`, `replay_passed: true`, native version `0.2.0` and first replay session `24`. Its `native_five_passed` field is null because this was a recorded-replay run.

The installer and health checks reported:

```text
SS_MODULE_VERSION=0.2.0
SS_VERSION_OK
http_status: 200
production_running: true
```

The full native suite passed **five classes / 12 test methods**, not merely the test runner's return status:

```text
SilentShift.Test.AdapterChecks passed
SilentShift.Test.ProviderChecks passed
SilentShift.Test.ReplayChecks passed
SilentShift.Test.RuntimeChecks passed
SilentShift.Test.TraceChecks passed
All PASSED
SS_UNIT_RESULT=1
SS_UNIT_OK
```

The initial replay used case `69262B24-D8EE-11F1-897E-970E6F17AA2B`, session **24**. [Repeat command output](evidence/judge-clean-clone-command-2.txt):

```text
execution_mode=recorded-replay; fresh_inference=false
case_id=6BADC663-D8EE-11F1-897E-970E6F17AA2B; session_id=58
visual_trace_url=http://127.0.0.1:52883/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=58
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

Both replays passed **12/12**: five paired provider exchanges in the original case session, each of the four native tools executed once, recorded-replay provenance, null current token usage/cost, critical policy veto, `QUARANTINED` and zero delivery receipts. Full per-call metadata is retained in the receipt. Neither replay made a model or embedding request.

The actual runtime reported:

```text
IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT
```

## Other checks and boundaries

| Command | Checkout | Observed result |
| --- | --- | --- |
| `uv run pytest -q` | Fresh clone | `174 passed in 8.66s` |
| `npm --prefix web run check` | Primary checkout, unchanged source | Exit 0; TypeScript passed |
| `npm --prefix web run build` | Primary checkout, unchanged source | Exit 0; Vite built in 853 ms; existing Lucide `use client` warnings |

The browser suite was not repeated for this documentation-only update; the prior run recorded **38 passed (1.0m)**. The [earlier public-package live receipt](evidence/final-public-live.json) retains **5/5 expected final routes** on build 154U. It is not presented as a new live run or proof of model accuracy. No build 109, new package publication, public deployment or organizer award is claimed.

The new test gateway and IRIS container were stopped after verification and retained, with their logs and private credentials. The existing application was preserved. Session URLs are local to this retained instance and require restarting that pair; session IDs are not globally unique:

```sh
docker --context colima-silentshift start silentshift-bonus-registry-judge-nov5
docker --context colima-silentshift start silentshift-bonus-registry-judge-nov5-gateway
```

Use a permitted local IRIS account to view message bodies. The successful API replay does not bypass portal permissions. Existing [native Body screenshots](../README.md#native-provider-metadata) remain the screenshot evidence.

## Earlier failed attempts — retained history

The previous attempts remain documented in their original receipts; none is relabeled successful:

1. An installer copied with mode `0600` could not be read by IRIS. The README added `chmod 644` for that public installer only. [First attempt and disk-gated retry](evidence/judge-verification.json), [loader error](evidence/judge-first-client-error.txt).
2. A sibling checkout installed the package but was outside the Colima shared directory, preventing gateway bind mounts. The README added the shared-directory prerequisite and early visibility check.
3. A later shared checkout installed the package and completed setup, then stopped at the host-space guard. The user requested stopping. [Resumed-attempt receipt](evidence/judge-resumed.json).
4. The November 5 run above used the corrected unchanged recipe after more host space became available. No further cleanup or lower safety floor was needed.

The separate November 4 retained-instance replay passed **12/12**, session **59**; [its evidence](evidence/freeze-build154-replay.json) remains independent of this clean-clone proof.

No external edit was part of the test run itself. The user subsequently authorized filing the [AI Hub bug as #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) and submitting the [OEX description](OPEN_EXCHANGE_COPY.md); both actions were verified on November 5. [OEX submission receipt](evidence/oex-submitted-nov5.json). Developer Community was unchanged. Organizer awards and public visibility of the dedicated OEX idea association remain unconfirmed.
