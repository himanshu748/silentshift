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

### 2026-11-10 15:26:19 IST — Backend item 3

- Formatting-only cleanup in the requested classes; the API token stream is unchanged apart from whitespace. XData joins JSON string fragments without separators.
- Pre-relocation system prompt: 1,959 UTF-8 bytes, SHA-256 `6e7453ef1af46af157c64dbc0ea93953da508c5b278b3dd1c25b71b5ff7aedc3`. Byte-equality regression passed.
- `uv run pytest -q`: 337 passed in 25.73s ([output](../evidence/backend-polish-nov10/03-pytest.txt)). Native compile remains pending.

### 2026-11-10 15:29:21 IST — Native formatting regression corrected

- First native candidate load failed: spaces inside two UUID pattern alternations caused ObjectScript #1020. [Original failure](../evidence/backend-polish-nov10/03-native-compile-failed.txt). Restored both exact patterns and added a regression test.
- Second load compiled and activated all candidate classes/assets successfully in the same fresh test container; this is a retry of a failed load, not a second fresh-install claim. [Output](../evidence/backend-polish-nov10/03-native-compile-retry.txt). No production/model invocation in this retry.
- `uv run pytest -q`: 338 passed in 21.22s ([output](../evidence/backend-polish-nov10/03b-pytest.txt)). Final fresh-clone gate remains required.

### 2026-11-10 15:32:33 IST — Backend item 4

- Centralized exact tool membership, native-only scope/budget/trace preamble, model default, Python import setup and precedent metadata parameters. Native callbacks perform no new Python/SQL work.
- `/api/policies` reads the unchanged seven-rule catalog via Bridge; preserved its existing catalog version 1.1.0 separately from routing engine version 1.2.0. No policy decisions changed: AST is identical after excluding the new RULES assignment.
- Added native regression checks for runtime prompt bytes, allowlist, redaction and catalog/default model. `uv run pytest -q`: 339 passed in 24.27s ([output](../evidence/backend-polish-nov10/04-pytest.txt)). Native helper execution still pending.

### 2026-11-10 15:34:31 IST — Backend item 5

- Before compacting replies, searched native process/service, web, scripts and native tests: no consumer reads References/Destination/Quarantine BodyJSON; their callers re-read Store. Partner still receives Semantic’s full case body. ProviderProbe ignores internal reply bodies.
- Those three acknowledgments now contain only case_id, routing and version; added a native summary-shape regression and message descriptions.
- Step-4 helpers also executed successfully on 154U: canonical JSON, default model, original runtime prompt hash and complete rule catalog ([native output](../evidence/backend-polish-nov10/04-native-smoke.txt)). This was an upgrade of the early isolated test instance, not a new clean-install claim.
- `uv run pytest -q`: 339 passed in 21.91s ([output](../evidence/backend-polish-nov10/05-pytest.txt)). Production reply inspection remains part of final gate.

### 2026-11-10 15:40:30 IST — Backend item 6

- Semantic now calls private stages in the original order. ApplyScenarioFault statements/strings match the pre-refactor conditional exactly ([comparison](../evidence/backend-polish-nov10/06-fault-invariant.json)).
- Declared administrator settings with existing defaults: normal step timeout 10s, optional-reference limit 10 per authority, empty Investigator wait/model overrides falling back to environment, adapter InboxPath defaulting to ROOT. Containment keeps its fixed 10s bound if configuration itself is invalid.
- One routing INFO is emitted only after the final response is constructed; failure then containment does not duplicate it.
- `uv run pytest -q`: 339 passed in 50.54s ([output](../evidence/backend-polish-nov10/06-pytest.txt)). Native settings/default tests remain pending.
- Static page also rendered locally at desktop/mobile breakpoints with keyboard anchor navigation and loaded historical captures; not published, and new production captures are still pending.

### 2026-11-10 15:44:45 IST — Backend item 7

