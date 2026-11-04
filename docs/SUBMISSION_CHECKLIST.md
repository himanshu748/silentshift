# Submission status and remaining steps

Updated November 4, 2026. Deadline: **November 9 at 10:29:59 IST / November 8 at 23:59:59 EST**, per [contest 49](https://openexchange.intersystems.com/contest/49). SilentShift is visibly on that contest's registered-app list. No organizer score or bonus award is claimed.

## Verified entry

| Item | Evidence |
|---|---|
| Native runtime | Official ARM64 Community AI Hub **2026.3.0AI.154.0 (Build 154U)**; no build-109 claim |
| Current live regression | **5/5 final routes**, four native tool reads per case, ten local provider pairs; sessions 1667, 1695, 1723, 1750, 1778. [Receipt](evidence/bonus-020-live.json) |
| Source-load replay | Fresh 0.2.0 load without mounts; corrected native suite **5 classes / 12 methods**, API replay **12/12**, session **24**, five recorded exchanges and zero deliveries. [Receipt](evidence/idea-replay-load.json) |
| Release-source identity | All **55 runtime/package source files** match the successful first clean-load stage byte for byte; unverified inspector refinement removed |
| Local checks | `uv run pytest -q`: **172 passed in 6.74s**. TypeScript and production web build passed; existing Lucide directive warnings retained |
| Open Exchange | Developer portal shows Published; existing 0.1.0 release, contest/IPM checked, dedicated DPI-I-689 field and video read back. 0.2.0 release is the current publication step |
| Public IPM | Anonymous 0.1.0 metadata/manifest HTTP 200. 0.2.0 public publication/install is a separate gate below |
| Video | [Public 2:30 demo](https://youtu.be/a4dOcqu89EA); prior 1080p/caption playback evidence retained |
| Articles | [Semantic validation](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [recoverable review](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery), submitted for moderation; public approval not refreshed |
| Questionnaire | Submitted previously with the user's answers; [receipt](assets/questionnaire-submitted.png). Do not submit again |

A second source-container load succeeded, but activation stopped at the disk-space floor; a post-restart readiness check also failed. That attempt was stopped under the two-failure rule. Colima's local disk capacity was increased from 16 to 20 GiB, with no files/volumes deleted. It does not replace the successful first fresh-load evidence above.

## Remaining gates in order

1. **Native metadata screenshot for DPI-I-689 (up to 4 points).** Use an existing authorized administrator account to open [the retained live trace](http://127.0.0.1:52773/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=374), select a CallResponse and its Body tab, and capture the visible model/prompt/timing/token properties. The agent-accessible portal still shows Login after the sign-in handoff. Standard reviewer graph access works, but native body access was denied twice; no password change or permanent permission expansion was made. Existing captures show graph/pair timing only. README/OEX idea links, reproducible provider replay, metadata exports and Langfuse comparison are present; the body-panel screenshot remains explicitly unverified.
2. **Publish and verify 0.2.0 through Open Exchange (IPM: 2 potential points).** Main must contain the tested manifest/source. Use My Applications → SilentShift → ellipsis → Add new release → Add new release → version 0.2.0 → release notes → Publish. Preserve the contest, IPM and idea fields. Refresh the description from the README and read back moderation state. Do not Unpublish or Cancel approval.
3. **Clean public-registry install.** After public 0.2.0 appears, run the exact `--source public-registry` command in [IPM.md](IPM.md#verify-a-public-install-in-a-second-clean-container). Require production startup, the full native suite and API replay to pass. A public badge or manifest alone is insufficient. Stop after two failures.
4. **Article moderation (2 + 1 potential points).** Check both existing posts after moderation; verify their public canonical links, then update the README pending-publication entries and OEX article associations. Do not create duplicate articles.
5. **Final public readback.** Confirm the release, README, video and registry version, and that SilentShift remains on [contest 49](https://openexchange.intersystems.com/contest/49). Do not untick Submit to Contest. Personal eligibility and organizer awards remain independent of technical verification.

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
| Public IPM package | 2 | 0.1.0 publicly listed; 0.2.0 install gate pending |

The rows total 24 potential points, with no awarded-score or ranking claim. There is no hosted demo, Java/.NET PEX integration or confirmed vendor-bug bonus. The [engineering evidence](BONUS_EVIDENCE.md) distinguishes live inference, recorded playback, source loading, public installation and publication.
