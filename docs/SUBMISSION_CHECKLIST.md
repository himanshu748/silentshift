# Submission checklist

Checked November 5, 2026. Submission deadline: **November 8 at 23:59:59 EST / November 9 at 10:29:59 IST**. [Contest 49](https://openexchange.intersystems.com/contest/49) lists SilentShift among its registered applications. **App/OEX release: 0.2.1; public native IPM: 0.2.0; verified IRIS: 2026.3.0AI.154.0 Community (154U), ARM64.** Verified means the linked behavior or publication was observed. **Organizer award: unconfirmed for every bonus.** Pending identifies an additional filing, visibility or eligibility gate; Not claimed means no bonus is requested for that item.

## Every bonus

| Bonus | Potential points | Status | Evidence and limit |
| --- | ---: | --- | --- |
| Questionnaire | 1 | Verified | [Submitted confirmation](assets/questionnaire-submitted.png); do not submit again |
| Java/.NET PEX | 3 | Not claimed | No Java or .NET production extension implemented |
| Native Workflow Engine | 2 | Verified | [54-check queue/concurrency receipt](evidence/review-queue.json), [actual UI approve/reject](evidence/review-ui.json) |
| Custom interoperability adapter | 2 | Verified | [82-check file-intake receipt](evidence/adapter.json), [walkthrough](PARTNER_INBOX.md) |
| Find a bug in AI Hub | 2 for first, +1 for second | Pending | [Quoted-method generator report](bug-reports/ai-hub-quoted-tool-name.md) reproduced on 154U and [filed as #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17); [readback receipt](evidence/ai-hub-bug-filed.json). Vendor confirmation and organizer qualification remain pending |
| Embedded Python | 3 | Not claimed | Not requested under the owner's November 5 instruction. [Native execution evidence](evidence/final-public-live.json) remains valid: deterministic assessment and policy execute inside IRIS |
| IRIS Vector Search | 2 | Verified | [Native corpus/vector evidence](evidence/precedent-corpus.json), [critical-policy veto](evidence/precedent-veto.json); the November 4 fresh live run indexed an amendment with local embeddings |
| Docker | 2 | Verified | [Fresh official 154U install](evidence/final-public-live.json), no source mounts |
| Public IPM package | 2 | Verified | Literal `zpm "install silentshift"` passed again in the [November 5 clean-clone run](evidence/judge-clean-clone.json), including production startup, full native suite and two replays; backend 0.2.0. [Earlier fresh live run](evidence/final-public-live.json) |
| Online demo | 2 | Not claimed | [EAP hosting restriction](HOSTING_REVIEW.md); no deployment or static mock claim |
| Community idea DPI-I-689 | 4 | Pending | Runtime tracing, [fresh-clone replay](JUDGE_VERIFICATION.md), [native Body screenshots](evidence/provider-body-captures.json) and [Langfuse comparison](../README.md#silentshift-iris-interoperability-vs-langfuse) verified. Dedicated field saved/read back; description edits sent for approval November 5. Owner status: Awaiting Review; anonymous association visibility unconfirmed. [Submission receipt](evidence/oex-submitted-nov5.json) |
| Find a bug in Embedded Python | 2 for first, +1 for second | Not claimed | [Historical callback crash candidate](bug-reports/callback-signal11-candidate.md) lacks a standalone repro and attribution; not a confirmed Python defect |
| First Developer Community article | 2 | Verified | [Public semantic-validation article](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production); body links SilentShift on OEX |
| Second Developer Community article | 1 | Verified | [Public recoverable-review article](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery); body links SilentShift on OEX |
| YouTube video | 3 | Verified | [Public demo](https://youtu.be/a4dOcqu89EA), [prior caption/1080p verification](evidence/submission-status.json); video URL present in the listing |

[Official criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). No awarded score or ranking is claimed. The native implementation remains **2026.3.0AI.154.0 (Build 154U), ARM64**. No newer runtime is declared tested or compatible.

## Final technical gate

**Current-main gate: VERIFIED for fresh clone e8e1e60 on November 5.** Public native 0.2.0, production startup, all five native test classes / 12 methods and two 12/12 replays passed at port **52893**, sessions **24** and **58**, with zero deliveries. Fresh-clone Python: **174 passed in 15.09s**. [Current receipt](evidence/judge-main-clean-clone.json).

**Earlier clean-clone gate: VERIFIED for 960b6b6 on November 5.** The unmodified README commands installed public native **0.2.0** into a fresh **154U** container without mounts, started production, passed **5 native test classes / 12 methods**, and passed two **12/12** API replays, sessions **24** and **58**, at port **52883**. Each replay executed four tools and five provider pairs and delivered nothing. Fresh-clone Python: **174 passed in 8.66s**; primary-checkout TypeScript and production build passed. No fresh inference was requested. [Commands, output and earlier failed attempts](JUDGE_VERIFICATION.md).

The following are earlier, separately retained gates; their live-model and browser results were not rerun for this documentation-only update:

- Fresh public install with the literal unqualified command, explicit production startup and full native `%UnitTest`: **5 classes / 12 methods passed** in each isolated container.
- No-key replay: **12/12 checks**, five paired provider exchanges, four real native tool reads, zero deliveries; session **24**, port **52823**.
- Fresh live local inference: **5/5 expected final routes**, all four native tools per case. Sessions **30, 58, 86, 113, 141**, port **52833**. One separate SDK warmup diagnostic and one local amendment embedding were excluded from the five-case score.
- Python: **174 passed in 5.74s**. Production frontend build passed. Browser: **38** landing/disconnected checks, **16** connected checks; final landing layout subset **6 passed in 17.7s**. [UI review](UI_REVIEW.md).
- Native runtime code and deterministic policy are unchanged; the frontend version is 0.2.1 and the separately installed native package remains 0.2.0.
- Native Visual Trace **Body** captures: success session **1667** and failure session **1807**, matched to persisted headers **1677** and **1810**. Both read-only inspectors passed. Both temporary read grants were removed and checked. [Capture receipt](evidence/provider-body-captures.json).

## Submitted actions and remaining external gates

1. **OEX consistency edit submitted.** The [product description](OPEN_EXCHANGE_COPY.md) was saved and sent for approval on November 5. Release **0.2.1**, native package **0.2.0**, video/articles, checked **Submit to Contest**, checked IPM and the dedicated idea URL were preserved and read back. [Receipt and screenshot](evidence/oex-submitted-nov5.json). No new release or approval cancellation occurred. The later signed-out check confirms the new description, but the **Ideas to the app** section is still absent and **Awaiting Review** remains visible. [Readback and proposed release-note correction](ENTRY_REVIEW.md). After moderation, verify the dedicated association again. If the association is still absent, ask OEX support to inspect the saved field. A pending review is not approval.
2. **AI Hub bug filed.** [Issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) is open under `himanshu748`; the body matches the prepared reproduction and evidence. [Filing receipt](evidence/ai-hub-bug-filed.json). Vendor confirmation and organizer qualification remain pending. Do not file a duplicate; keep the signal-11 candidate separate and unclaimed.
3. **Articles and questionnaire need no duplicate submission.** Both articles are public and link OEX. The overview now distinguishes the current 192-token request budget from the 700-token ingress ceiling, with source links; the correction was saved in place and verified while signed out. Historical experiment results remain unchanged. [Correction receipt](evidence/article-clarification.json). Questionnaire confirmation is already retained.
4. **Hosting remains stopped.** Obtain written vendor confirmation or an eligible separately licensed runtime before reconsidering a public demo. No paid host, card, provider or new subscription was used.
