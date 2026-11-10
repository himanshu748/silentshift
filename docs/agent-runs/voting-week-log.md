# SilentShift voting-week run log

All timestamps below are IST (UTC+05:30). Public changes freeze **November 16, 2026 at 07:00 IST**; voting closes **November 16 at 10:29:59 IST**. Submissions are closed. No new entry will be registered.

## Action gate

Open Exchange approval/publication, organiser email/message, community post/comment, video upload and tags/releases require a prepared draft and screenshot, then the owner's exact **`submit`**. Each approval permits only the identified action, followed by anonymous readback. No sending or publishing occurred in this pass. No account, password, billing or contest settings were changed.

## 2026-11-10 13:55:41 IST — Phase 0 orientation and readback

| Action | Result | Decision |
| --- | --- | --- |
| Clone GitHub main into an ignored scratch directory | HEAD `a10de3f61e1d809b374832a4db67761318bc16ea` | Judge-facing main is separate from the existing `push/top3` checkout at `e36ba2e`; preserve pre-existing README/UI edits and incomplete local evaluation artifacts |
| Read README, INSTALL and the six requested contest/evidence/hosting/judge/listing documents | Public native IPM/OEX 0.3.0; separate React 0.2.1. Main retains historical stale idea-visibility and hosting-permission statements; source branch has later corrections | Qualify dated evidence; never present unpublished branch work as registry contents |
| Check official contest, rules, bonuses and voting post | SilentShift is registered among 44 apps; voting is Nov 9–15 EST; improvements during voting are permitted | User's voting deadline matches. App order and signed-in voting preferences are not final rankings or awards |
| Compare public listing and signed-in owner view | Anonymous listing has native/archive 0.3.0, install command, current CSV release notes, dedicated DPI-I-689, video, MP4 and both articles. Body still says public IPM 0.2.0/source-only CSV | Description remains inconsistent; public association issue is resolved, four-point qualification is not confirmed |
| Inspect owner editor without writing | Correct 0.3.0 body is already saved; status Published plus unpublished changes. IPM checked, idea/video/articles preserved, Demo URL empty. No Submit to Contest control exposed on this edit page | Do not duplicate the edit or change contest registration. Prepare submission of this existing description only; wait for exact `submit` |
| Read both articles anonymously and in signed-in browser | Both return HTTP 200, expose owner Edit links in the existing signed-in session and link OEX/repo/video. Their results concern historical synthetic cases | No article edits or new posts. Review article's older first-article slug and main INSTALL's missing 109 caveat are Phase 3 link/documentation follow-ups |
| Check original video | Anonymous oEmbed HTTP 200; signed-in Studio shows Public with disabled Save; player runs and displays captions | Accessible video confirmed; no re-upload needed. Video predates CSV, which the description already discloses |
| Download MP4 anonymously to a streaming digest | HTTP 200; 3,561,558 bytes; SHA-256 `9ad0e678ded827cf07dd087be936a8c2b168cacb7d07b3c7655357f6d91a5d7d`; matches fresh-main file | Downloadable without registration. No duplicate binary added |
| Check video acknowledgement | No SilentShift-specific acknowledgement in bonus/voting thread text. Iryna's public article comment confirms featuring the demo on InterSystems Developers YouTube | No duplicate follow-up drafted or sent: staff feature is acknowledged, bonus award still unconfirmed |
| Check declared build against official clarification | Organiser allows 2027.1.0AI.109.0; our verified target remains only 2026.3.0AI.154.0 / 154U ARM64 | No 109/x64 claim. Add allowed-but-unverified caveat to INSTALL during Phase 3; image must be obtained independently, never redistributed |

### Evidence and exact checks

- [Anonymous receipt](../evidence/voting-week-nov10/public-readback.json), produced with `python3 .local/voting-week/check_public.py`; [executed script](../evidence/voting-week-nov10/check_public.py). Only unauthenticated HTTP reads and a full streamed MP4 digest ran. `Content-Type` for the MP4 was `application/octet-stream`; the response bytes matched the checked-in MP4 exactly.
- [Owner receipt](../evidence/voting-week-nov10/owner-readback.json), [saved field readback](../evidence/voting-week-nov10/oex-owner-fields.txt), [approval-boundary screenshot](../evidence/voting-week-nov10/oex-owner-pending.jpg), [video visibility](../evidence/voting-week-nov10/youtube-visibility.txt).
- [Exact prepared OEX description](oex-description-approval.md). This excludes the separate unpublished provider/frontend/evaluation proposal in the earlier source-branch draft. No new release or registry publication is part of the approval target.
- No native suite, replay, model investigation, UI regression suite or new installation ran in Phase 0. Earlier execution receipts retain their original scope. Reading a clone and checking links does not renew them.