- Discarded unused Review return value while preserving the call. CSV preserves a pristine parsed bundle before annotations, eliminating a redundant parse without admitting annotated authority. pyproject now matches module 0.3.0; Ruff 0.17.4 is a dev dependency.
- The requested Investigator HTTPS branch is already absent. Legacy API key names remain redaction-only and are commented accordingly. Configurable providers already exist on this source branch; claiming every live path is pinned by Lease.LocalHost would be false. Only local Qwen execution is qualified here.
- Ruff safe fixes applied outside fixtures/raw evidence. Initial whole-tree count: 154; scoped pre-fix: 144; final whole-tree: 79. Remaining findings retained, no failing Ruff CI step added, no unsafe fixes. Historical evidence scripts were not rewritten.
- Auto-removal of pilot re-exports caused 17 tests to fail; restored explicit exports. Preserved the original engine Decimal literals and proved all engine functions/classes have identical ASTs ([invariants](../evidence/backend-polish-nov10/07-policy-invariants.json)). Fixed loop binding in review and adapter verification helpers.
- Final `uv run pytest -q`: 339 passed in 22.24s ([output](../evidence/backend-polish-nov10/07c-pytest.txt)). Original failure and both subsequent passing runs retained.

### 2026-11-10 15:49:05 IST — Native defaults test repair

- All source compiled and production started on 154U. First native suite exposed an invalid test assumption: an Ensemble host cannot be instantiated with plain %New without production configuration. Replaced that with status-checked Ens.Director reads of the actual running hosts and adapter.
- Native suite retry: All PASSED. This was an isolated same-instance source upgrade, not a fresh-install claim. Original failure retained. Keyless replay: 12/12, session 46, five provider pairs, QUARANTINED, zero receipts; no fresh inference.
- `uv run pytest -q`: 339 passed in 21.06s ([output](../evidence/backend-polish-nov10/07d-pytest.txt)).

### 2026-11-10 16:00:18 IST — Backend item 8 and production checks

- Exported nine generated Storage Default blocks using $SYSTEM.OBJ.ExportUDL after compiling on 154U; copied only those exact blocks into Data classes and ReviewTask. Commit c3302c3 contains only storage additions. [Hashes/provenance](../evidence/backend-polish-nov10/08-storage.json). `uv run pytest -q`: 339 passed in 20.44s.
- Native suite retry produced All PASSED: seven classes / 22 methods. Recorded replay scored 12/12 at session 46. Native CSV commit/repeat with an existing-case annotation succeeded; no CSV cases were dispatched for inference. [Probe](../evidence/backend-polish-nov10/csv-probe.txt).
- Review queue verifier initially assumed an /opt source mount. Added a backwards-compatible --test-root for copied native checks, then it passed reject 26/26 and approve 26/26, including concurrency and one delivery receipt. [Receipt](../evidence/backend-polish-nov10/upgrade-review.json).
- A separate metadata-inspection helper failed twice (interactive loop, then temporary helper indentation). Stopped that helper, rejected its partial result and recorded passed=false; do not claim it verifies compact production reply bodies. [Blocked receipt](../evidence/backend-polish-nov10/08-production-routes.json). Native compact-summary unit test remains separately passed. No runtime workaround was introduced.
- `uv run pytest -q` after the verifier path fix: 339 passed in 21.19s ([output](../evidence/backend-polish-nov10/08b-pytest.txt)). 0.3.1 promotion remains on hold pending complete production readback.

### 2026-11-10 16:04:26 IST — Backend item 9

- Added a short operator section to IPM.md: SILENTSHIFT/build-154 requirement, single configured Workflow reviewer, 20-row CSV cap, verified local model/embeddings, and a manual ownership-aware cleanup list. No uninstall implementation or cleanup was performed. Existing system services/accounts must be restored from prior backups, not deleted.
- Kept manifest/project at 0.3.0 and explicitly prohibited republishing this changed branch under the existing public identity. 0.3.1 is not prepared while production readback remains incomplete. Added exact inherited-branch commit inventory and scope notes to the changelog, verification, build status and checklist. Bonus statuses unchanged.
- `uv run pytest -q`: 339 passed in 23.68s ([output](../evidence/backend-polish-nov10/09-pytest.txt)). Fresh-clone source gate is next.

