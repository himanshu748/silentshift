# Submission checklist

Checked November 4, 2026. Submission deadline: **November 8 at 23:59:59 EST / November 9 at 10:29:59 IST**. [Contest 49](https://openexchange.intersystems.com/contest/49) lists SilentShift among its registered applications. **App/OEX release: 0.2.1; public native IPM: 0.2.0; verified IRIS: 2026.3.0AI.154.0 Community (154U), ARM64.** Verified means the linked behavior or publication was observed. **Organizer award: unconfirmed for every bonus.** Pending identifies an additional filing, visibility or eligibility gate; Not claimed means no bonus is requested for that item.

## Every bonus

| Bonus | Potential points | Status | Evidence and limit |
| --- | ---: | --- | --- |
| Questionnaire | 1 | Verified | [Submitted confirmation](assets/questionnaire-submitted.png); do not submit again |
| Java/.NET PEX | 3 | Not claimed | No Java or .NET production extension implemented |
| Native Workflow Engine | 2 | Verified | [54-check queue/concurrency receipt](evidence/review-queue.json), [actual UI approve/reject](evidence/review-ui.json) |
| Custom interoperability adapter | 2 | Verified | [82-check file-intake receipt](evidence/adapter.json), [walkthrough](PARTNER_INBOX.md) |
| Find a bug in AI Hub | 2 for first, +1 for second | Pending | [Quoted-method generator bug draft](bug-reports/ai-hub-quoted-tool-name.md) reproduced again on 154U; [compiler log](bug-reports/evidence/quoted-tool-build154.txt). User filing, vendor confirmation and organizer qualification remain pending |
| Embedded Python | 3 | Verified | [Fresh installed native five-case run](evidence/final-public-live.json); deterministic assessment and policy execute inside IRIS |
| IRIS Vector Search | 2 | Verified | [Native corpus/vector evidence](evidence/precedent-corpus.json), [critical-policy veto](evidence/precedent-veto.json); latest fresh run indexed an amendment with local embeddings |
| Docker | 2 | Verified | [Fresh official 154U install](evidence/final-public-live.json), no source mounts |
| Public IPM package | 2 | Verified | Literal `zpm "install silentshift"` passed in [fresh replay](evidence/final-public-replay.json) and [fresh live](evidence/final-public-live.json) containers; backend version 0.2.0 |
| Online demo | 2 | Not claimed | [EAP hosting restriction](HOSTING_REVIEW.md); no deployment or static mock claim |
| Community idea DPI-I-689 | 4 | Pending | Runtime tracing, replay, [native Body screenshots](evidence/provider-body-captures.json) and [Langfuse comparison](../README.md#silentshift-iris-interoperability-vs-langfuse) verified. Updated README/capture public. Dedicated field saved and visible to owner, but absent in a fresh signed-out Safari window; listing edits remain Awaiting Review. [Readback](evidence/public-visibility.json) |
| Find a bug in Embedded Python | 2 for first, +1 for second | Not claimed | [Historical callback crash candidate](bug-reports/callback-signal11-candidate.md) lacks a standalone repro and attribution; not a confirmed Python defect |
| First Developer Community article | 2 | Verified | [Public semantic-validation article](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production); body links SilentShift on OEX |
| Second Developer Community article | 1 | Verified | [Public recoverable-review article](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery); body links SilentShift on OEX |
| YouTube video | 3 | Verified | [Public demo](https://youtu.be/a4dOcqu89EA), [prior caption/1080p verification](evidence/submission-status.json); video URL present in the listing |

[Official criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). No awarded score or ranking is claimed. The native implementation remains **2026.3.0AI.154.0 (Build 154U), ARM64**. No newer runtime is declared tested or compatible.

## Final technical gate

**Current freeze-pass clean-clone gate: BLOCKED.** Two fresh GitHub clones were attempted. The first stopped at public-installer file permissions; the README correction is committed. The second stopped at the host disk floor before creating a container. No new clean install, native-suite pass or replay is claimed. [Commands and output](JUDGE_VERIFICATION.md). The retained-instance replay passed **12/12**, session **59**. The older successful gates below remain dated evidence, not a replacement for the blocked fresh-clone check.

- Fresh public install with the literal unqualified command, explicit production startup and full native `%UnitTest`: **5 classes / 12 methods passed** in each isolated container.
- No-key replay: **12/12 checks**, five paired provider exchanges, four real native tool reads, zero deliveries; session **24**, port **52823**.
- Fresh live local inference: **5/5 expected final routes**, all four native tools per case. Sessions **30, 58, 86, 113, 141**, port **52833**. One separate SDK warmup diagnostic and one local amendment embedding were excluded from the five-case score.
- Python: **174 passed in 5.74s**. Production frontend build passed. Browser: **38** landing/disconnected checks, **16** connected checks; final landing layout subset **6 passed in 17.7s**. [UI review](UI_REVIEW.md).
- Native runtime code and deterministic policy are unchanged; the frontend version is 0.2.1 and the separately installed native package remains 0.2.0.
- Native Visual Trace **Body** captures: success session **1667** and failure session **1807**, matched to persisted headers **1677** and **1810**. Both read-only inspectors passed. Both temporary read grants were removed and checked. [Capture receipt](evidence/provider-body-captures.json).

## Remaining actions — user only

1. **Apply the prepared OEX consistency edit when editing is available.** Use the [paste-ready description and exact field checklist](OPEN_EXCHANGE_COPY.md). Retain release **0.2.1**, native package **0.2.0**, the video/articles, checked **Submit to Contest** and checked IPM. Preserve DPI-I-689 in the dedicated field. Never cancel approval. After moderation, verify **Ideas to the app** while signed out; if still missing, ask OEX support to inspect the saved association. [Last public readback](evidence/public-visibility.json). No external edit was performed in this freeze pass.
2. **File the AI Hub bug.** Copy the [exact title/body and log](bug-reports/ai-hub-quoted-tool-name.md) into the [official contest bug tracker](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/new). Add the issue URL to the evidence after filing; do not change its status to confirmed until the vendor/organizer responds. Keep the signal-11 candidate separate.
3. **Articles and questionnaire need no duplicate submission.** Both articles are public and link OEX. The overview now distinguishes the current 192-token request budget from the 700-token ingress ceiling, with source links; the correction was saved in place and verified while signed out. Historical experiment results remain unchanged. [Correction receipt](evidence/article-clarification.json). Questionnaire confirmation is already retained.
4. **Hosting remains stopped.** Obtain written vendor confirmation or an eligible separately licensed runtime before reconsidering a public demo. No paid host, card, provider or new subscription was used.