### Sources and differences from the brief

- [Contest 49](https://openexchange.intersystems.com/contest/49): registration still present; 44 apps at this check. No standings or bonus award inferred.
- [Announcement and Nov 2 build clarification](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-interoperability-workflows): 109 is permitted, not locally tested; continued improvements are permitted.
- [Technology bonuses](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows): README idea link, dedicated OEX association and reproducible Visual Trace are the relevant idea requirements; comparison supplied. Staff says bonus review results will be announced during the week. No result is assumed.
- [Voting post](https://community.intersystems.com/post/time-vote-intersystems-programming-contest-ai-agents-interoperability-workflows): voting is blind; listed order is submission order, not an expert ranking.
- [Staff video feature](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production#comment-288552): confirms featuring, not award or bonus qualification.
- Main's older hosting review says permission is absent. The later source-branch review records Irene's Nov 8 contest-demo permission; **deployment**, not that historical permission gate, remains unverified. No hosting or online-demo bonus is claimed.

### Earlier proposed gated action — superseded by the queue check below

Send **only the existing corrected OEX description** for approval, after the owner replies exactly `submit`. Do not publish a release/package, cancel approval, change contest registration or send an organiser message. If the site offers a second consequential action beyond submitting these description edits, stop. Then read the public listing anonymously and log whether moderation is still pending or the corrected text is live.

Embedded Python, Java/.NET PEX and online-demo bonuses remain **Not claimed**. AI Hub issue #17 is not duplicated or commented on. Questionnaire is not resubmitted. No money is spent, EAP software is not redistributed, and no public Git push or other external write is performed.


## 2026-11-10 14:02:17 IST — Check for an existing moderation request

- **Action:** re-read the existing OEX owner editor without pressing Save, Send for approval or any cancellation control. It shows Published, unpublished changes and Send for approval; no Awaiting Review or Cancel approval indicator is visible. [Fresh UI readback](../evidence/voting-week-nov10/approval-status-recheck.txt) · [screenshot](../evidence/voting-week-nov10/approval-status-recheck.jpg).
- **Historical cross-check:** the November 8 publication receipt records successful submission of the later 0.3.0 description correction. The earlier 08:26 UTC approval email preceded that correction; the 10:00 UTC email confirms IPM publication, not approval of the corrected description. The owner's 10:14 UTC sent message also explicitly records the correction submission. Targeted Gmail searches included Spam and found no later confirmation for this description. No private mail headers or raw mailbox exports were added to Git.
- **Result:** the live moderation queue is **unconfirmed**, not proven empty. The previous suggestion to submit immediately is superseded. An available Send button does not conclusively establish that no request is queued.
- **Decision:** do not resubmit the description. [One short queue-check reply is prepared](oex-description-queue-note.md), addressed to the existing Open Exchange team conversation. It asks them to process the existing correction if queued, or say whether resubmission is needed. It does not repeat the resolved idea-visibility request, ask for another release or make an award claim.
- **Next gated action:** only this **email reply**, after exact `submit`. That approval would not authorise an OEX form submission. Nothing was sent, posted, saved in OEX/Gmail, published, cancelled or pushed. Contest registration and package/video/article/idea fields were untouched.
- [Sanitised queue-check receipt](../evidence/voting-week-nov10/approval-queue-check.json). Native tests and models were not run for this read-only check.


## 2026-11-10 14:21:36 IST — Authorised queue-check email sent

- **Authorisation:** owner replied exactly `submit` to the proposal for one email reply only. This did not authorise OEX form submission or any other external action.
- **Action:** sent the [prepared queue-check note](oex-description-queue-note.md) to `openexchange.team@intersystems.com` in the existing SilentShift conversation. No CC/BCC or attachment was added. The reply asks whether the existing correction is queued and avoids duplicate moderation submission.
- **Verification:** Gmail readback shows **SENT**, message `1a1c4a7d62d2d426` in thread `1a1ba468d483b833`. The new reply text matches the approved draft; the mail service appended the ordinary quoted prior conversation. [Sanitised receipt](../evidence/voting-week-nov10/queue-note-sent.json). This proves sending, not recipient acknowledgement or moderation approval.
- **Anonymous readback after sending:** HTTP 200; public archive/release 0.3.0 and dedicated idea section remain present; old 0.2.0/source-only CSV body text remains. [Public readback](../evidence/voting-week-nov10/queue-mail-public-after.json). The first default-User-Agent request returned 403; the one explicit-verifier retry succeeded. No further retry was made.
- **Decision:** wait for the team's queue clarification. Do not resubmit the OEX form, send another follow-up, publish a package/release, change contest selections or infer bonus qualification. No model/test run, spending or Git push occurred.


## 2026-11-10 14:28:30 IST — Renewed Phase 1: existing description prepared, not submitted

- **Owner direction:** prepare Send for approval on the existing corrected description, with no other edits, then screenshot and stop for exact `submit`. This supersedes the earlier local recommendation to wait for a queue clarification; it does not establish that the earlier request is absent.
- **Mail:** read both existing Open Exchange team threads and searched including Spam. No new OEX reply was found. The previously authorised email remains sent at 14:21:36 IST; no duplicate message was sent. No four-point confirmation is claimed.
- **Owner readback:** Published + unpublished changes, active Send for approval, no visible Awaiting Review or Cancel approval control. The saved description matches the prepared approval body exactly. IPM stays checked; idea, video and articles retain their values. No contest control was touched. The current editor does not expose a Submit to Contest checkbox; registration was separately observed in Phase 0.
- **Public readback:** {"url": "https://openexchange.intersystems.com/package/SilentShift", "authentication": "none", "http_status": 200, "archive_030_visible": true, "legacy_native_020_visible": true, "legacy_source_only_csv_visible": true, "dedicated_idea_section_visible": true}. This checks visibility, not moderation's internal queue.
- **Prepared artifact:** [exact unchanged description](oex-description-approval.md), [fresh screenshot](../evidence/voting-week-nov10/phase1-approval-ready.jpg), [sanitised receipt](../evidence/voting-week-nov10/phase1-approval-ready.json), [owner readback](../evidence/voting-week-nov10/phase1-approval-ready-owner.txt).
- **STOP:** no Save, Send for approval, release, email, post, upload, tag, registry publication, deployment, spending or public Git push occurred. The next exact `submit` would authorise only submitting these description edits. Later external actions each need their own approval. No runtime or model/test execution took place.


## 2026-11-10T14:32:35.751726+05:30 — Logo assets created locally

- **Owner request:** create a SilentShift logo. Used the built-in image generation tool to create an S mark from offset record forms, a matching wordmark and a standalone square icon. Used the existing product's ink/accent tokens; did not redesign the frontend.
- **Artifacts:** [transparent wordmark PNG](../assets/brand/silentshift-logo-v1.png), [transparent icon PNG](../assets/brand/silentshift-icon-v1.png), [generation receipt](../assets/brand/logo-v1-receipt.json), [prompts and usage](../assets/brand/README.md). Raster assets, not vector masters. Both inspected visually; metadata checks are recorded alongside them.
- **Boundary:** source images copied into the workspace, originals preserved. No existing logo, app code, OEX field or runtime behavior was replaced. No upload, public push, approval submission, release or paid provider call occurred. The existing OEX description remains at its separate exact-`submit` gate; this logo request does not approve submission or a logo upload.


## 2026-11-10 14:52:12 IST — Phase 2 public competitive scan

- Read all **44** contest listing pages and **44** linked default-branch READMEs anonymously. [Comparison report](competitor-scan.md) records author, task, stated AI Hub/native boundaries, media, package/setup signals, candidate bonus technologies and visible review counts. [Observation receipt](../evidence/voting-week-nov10/competitor-scan.json). No competing app was installed, logged into, exercised or model-tested.
- Ten editorial comparison targets and five prioritised gaps are documented. These are public-presentation judgments, not expert rankings or functional test results. Four advertised runtime-demo landing pages returned HTTP 200; no native/live-demo inference was verified. Subscription counters were not relabelled likes or votes.
- The official voting post still has no published leaderboard comments in the inspected anonymous text; voting is blind. Third and later articles bring no additional article bonus. No new award, point total, win probability or health outcome is claimed.
- Gmail check: both existing OEX conversations contain no new organiser reply; the latest remains our authorised 14:21 IST queue-check email. No duplicate follow-up was sent. The new mission's prepare-only OEX approval gate remains active; `go on` is not exact `submit`.
- No public edit, post, vote, email, registry action, release, hosting or spending occurred.


## 2026-11-10 14:52:48 IST — Fresh-main public judge path passed

- Started the existing local Colima profile without a new image download. It had no running containers; official ARM64 154U and Web Gateway were loaded. A new GitHub main clone at `a10de3f61e1d809b374832a4db67761318bc16ea` followed the documented setup/keyless path with private, freshly generated local test passwords and no provider keys.
- Public native IPM **0.3.0** installed using literal `zpm "install silentshift"`; production started, **5 native classes / 12 methods** passed, and two recorded replays passed **12/12** each, sessions **24 / 58**, quarantined with zero deliveries. Fresh-clone `uv run pytest -q`: **207 passed in 11.40s**. [Receipt](../evidence/voting-week-nov10/judge-main-nov10.json) · [executed commands/output](../evidence/voting-week-nov10/judge-main-commands.txt).
- The new test IRIS/gateway were retained stopped after capture to limit memory before the separate wrapper check. No prior container, source, model or benchmark result was deleted or changed. No fresh inference or new native live5/5 claim.
- Found a harness-boundary issue during preparation: current source adds native cited-finding/permission tests that public0.3.0 cannot satisfy. The new launcher now uses a pinned release-matched verification checkout; it does not call an older public package a test of unpublished runtime code. Wrapper native verification is separate and not yet claimed here.


## 2026-11-10 15:06:53 IST — Phase 3 judge-path improvements and validation

- Added the source-only `scripts/judge_replay.py` launcher and focused failure-boundary tests. It preflights the exact local build/architecture, gateway, context and port; obtains a pinned compatible verification checkout, generates private credentials, installs public0.3.0 and runs two recorded replays. It never edits existing `.env`, lowers disk limits, pulls an IRIS image, calls a model or replaces a container.
- Actual launcher gate: **5 native classes / 12 methods**, two **12/12** recorded replays, quarantine and zero deliveries, sessions **24 / 58**; total command **155.331 seconds**. [Receipt](../evidence/voting-week-nov10/judge-wrapper.json). This tests public0.3.0, not unpublished narrative/provider runtime changes.
- Actual working-tree checks: `uv run pytest -q`: **330 passed in 22.60s**; focused launcher tests: **12 passed in 0.42s**; TypeScript/build passed with existing non-fatal lucide-react directive warnings. A real deliberately missing-image invocation returned the intended clear error before creating run files. All Compose variable names are represented in `.env.example`. [Checks](../evidence/voting-week-nov10/judge-polish-checks.json).
- README now leads with the operator problem and a no-install video/captured-evidence path. Four existing captures have contextual annotations; measured benchmark results and every honest limit are preserved below that path. Added per-bonus evidence links and a short intended-user/value section. INSTALL distinguishes source branch, public package and unverified build109; the keyless route is one command with three first-run remedies.
- Earlier link check, before the final README setup consolidation: **52 local paths/anchors** and **7 external URLs**, all resolved. [Receipt](../evidence/voting-week-nov10/judge-links.json). No native runtime source, routing policy, source model execution or UI code was changed in this pass. Pre-existing UI edits and incomplete sealed-run data were preserved, not staged as part of this work.

## 2026-11-10 15:06:53 IST — Phase 4 drafts and Phase 5 daily read-only loop

- Updated the existing [technical article draft](../articles/draft-what-was-hard.md) rather than creating another duplicate. Prepared one [voting-thread comment](voting-thread-comment.md) and one [LinkedIn post](linkedin-post.md), each useful and without vote solicitation, vote exchanges or competitor criticism. All are unsent and require separate exact-`submit` approval. A third article would add no further article-bonus points.
- Prepared a [future OEX screenshot addendum](oex-screenshot-addendum.md), explicitly separate from the currently approved-for-review description. It was not entered into the OEX form. The currently prepared owner description remains unchanged at its exact-`submit` gate.
- Prepared the [local CSV media supplement](csv-supplement.md) using existing captured UI, H.264/AAC and captions, not a new live recording. No upload, narration generation, re-upload of the original demo or provider call.
- Updated the existing monitoring automation, without creating a duplicate, to run daily at **06:00 IST**. It checks public listing, organiser mail including Spam, official leaderboard, meaningful rival updates and existing issue/support feedback; it may append only a factual local log entry. It cannot send, submit, publish, vote, run models/tests, deploy or spend. Its November16 morning check must provide the final read-only status and remove the automation before the 07:00 IST public-change freeze.
- No public Git push, package publication, OEX edit, email, post/comment, upload, tag/release, questionnaire resubmission or new bug filing occurred. The 14:21 IST email remains the only previously authorised external action in today's log. Remaining gates: description approval, owner merge/publication choices and external idea/bug qualification. No rank or award is predicted.


## 2026-11-10 15:09:24 IST — Final local readback for this pass

- The OEX owner form still matches the exact prepared description and shows unpublished changes plus Send for approval. No form action was taken. Both mail conversations were re-read; no new organiser reply has arrived after the authorised 14:21 IST message. The next exact `submit` still refers only to the unchanged OEX description submission, not any post, video, gallery or email.
- The separate wrapper test containers were retained stopped after evidence capture; no existing app/benchmark container was modified and nothing was deleted. Re-starting the matching retained test pair is required to inspect its printed local trace URL. A user's successful launcher run retains its new resources for inspection.
- Local CSV supplement: **48.021333 seconds**, **1920×1080 H.264**, silent AAC, English captions, under 50 MiB. Historical November8 captures are visibly labelled throughout, with source hashes in the receipt. No generated voice, staged UI/model response, new live inference, upload or public-demo claim. [Media details](../evidence/voting-week-nov10/csv-supplement.json).
- No main-branch push, PR edit, registry publication, public listing change or social post occurred. Current docs/harness commits are local on `push/top3`; unrelated pre-existing frontend edits and incomplete sealed-run data remain uncommitted and untouched. This is a local checkpoint, not the November16 final public freeze report.


## 2026-11-10 15:13:35 IST — Final documentation checks

- Consolidated the README's full setup instructions into INSTALL rather than duplicating them. Final link probe: **51 local paths/anchors** and **7 external URLs**, all resolved. This is the final receipt; the earlier 52-link count described the pre-consolidation draft.
- AI Hub issue17 was read again: still open, no comments or labels, no vendor/organizer confirmation. [Readback](../evidence/voting-week-nov10/issue17-final.json). No bug action was taken.
- The original complete v2 comparison remains in the README with every result/limit, now explicitly labelled as preceding later pipeline changes. The incomplete sealed run is not presented as a result. No label or model output was edited.
- Native source and UI behavior were not changed in this pass. The new code is only the release-pinned verification launcher and its focused tests. No new source-native5/5, connected-browser or live deployment result is claimed. All gated drafts remain unsent.

### 2026-11-10 15:20:56 IST — Backend addendum, item 1

- Created `backend-polish-nov10`; preserved earlier staged drafts and user UI changes without committing them. No push.
- Official announcement says: “You can continue improving your application throughout both the submission and voting periods.” Source: https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-interoperability-workflows (read today).
- Added host-only stable-code/stage/case-id Event Log messages, Semantic stage traces and one routing info event on the normal path or successful containment. No payload, prompt, provider or exception text is logged.
- `uv run pytest -q`: 330 passed in 21.92s; [output](../evidence/backend-polish-nov10/01-pytest.txt). Native compilation/readback still pending.
- Earlier screenshot/Pages work remains queued; community posting is owner-handled. All external actions, including pushes, require exact `submit`.

### 2026-11-10 15:22:36 IST — Backend item 2

- Setup/IPM catch statuses now retain friendly context plus the bounded original error text after configured password/key values are redacted. The same text is stored server-side in `^SilentShift.Diagnostics("last_setup_error")`; persistence failure does not replace the original failure.
- `uv run pytest -q`: 336 passed in 43.42s ([output](../evidence/backend-polish-nov10/02-pytest.txt)). The increase includes the shell/archive harness tests being prepared independently. Native diagnostic readback is pending.
