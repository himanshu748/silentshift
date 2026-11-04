# Submission checklist

Checked November 4, 2026. Submission deadline: **November 8 at 23:59:59 EST / November 9 at 10:29:59 IST**. [Contest 49](https://openexchange.intersystems.com/contest/49) lists SilentShift among its registered applications. Verified means the linked behavior or publication was observed; it does not mean organizers awarded the points.

## Every bonus

| Bonus | Potential points | Status | Evidence and limit |
| --- | ---: | --- | --- |
| Questionnaire | 1 | Verified | [Submitted confirmation](assets/questionnaire-submitted.png); do not submit again |
| Java/.NET PEX | 3 | Not claimed | No Java or .NET production extension implemented |
| Native Workflow Engine | 2 | Verified | [54-check queue/concurrency receipt](evidence/review-queue.json), [actual UI approve/reject](evidence/review-ui.json) |
| Custom interoperability adapter | 2 | Verified | [82-check file-intake receipt](evidence/adapter.json), [walkthrough](PARTNER_INBOX.md) |
| Find a bug in AI Hub | 2 for first, +1 for second | Pending | [Quoted-method generator bug draft](bug-reports/ai-hub-quoted-tool-name.md) reproduced on 154U; not filed or vendor-confirmed |
| Embedded Python | 3 | Verified | [Fresh installed native five-case run](evidence/final-public-live.json); deterministic assessment and policy execute inside IRIS |
| IRIS Vector Search | 2 | Verified | [Native corpus/vector evidence](evidence/precedent-corpus.json), [critical-policy veto](evidence/precedent-veto.json); latest fresh run indexed an amendment with local embeddings |
| Docker | 2 | Verified | [Fresh official 154U install](evidence/final-public-live.json), no source mounts |
| Public IPM package | 2 | Verified | Literal `zpm "install silentshift"` passed in [fresh replay](evidence/final-public-replay.json) and [fresh live](evidence/final-public-live.json) containers; backend version 0.2.0 |
| Online demo | 2 | Not claimed | [EAP hosting restriction](HOSTING_REVIEW.md); no deployment or static mock claim |
| Community idea DPI-I-689 | 4 | Pending | Runtime tracing, replay, [native Body screenshots](evidence/provider-body-captures.json) and [Langfuse comparison](../README.md#silentshift-iris-interoperability-vs-langfuse) verified. Dedicated field saved and visible in owner view. Release 0.2.1/README are visible anonymously; the dedicated idea association is absent from that extract and listing edits remain Awaiting Review |
| Find a bug in Embedded Python | 2 for first, +1 for second | Not claimed | [Historical callback crash candidate](bug-reports/callback-signal11-candidate.md) lacks a standalone repro and attribution; not a confirmed Python defect |
| First Developer Community article | 2 | Verified | [Public semantic-validation article](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production); body links SilentShift on OEX |
| Second Developer Community article | 1 | Verified | [Public recoverable-review article](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery); body links SilentShift on OEX |
| YouTube video | 3 | Verified | [Public demo](https://youtu.be/a4dOcqu89EA), [prior caption/1080p verification](evidence/submission-status.json); video URL present in the listing |

[Official criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). No awarded score or ranking is claimed. The native implementation remains **2026.3.0AI.154.0 (Build 154U), ARM64**. Organizers also accept **2027.1.0AI.109.0 Community**, which was not tested here.

## Final technical gate

- Fresh public install with the literal unqualified command, explicit production startup and full native `%UnitTest`: **5 classes / 12 methods passed** in each isolated container.
- No-key replay: **12/12 checks**, five paired provider exchanges, four real native tool reads, zero deliveries; session **24**, port **52823**.
- Fresh live local inference: **5/5 expected final routes**, all four native tools per case. Sessions **30, 58, 86, 113, 141**, port **52833**. One separate SDK warmup diagnostic and one local amendment embedding were excluded from the five-case score.
- Python: **174 passed in 5.74s**. Production frontend build passed. Browser: **38** landing/disconnected checks, **16** connected checks; final landing layout subset **6 passed in 17.7s**. [UI review](UI_REVIEW.md).
- Native runtime code and deterministic policy are unchanged; the frontend version is 0.2.1 and the separately installed native package remains 0.2.0.
- Native Visual Trace **Body** captures: success session **1667** and failure session **1807**, matched to persisted headers **1677** and **1810**. Both read-only inspectors passed. Both temporary read grants were removed and checked. [Capture receipt](evidence/provider-body-captures.json).

## Remaining actions

1. **Finish OEX moderation/idea-field public readback.** Release **0.2.1** appears under Published releases and in anonymous retrieval, with two articles, retained video and install command. The later native Body screenshots from commit **1c3941b** are visible in the owner preview and were sent as description edits; anonymous retrieval still shows the preceding description. Native registry **0.2.0** remains unchanged. The owner still sees **Awaiting Review** and the dedicated idea association; anonymous extraction omits that association, so that public-field gate remains pending. Submit to Contest and IPM remained checked; no approval was cancelled. [Final receipt](FINAL_PASS_REPORT.md).
2. **File the reproducible AI Hub bug if you choose.** Review the draft and two tiny repro classes, then file through the official AI Hub issue channel. No issue was filed by the agent. Keep the historical signal-11 candidate separate until it has a minimal reproducer and stack attribution.
3. **Articles and questionnaire need no duplicate submission.** Both articles are public and link OEX. Their recorded experiments remain historical; the first article's recorded 700-token wording predates the current 192-token setting. A current-configuration correction can be applied by the author. Questionnaire confirmation is already retained.
4. **Hosting remains stopped.** Obtain written vendor confirmation or an eligible separately licensed runtime before reconsidering a public demo. No paid host, card, provider or new subscription was used.