### 2026-11-10 16:56:30 IST — Fresh source gate and temporary native readback

- Fresh local Git clone at `76d9ef17f660d3d9ca9aa428257563055111fb51`, no application source mounts. Source IPM load compiled; activation first failed because Docker default network pools were exhausted. Resumed the same still-empty installed instance on a disjoint private /28 without deleting networks. Seven native classes / 22 methods passed; both recorded replays passed 12/12 (sessions 24 and 58). [Receipt](../evidence/backend-polish-nov10/fresh-source.json). No fresh model inference.
- Fresh-clone pytest passed 339 in 41.99s; TypeScript/build and 54 disconnected browser checks passed. Separately, updated network/test-source harness passed 373 pytest in 36.54s. The shell wrapper remains Docker-based, not Compose.
- Exact `submit` authorized temporary message-content/Event Log resources and SELECT on two tables in this instance only. Observed native References compact reply, provider metadata, routing INFO and investigation WARNING. Saved [native UI receipt](../evidence/backend-polish-nov10/11-native-ui.json). Restored exact role and verified both table grants absent: [restoration](../evidence/backend-polish-nov10/11-permissions-restored.json). No write/resend/control/password permissions added.
- Additional final-instance review verifier stopped after two environment-preparation errors; no cases created. [Blocked receipt](../evidence/backend-polish-nov10/fresh-review-blocked.json). Earlier upgrade review passed separately. Delivered-case screenshots remain missing, so 0.3.1 is not prepared.

### 2026-11-10 16:59:52 IST — Shell launcher repeated from a fresh local clone

- `./scripts/judge-replay.sh --api-port 53013 --container silentshift-bonus-registry-shell-final-nov10` completed at source `f9fc970b197e8c2830a784ede062a4485a18b7a2`. Public native 0.3.0 installed, production started, release-matched 5 classes / 12 methods passed, both recorded replays passed 12/12 (sessions 24 / 58). [Summary](../evidence/backend-polish-nov10/public-shell-summary.json), [output](../evidence/backend-polish-nov10/public-shell-output.txt). Automatic disjoint-subnet selection avoided the exhausted Docker default pool; no network was removed. This is not a new source-runtime gate or fresh inference.
- Existing OEX organizer threads, including their Spam-labelled messages if any, have no new response; last organizer reply remains Irene’s November 8 message. The November 10 queue-check email remains unanswered. No message sent.

### 2026-11-10 17:07:54 IST — Presentation bundle and final scope

- Five November 10 recorded-source captures added to the README and static candidate. Static page checked at 390px and 1440px: no horizontal overflow, seven images loaded, keyboard run anchor and no observed browser errors. Reduced-motion CSS present; OS emulation not performed. [Receipt](../evidence/voting-week-nov10/site-final-browser.json). No Pages publishing.
- One corrected OEX bundle replaces the older description-only target; its commit-addressed capture URLs must become public through an approved push before form preparation. No OEX save/Send action. Public readback still has the known stale body and public idea association; no new organizer reply. Broken OEX null-path image reported in the handoff, no email sent.
- Connected suite finished 12 passed / 4 failed for absent delivered/precedent cases. Kept failure output, no rerun or fixture injection. Ruff final whole-tree count 83, including three raw command-artifact findings; no CI lint gate. 0.3.1 remains unprepared. [Full report and exact gates](backend-polish-report.md).
- Updated the existing daily monitor with current branch/gate/bundle state, preserved schedule and notifications. Community visibility phase remains owner-handled. No external publication or spending.

### 2026-11-10 17:10:53 IST — Handoff checks

