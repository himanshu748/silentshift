# Draft reply to Tatiana — not posted

Target: reply to Tatiana Tikhonova's downloadable-video reminder on the [technology-bonuses post](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows).

**Gate:** the release-asset URL below is proposed, not uploaded or verified yet. Post this text only after the claims PR is merged, the separately approved asset upload returns the expected full-file download/hash, and the owner gives another exact `submit` for this one comment. No claim below asserts awarded points.

---

Hi Tatiana,

SilentShift's demo MP4 can be downloaded here without signing in:
https://github.com/himanshu748/silentshift/releases/download/v0.3.1/silentshift-demo.mp4

It is the same captioned 2:30 video as [YouTube](https://youtu.be/a4dOcqu89EA). It demonstrates synthetic orders and simulator delivery, and predates the CSV addition.

For bonus review, here are the claims and supporting links:

- **Docker (2):** [Compose setup and native production](https://github.com/himanshu748/silentshift/blob/main/compose.judge.yaml).
- **IPM (2):** `zpm "install silentshift"`; [public 0.3.1 archive](https://pm.community.intersystems.com/download/silentshift/-/silentshift-0.3.1.tgz). The README separates the current manifest readback from the earlier public-install and source-install tests.
- **Workflow Engine (2):** [native Workflow coordinator](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Workflow/Coordinator.cls) and [approve/reject/concurrency execution](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/review-queue.json).
- **Custom adapter (2):** [PartnerJSON inbound adapter](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Adapter/PartnerJSON.cls) and [executed intake](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/adapter.json).
- **Vector Search (2):** [native VECTOR/cosine precedent retrieval](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Precedents.cls) and [corpus evidence](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/precedent-corpus.json).
- **Embedded Python (3):** [assessment and policy methods marked Language = python](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Bridge.cls#L22), called by the [native production process](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Process/Semantic.cls#L93).
- **Community idea DPI-I-689 (4):** [idea](https://ideas.intersystems.com/ideas/DPI-I-689), [Visual Trace recipe and Langfuse comparison](https://github.com/himanshu748/silentshift#community-idea-dpi-i-689-llm-tracing-with-interoperability). The dedicated association is visible on [Open Exchange](https://openexchange.intersystems.com/package/SilentShift); qualification remains pending.
- **First AI Hub bug (2):** [issue #17, with standalone reproduction and compiler output](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17); vendor and organizer confirmation remain pending.
- **First article (2):** [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production).
- **Second article (1):** [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery).
- **Video (3):** the downloadable MP4 above and the matching YouTube video.
- **Questionnaire (1):** already submitted; [retained confirmation](https://github.com/himanshu748/silentshift/blob/main/docs/assets/questionnaire-submitted.png).

The [README Contest bonuses table](https://github.com/himanshu748/silentshift#contest-bonuses) has the complete evidence map and limits. Our locally verified runtime is 2026.3.0AI.154.0 / 154U ARM64. We are not claiming an online demo, Java/.NET PEX or an Embedded Python bug.

Thank you for reviewing SilentShift.
