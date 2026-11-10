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