- Scoped local-link check passed for README, INSTALL, verification/checklist/build status, current OEX copy, static-site guide and final report; new evidence JSON parses. Diff whitespace check passed. No tracked file over 50 MiB and no tag exists. Pattern and configured-secret-value scans found no signals in the relevant changed text; this is a scoped check, not a comprehensive security audit.
- Stopped only the newly completed public-shell verification pair to reduce memory pressure; retained its containers, data and exported proof. Source UI/native instance remains running. No data/image/volume was deleted. Local main was not changed or pushed. Protected pre-existing UI edits and sealed-evaluation files remain untouched/uncommitted.

### 2026-11-10 17:26:07 IST — Approved branch push completed

- The owner’s exact `submit` consumed only the previously queued branch-push approval. Pushed `backend-polish-nov10` to `himanshu748/silentshift`, without force, at `08dad0bc2b1c3e9528388e87251a8aa6e5e51714`. Remote readback matches. Remote main remains `a10de3f61e1d809b374832a4db67761318bc16ea`; no main push.
- All five commit-addressed screenshot URLs in the prepared OEX bundle now return anonymous HTTP 200 with image/jpeg. This closes their public-asset prerequisite, not the OEX approval gate.
- No PR, merge, OEX save/submission, Pages deployment, tag/release, IPM publication, message or container deletion was performed. Protected uncommitted UI and sealed-evaluation work remains outside the push. This post-push log entry is local and uncommitted.

### 2026-11-10 17:33:16 IST — Voting-week finish, CI restored

- Owner authorized branch-only work/pushes and CI reruns; PR actions, main merge, OEX saves/approval, tags/releases, registry/Pages publication and communications remain individually gated. Re-ran latest main run 42569241885 and backend run 42811379567, attempt 2. Both executed steps: the old billing lock no longer blocks these attempts. Main completed successfully.
- Backend ran 373 Python checks: 372 passed, one failed because the default shallow checkout could not resolve frozen historical commit d1d752c. Preserved [failure log](../evidence/voting-finish-nov10/ci-backend-initial-failure.txt). Added fetch-depth: 0 to checkout; the baseline assertion and all checks remain unchanged. Local pytest: 373 passed in 20.89s ([output](../evidence/voting-finish-nov10/ci-checkout-fix-pytest.txt)).

### 2026-11-10 17:43:31 IST — CI green and safe lint cleanup

- Main attempt 2 and backend fix commit da2e9e9 both passed hosted Actions; [run metadata and counts](../evidence/voting-finish-nov10/ci-restored.json). No billing/settings or main code changes.
- Safe lint changes reduced findings from 83 to 40. Every remaining finding has a file/line/rule/reason in [the exception inventory](../RUFF_REMAINING.md); no blanket ignore or failing check suppression. Native runtime/policy/fixtures/raw evidence untouched. `uv run pytest -q`: 373 passed in 29.54s ([output](../evidence/voting-finish-nov10/safe-lint-pytest.txt)).

### 2026-11-10 17:48:38 IST — Real operator cases prepared; stale connected expectation found

- Fresh GitHub clone da2e9e9 source load on a new isolated 154U ARM64 container passed its full native suite and 5/5 live local-model scenarios. Case submission used the same authenticated Scenario Lab API as operators; no fabricated delivered state or precedent response was inserted. Installed synthetic reference catalog and source-bound native indexing are explicitly separate.
- Delivered amendment and actual retrieved precedents now exist. Connected browser pass reached 14/16; both remaining failures are the old exact prompt expectation 1.3.1 versus source/runtime 1.4.2. [Failure output](../evidence/voting-finish-nov10/connected-initial-failure.txt). Updated the exact expected version to match the checked-in Investigator parameter; no assertion was removed or relaxed. Added [setup instructions](../CONNECTED_CHECKS.md). A fresh-clone repeat follows.


### 2026-11-10 18:27:28 IST — Fresh verification gates and unpublished 0.3.1 prepared

