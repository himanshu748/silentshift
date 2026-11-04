# Submission status and remaining steps

Updated November 4, 2026. Deadline: **November 9 at 10:29:59 IST / November 8 at 23:59:59 EST**, per [contest 49](https://openexchange.intersystems.com/contest/49). SilentShift is visibly on that contest's registered-app list. No organizer score or bonus award is claimed.

## Verified entry

| Item | Evidence |
|---|---|
| Native runtime | Official ARM64 Community AI Hub **2026.3.0AI.154.0 (Build 154U)**; no build-109 claim |
| Current live regression | **5/5 final routes**, four native tool reads per case, ten local provider pairs; sessions 1667, 1695, 1723, 1750, 1778. [Receipt](evidence/bonus-020-live.json) |
| Source-load replay | Fresh 0.2.0 load without mounts; corrected native suite **5 classes / 12 methods**, API replay **12/12**, session **24**, five recorded exchanges and zero deliveries. [Receipt](evidence/idea-replay-load.json) |
| Release-source identity | All **55 runtime/package source files** match the successful first clean-load stage byte for byte; unverified inspector refinement removed |
| Local checks | `uv run pytest -q`: **172 passed in 3.13s**. TypeScript and production web build passed; existing Lucide directive warnings retained |
| Open Exchange | Developer portal shows Published; existing 0.1.0 release, contest/IPM checked, dedicated DPI-I-689 field and video read back. 0.2.0 release published successfully; README-backed description refresh sent for approval |
| Public IPM | 0.2.0 metadata/manifest HTTP 200; clean public install, startup, all 12 native methods and replay 12/12 passed. [Receipt](evidence/bonus-020-registry-install.json) |
| Video | [Public 2:30 demo](https://youtu.be/a4dOcqu89EA); prior 1080p/caption playback evidence retained |
| Articles | [Semantic validation](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [recoverable review](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery), submitted for moderation; public approval not refreshed |
| Questionnaire | Submitted previously with the user's answers; [receipt](assets/questionnaire-submitted.png). Do not submit again |

A second source-container load succeeded, but activation stopped at the disk-space floor; a post-restart readiness check also failed. A later independent clean public-registry run passed the full suite and replay. That source attempt was stopped under the two-failure rule. Colima's local disk capacity was increased from 16 to 20 GiB, with no files/volumes deleted. It does not replace the successful first fresh-load evidence above.

## Remaining gates in order

1. **Native metadata screenshot for DPI-I-689 (up to 4 points).** Sign in to the existing [live session 1723](http://127.0.0.1:52773/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=1723) using an administrator account already permitted to view message bodies. Select a CallResponse and **Body**, then capture model, prompt version, duration and token properties. The agent-accessible portal still shows Login after the handoff; standard reviewer body access was denied twice. No password change or permanent permission expansion was made. Existing captures show graph/pair timing; current metadata is independently exported from native bodies. README/OEX idea links, exact no-key recipe and Langfuse comparison are present. This body-panel image remains explicitly unverified.
2. **Check description moderation.** Release **0.2.0 is published**, public IPM **0.2.0 is installed and verified**, and SilentShift remains in contest 49. The README-backed description refresh is separately **sent for approval**. Preserve that request, the dedicated idea field and the checked contest/IPM options; do not Cancel approval or Unpublish. [Release receipt](assets/oex-020-release-published.jpg) · [description request](assets/oex-020-description-sent.jpg) · [contest card](assets/oex-contest-49-silentshift.jpg).
3. **Check article moderation (2 + 1 potential points).** Review the two existing submitted posts after moderation; verify public canonical URLs, then replace the README pending-publication labels and update OEX article associations. Do not create duplicate posts. No new article publication was performed in this task.
4. **Check personal eligibility and organizer decisions.** The technical tests do not establish personal eligibility, moderation approval or awarded points. Video and questionnaire already have receipts; no new upload or duplicate questionnaire response is needed.

## Bonus evidence

All points are **potential**, with organizer acceptance unconfirmed. [Official criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows).

| Criterion | Points | State |
|---|---:|---|
| Embedded Python | 3 | Native deterministic policy and installed Python origins verified |
| Docker | 2 | Official build 154U and isolated installations verified |
| Native Workflow | 2 | Real tasks, review, concurrency and recorded-decision recovery verified |
| Custom adapter | 2 | Actual ready-file intake, held/delivered cases and duplicate protection verified |
| IRIS vector retrieval | 2 | Native vectors/cosine, fourth tool and critical veto verified |
| DPI-I-689 | Up to 4 | README/OEX link, live/replay metadata and comparison present; body-panel capture remains a gate |
| Questionnaire | 1 | Previously submitted |
| YouTube demonstration | 3 | Published with retained caption/1080p evidence |
| First / second article | 2 + 1 | Submitted for moderation |
| Public IPM package | 2 | 0.2.0 published and clean public install/startup/full suite/replay verified |

The rows total 24 potential points, with no awarded-score or ranking claim. There is no hosted demo, Java/.NET PEX integration or confirmed vendor-bug bonus. The [engineering evidence](BONUS_EVIDENCE.md) distinguishes live inference, recorded playback, source loading, public installation and publication.

Exact commands and observed outputs are in [RELEASE_REPORT.md](RELEASE_REPORT.md).