- Main rerun and backend candidate CI execute and pass. Candidate source `7b3d5efafb07fd54530c912f6b9cdbb710462020`: 393 pytest locally in 31.29s; hosted 393 in 23.17s, types/build and 54 browser checks in 1.1m. No billing settings or main code changed.
- Fresh native source live Scenario Lab: 7 native classes / 22 methods and 5/5 final routes, raw proposals 3/5. Real approved amendment delivery and local vector matches supplied the missing connected setup. Fresh client suite passes 16/16 in 46.6s after the exact prompt expectation was aligned and the OOM-affected instance recovered. [All receipts](../evidence/voting-finish-nov10/candidate-031-summary.json).
- Captured actual Destination/Quarantine compact XML and both routing Event Logs; both temporary read windows were fully restored. Body version is the operation-time acknowledgment, not the later case version. No write/resend/control/password rights added.
- First Compose failed under VM OOM; serial attempt exposed a real read-only node_modules mount bug. Both retained. Fixed only the launcher, added a dedicated writable frontend volume and another-native-instance guard. Fresh GitHub source Compose passes 12/12, session 2, in 35.451s. Actual browser login and case/recorded-agent readback passed. No model call or hosted demo.
- Prepared module/project 0.3.1 and changelog only after the requested gates passed (Ruff uses the permitted per-finding inventory: 40 remain). Fresh source-load startup/native suite and both replays pass. Exported archive also installed from a local-filesystem repository in a second pristine container in 80.522s; it stayed empty/stopped, not a second API run or public registry proof. Public native IPM/OEX remain 0.3.0, React 0.2.1.
- GitHub clone paths and private configuration are sanitized in public receipts. Failed preflights/transports retained. Protected UI/sealed work untouched. No spending, deletion, PR action, main merge, tag/release, registry/Pages publication, OEX save or message. Organizer thread has no newer reply; duplicate follow-up not sent.
- Next approval is only opening the prepared draft backend PR. Later closures, OEX bundle, merge/release/publication and Pages remain separate gates; [report](backend-polish-report.md).

- 18:30:52 IST: after serial verification, stopped only the new completed test stacks without deleting data, then restored the earlier backend-final native/gateway pair at localhost:53003 to running. The new test containers/volumes and failed receipts are retained. Stopped this run's temporary Vite server on 5195. Local links/JSON/lint-inventory and configured-secret/session-capability scans passed; no tracked artifact exceeds 50 MiB.

### 2026-11-10 18:37:49 IST — Final pushed-tip readback (local handoff note)

- Remote backend-polish-nov10 is d0adca9fa4ef26fe176ae91c35d824924b3ffd7e; remote main remains a10de3f61e1d809b374832a4db67761318bc16ea. Latest hosted run 42821071803 succeeded at that exact tip; https://github.com/himanshu748/silentshift/actions/runs/42821071803. This post-push readback is local, so it does not trigger another documentation-only CI cycle. Native code qualification remains tied to 7b3d5ef.
- Four new native body/Event Log capture URLs read anonymously with HTTP 200 and JPEG signatures. Restored the earlier backend-final production to state 1/running; all new completed verification resources are stopped and retained. Protected UI/article/social/sealed work remains unchanged. No PR or external gated action performed.
- Refreshed the existing daily read-only monitor with current source/public/CI/gate facts, preserving schedule and notification preferences. The next exact submit approves only opening the prepared draft PR.

### 2026-11-10 18:42:07 IST — Updated judge-shipping order, PR gate prepared

- Read back remote main a10de3f and backend tip d0adca9. Tip Actions run 42821071803 is SUCCESS; PRs #3 and #2 remain open, no backend PR exists. No rerun was needed for the already-green tip.
- Phase 3H is already satisfied by the linked 393 pytest, 7 native classes/22 methods, two 12/12 replays, live 5/5, connected 16/16, body/Event Log captures, Compose and clean exported-archive installation. Retained the prepared 0.3.1 manifest under the latest instruction's exception; public IPM/OEX remain 0.3.0.
- Updated the prepared PR/report/runbook to the new order: PR approval, merge-commit approval, closure/deletion gates, then the OEX correction, followed by landing/demo work. No public gated action was taken. Made the guide target main after the intended merge and pinned PR evidence links to immutable d0adca9 so later branch deletion will not break those links. These are merge-ready documentation changes, not a fresh-main runtime claim.
- New landing and public replay requirements remain unimplemented and unverified. The semantic story must not become an unsupported transport-loss claim; a static recorded demo will be labeled and will not be called a native hosted-demo bonus. Protected UI/article/social/sealed work is untouched.

- 18:46:16 IST: shipping-order docs commit a77a5748dd3a261852a9b584bc8379a686b07c82 is pushed and its hosted run 42822539529 is SUCCESS. https://github.com/himanshu748/silentshift/actions/runs/42822539529. Native/test/harness/manifest files are unchanged since tested candidate 7b3d5ef; only merge-ready docs changed. Approval manifest/body and the immutable main-to-head comparison are prepared under ignored .local/shipping-phase1-nov10/. No PR opened, merge, closure, branch deletion, OEX save, Pages/demo deployment or spend occurred. This post-push readback is local to avoid another docs-only CI cycle.

### 2026-11-10 18:50:31 IST — Approved draft PR opened

- The exact submit approved only opening the prepared draft PR. Created https://github.com/himanshu748/silentshift/pull/4 through the GitHub connector as himanshu748, head a77a5748dd3a261852a9b584bc8379a686b07c82 → main a10de3f61e1d809b374832a4db67761318bc16ea. Target-side readback confirms OPEN/DRAFT and the approved body hash.
- Branch push CI 42822539529 was green before opening. PR-triggered checks are separate; no main merge, PR closure/comment, branch deletion, tag/release, IPM/Pages publish, OEX edit, hosting or spend was performed. Next gate is the reviewed merge-commit action; protected local work remains unchanged. This completion/readback note is local and uncommitted.

- PR #4 creation triggered GitGuardian check 129854912861, which failed with three Generic Password occurrences under incident 38253018. Read-only triage found only Compose required-variable expressions at compose.judge.yaml lines 7/9/10 in commit 2fc57f7; no embedded credential value. Check remains failed; nothing was ignored, dismissed or changed. Evidence is private .local/shipping-phase1-nov10/gitguardian-triage.json. PR test run 42823562245 was still running at initial readback. Merge gate is held until the check is resolved or explicitly reviewed; no merge approval is consumed.

### 2026-11-10 19:08:56 IST — GitGuardian false-positive remediation

- Owner authorized fixing the false positive and getting PR #4 green, then stopping before merge. GitGuardian extracted only the literal ?Set from required-value expressions. Verified all ten grouped contexts before classifying the single exact incident 38253018 as Ignored / Not a secret (false positive). No other source repository was modified, no scanner or check was disabled/skipped, no blanket ignore or history rewrite. Existing GitHub sign-in worked without new account, permissions or terms.
- Simplified the three password guards to standard required-value syntax, retaining rejection of unset/empty values. Startup validation for three distinct passwords of at least twelve characters remains unchanged. Real Compose config checks passed 7/7 without runtime creation or model calls; pytest passed 393 in 21.78s. [Report](gitguardian-pr4.md). Branch push and final hosted checks follow; no merge, readiness change, PR comment, deployment or publication.

### 2026-11-10 21:02:00 IST — Landing/demo task started; required stop at cloud preflight

- Created isolated local branch/worktree landing-demo-nov10 at verified remote main 9f3178e, preserving all original uncommitted work. Read the applicable engineering/design contract, existing site, README, Compose launcher, hosting review and video script. Applied motion-design and browser-recording guidance; no generated narration or provider calls.
- AWS Core read-only host inventory failed before API execution: UNAUTHORIZED / connection requires reauthentication. The supplied 32.193.44.79 also differs from Crashcart’s locally documented 52.202.25.181 URL. Honored the owner STOP-on-failure/ambiguity rule: no SSH or credential fallback, no site/host change or spending. Partial source audit is in landing-demo-nov10.md. No new page, screenshots/Lighthouse/recording, push/PR/merge, Pages/demo deployment, IPM/OEX/release edit or branch deletion.

### 2026-11-10 21:21:55 IST — Owner-authorized CLI Crashcart preflight

- AWS CLI works; confirmed correct new host crashcart-demo-nov10 / 32.193.44.79. Read-only, strictly pinned SSH reports x86_64 and 2 GiB-class RAM, with 1500553216 bytes available and no swap. Existing Caddy container uses 12.5 MiB; public root and static health return 200, root hash unchanged. No remote mutation, firewall change, container/image transfer or spending. Temporary local SSH keys removed.
- Stop: current verified SilentShift Compose/image is ARM64-only, so cohosting the verified native stack on this x86_64 host is not an as-is deploy. No unapproved emulation, image/build substitution or static fallback. New branch remains local at 9f3178e; landing, Lighthouse, screenshots/recording, push/PR and deployment remain unperformed. User must resolve native-image/host compatibility or explicitly change demo scope.

### 2026-11-10 22:03:08 IST — CLI landing candidate verified; publication stopped

- Owner explicitly requested independent CLI work after the host preflight. Built the isolated `landing-demo-nov10` static product page from main `9f3178e`; preserved the original checkout and its uncommitted work.
- Static browser checks 46/46; Python 393 in 24.44s; unchanged workbench suites 54 passed; TypeScript/build pass. Latest Lighthouse mobile 97/100/100/100, desktop 100/100/100/100. Earlier failures and repairs are retained.
- Created desktop/mobile captures and an actual 19.96s scroll recording. Added a manual-only, main-only Pages workflow; no dispatch or configuration change.
- Read-only Crashcart inspection confirms x86_64 versus the qualified ARM64 image; native deployment blocked. Root and healthz returned 200; no remote changes or spend. Public OEX is 0.3.1 but body still says native 0.3.0; fields untouched.
- Decision: prepare local commits and PR copy, then stop for exact `submit` to push/open the PR only. [Report](landing-demo-nov10.md); [quality](../evidence/landing-demo-nov10/quality.json); [tests](../evidence/landing-demo-nov10/tests.json).

### 2026-11-11 10:04:17 IST — Bonus claim evidence and video upload prepared

- Created isolated local branch `chore/bonus-claims-nov11` from public main `3bacc61`, preserving the existing landing worktree and original uncommitted work. Read the full official technology-bonuses post and discussion, including entrant claims and staff replies.
- Reclassified Embedded Python **usage** as Claimed under the owner's new explicit instruction: actual in-IRIS Language=python methods, production call sites and engine match the earlier native/live source hashes. The old exclusion was owner scope, not a technical failure. No new native/model test is implied. PEX, online demo and the Embedded Python bug remain Not claimed.
- Anonymous raw MP4: HTTP 200, 3,561,558 bytes, exact source SHA-256 match, 150.000 seconds with captions. Existing v0.3.1 has no assets. Prepared adding only that MP4 to the existing release; no upload or new tag. Public native IPM manifest is 0.3.1; the OEX body still has older 0.3.0 wording. Both articles are public and retain OEX backlinks; issue #17 remains open without comments/labels.
- Prepared a single README claim table, matching checklist/evidence updates, exact DC reply, and optional Java PEX effort/risk plan. No defensible second bug is filing-ready; historical signal-11 candidate remains unisolated. No post, message, OEX/IPM change, push/PR, merge, branch deletion or spending.
- Document validation: 370 relative links resolve; JSON parses, the readback script compiles, and whitespace validation passes. Local draft screenshots and [report](bonus-claims-nov11.md) are prepared. Next gate: one exact submit to push this branch and open the claims PR only.

- Refreshed the existing daily read-only monitor to the actual merged main/public 0.3.1/Pages baseline and the newly authorized local Embedded Python usage claim; preserved its schedule and gates. No duplicate automation or external communication.

## 11 November 2026 — Java PEX source work (IST)

- Created isolated branch `feat/java-pex-nov11` from main `1c92e095dcc2e9bc7493f1ad5e4a9b9355d78ec1`. Scope: append signed receipts after existing routing; no policy/veto changes, publishing or deployment.
- Started the existing local Colima profile. The preloaded ARM64 build 154U includes Temurin Java 11 and its PEX/JDBC SDK. No EAP image download or registry upload.
- Baseline source Compose launcher passed its unchanged keyless replay: `checks=12/12`, session `2`. This is recorded playback, not fresh inference.
- Read the official PEX guide and the bonus-linked pex-demo, plus Triage.Export and Readback's Java operation wiring. These establish an integration pattern; actual build-154 compatibility must be proved locally.
- Receipt design: RSA/SHA-256 signatures with per-instance private keys outside Git. Immutable files keyed by case/outcome/evidence fingerprint; retries reuse an original record, later human decisions append another record. Export failures must preserve the committed route.
- Public actions remain gated; online demo work has not started.
- First clean Compose build stopped before startup because the Dockerfile tried to create its JAR directory under `/opt` as irisowner. Corrected the image build to create/chown that directory as root, then return to irisowner before compiling/running. The failed log is retained privately. No routing test result was inferred from that failure.
- The next clean launch exposed a second, distinct Dockerfile issue: its inherited optional-source working directory was the read-only source mount, so iris-main could not create its startup log. Restored the vendor image's `/home/irisowner` working directory. This was container setup, not a PEX or policy assertion failure; both failed attempts remain retained and are not counted as passes.
- Clean IPM load stopped before application installation: the pinned installer was copied with host mode 600 and a different UID, so irisowner could not read it. Added a narrowly scoped owner correction for that copied installer in the test harness. This is not an app/PEX failure; no load/startup success is claimed for the blocked attempt.
- Clean source Compose passed both recorded replays (`12/12`, sessions 2 and 87), native 8 classes / 25 methods, including a real five-second stopped-exporter outage check. Authenticated Visual Trace session 87 shows Quarantine -> ReceiptExporter -> ExportResponse; no temporary portal permissions were added.
- A separate no-source-mount IPM container loaded/exported native 0.3.2 successfully. Docker's automatic address pools were exhausted, so network activation resumed with an inspected unused subnet. Startup and another complete native 8-class/25-method suite passed. The pinned approved-amendment embedding and local SDK warmup ran before the unchanged live five-case verifier.
- The owner clarified that 0.3.2 must remain unpublished. Public 0.3.1, main, OEX and all gated external actions remain untouched.
- **11:41 IST — STOP: real verification failure retained.** The explicit ObjectScript `RunFrozen` repeat returned `ERROR #5001: Frozen policy result changed`: 4/5 expected routes, while all five Java receipt checks passed. Approved-amendment case `74E6DF76-DD96-11F1-A2D3-A50F91B4F850` was held for review. Its model proposed ALLOW with only `contract:PO-2048:v2`; the unchanged `EVIDENCE_COMPLETE` gate denied release because required evidence citations were incomplete. The earlier unchanged API verifier passed 5/5. Neither result replaces the other.
- No model rerun, policy/prompt repair, weakened assertion or fresh archive-install attempt followed this real failure. The exported 0.3.2 archive was inspected, but its second pristine archive install remains unexecuted. Hosted branch CI is unexecuted because pushing remains gated. 0.3.2 is **not publish-ready**.
- The Java implementation executed on both sets of five cases; persisted hashes and signatures match the actual routes. Initial five signatures also passed independent OpenSSL verification. Native review exports retained REVIEW then DELIVERED/REJECTED records without overwriting the initial receipt. This establishes usage, not organizer qualification.
- Other observed checks: native 8 classes / 25 methods in source Compose and installed-source instances; two 12/12 keyless replays; 7 JUnit tests; 393 pytest; TS/build; 54 disconnected + 16 connected browser checks; 32 CSV browser checks; 54 native review assertions. Their exact scopes and outputs are retained in the new Java evidence.
