# Submission checklist

Checked November 8, 2026 (UTC) for the local verification below. External publication and bonus statuses refer to their dated receipts; they were not refreshed in this run. Submission deadline: **November 8 at 23:59:59 EST / November 9 at 10:29:59 IST**. The [historical signed-out readback](evidence/entry-readback-nov5.json) records SilentShift on [Contest 49](https://openexchange.intersystems.com/contest/49). **App/OEX release: 0.2.1; public native IPM: 0.2.0; verified IRIS: 2026.3.0AI.154.0 Community (154U), ARM64.** Verified means the linked behavior or publication was observed. **Organizer award: unconfirmed for every bonus.** Pending identifies an additional filing, visibility or eligibility gate; Not claimed means no bonus is requested for that item.

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
| Docker | 2 | Verified | [Fresh official 154U install in this run](evidence/judge-current-nov8.json), no application source mounts; replay only |
| Public IPM package | 2 | Verified | Literal `zpm "install silentshift"` passed in the [current-main fresh-clone gate](evidence/judge-current-nov8.json), including startup, the full native suite and both replays. Installed native package remains 0.2.0; current-main CSV is separate |
| Online demo | 2 | Not claimed | [EAP hosting restriction](HOSTING_REVIEW.md); no deployment or static mock claim |
| Community idea DPI-I-689 | 4 | Pending | Runtime tracing, [fresh-clone replay](JUDGE_VERIFICATION.md), [native Body screenshots](evidence/provider-body-captures.json) and [Langfuse comparison](../README.md#silentshift-iris-interoperability-vs-langfuse) verified. [Dated field/submission receipt](evidence/oex-submitted-nov5.json) records the saved idea URL; [historical anonymous readback](evidence/entry-readback-nov5.json) did not show the dedicated association. No fresh portal check in this run; organizer qualification remains unconfirmed |
| Find a bug in Embedded Python | 2 for first, +1 for second | Not claimed | [Historical callback crash candidate](bug-reports/callback-signal11-candidate.md) lacks a standalone repro and attribution; not a confirmed Python defect |
| First Developer Community article | 2 | Verified | [Public semantic-validation article](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production); body links SilentShift on OEX. [Publication/backlink receipt](evidence/entry-readback-nov5.json) |
| Second Developer Community article | 1 | Verified | [Public recoverable-review article](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery); body links SilentShift on OEX. [Publication/backlink receipt](evidence/entry-readback-nov5.json) |
| YouTube video | 3 | Verified | [Public demo](https://youtu.be/a4dOcqu89EA), [prior caption/1080p verification](evidence/submission-status.json); video URL present in the listing |

[Official criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). No awarded score or ranking is claimed. The native implementation remains **2026.3.0AI.154.0 (Build 154U), ARM64**. No newer runtime is declared tested or compatible.

## Final technical gate

**Fresh public-package gate: VERIFIED for `df591420c06ed081623f6178804359ceb1686964` on November 8 (UTC).** The fresh GitHub clone includes the CSV and UI changes. Public native **0.2.0** installed on **154U ARM64**, production started, **5 native classes / 12 methods** passed, and both API replays passed **12/12**, sessions **24** and **58**, with **0 deliveries**. Fresh-clone Python: **207 passed in 14.21s**. [Current receipt](evidence/judge-current-nov8.json), [exact commands and elapsed times](JUDGE_VERIFICATION.md#current-main-repeat--november-8-2026-utc).

**Current-main CSV repeat: STOPPED at failed source-reload preparation.** The retained instance contained an untracked diagnostic class whose generated method failed compilation. The bootstrap exited **1**; no post-gate CSV or full live five-case rerun followed. Production was restored without deleting that diagnostic or changing native code. [Failure receipt](evidence/csv-current-nov8.json) and [compiler excerpt](evidence/csv-current-nov8-compiler.txt). This failure is separate from the passing clean public-package install.

The earlier same-turn UI finish passed **32 browser checks** using actual synthetic CSV uploads and local-model investigations. [Success observations](evidence/csv-ui-nov8-success.json), [bounded-rejection observations](evidence/csv-ui-nov8-rejection.json), [complete UI receipt](evidence/csv-ui-design-nov8.json). It precedes the fresh-clone gate and is not presented as the stopped repeat.

Earlier gates retain their original scope and dates: [historical clean-clone receipts](JUDGE_VERIFICATION.md#current-main-repeat--november-5-09040909-utc), [fresh live native run](evidence/final-public-live.json), [review and UI checks](UI_REVIEW.md), and [native message Body captures](evidence/provider-body-captures.json). These were not rerun after the source-reload failure. Current-main runtime changes are listed below; the earlier documentation-only freeze statement does not cover them.

## Submitted actions and remaining external gates

1. **No OEX edit or publication in this run.** The [dated submission receipt](evidence/oex-submitted-nov5.json) records the existing release, video, articles, contest selection and idea field. Its moderation observation is historical. Current approval and dedicated association visibility were not rechecked here; do not infer a new moderation state or send a duplicate support message from this checklist.
2. **AI Hub bug filed.** [Issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) is open under `himanshu748`; the body matches the prepared reproduction and evidence. [Filing receipt](evidence/ai-hub-bug-filed.json). Vendor confirmation and organizer qualification remain pending. Do not file a duplicate; keep the signal-11 candidate separate and unclaimed.
3. **Articles and questionnaire need no duplicate submission.** Both articles are public and link OEX. The overview now distinguishes the current 192-token request budget from the 700-token ingress ceiling, with source links; the correction was saved in place and verified while signed out. Historical experiment results remain unchanged. [Correction receipt](evidence/article-clarification.json). Questionnaire confirmation is already retained.
4. **Hosting remains stopped.** Obtain written vendor confirmation or an eligible separately licensed runtime before reconsidering a public demo. No paid host, card, provider or new subscription was used.

## Published vs main

Public native IPM **0.2.0** is unchanged. In this run, the downloaded public archive was compared byte for byte with Git commit [`d3637bb`](https://github.com/himanshu748/silentshift/commit/d3637bbe85812035e6258320c81af93305e95560): all archived files match that source snapshot. [Archive identity, file comparison and exact commit inventory](evidence/published-vs-main-nov8.json).

The fresh-clone verification covers current-main snapshot `df591420c06ed081623f6178804359ceb1686964` within the boundaries above: Python and released-package replay passed; the later CSV source reload failed. It does not turn unreleased source into a verified registry package. The module manifest still declares the published version; that is not proof that the CSV changes were published.

Code or asset changes after the published snapshot include the interactive landing/workbench (`770baab`), image optimization (`fbd3947`), bounded CSV/native intake (`09f71b7`), native CSV workbench (`ab00ecc`) and CSV presentation finish (`df59142`). The complete post-package commit list through the verified source snapshot is:

- [`9872451`](https://github.com/himanshu748/silentshift/commit/9872451dfd96e10dc6d3140b79d46097163cada9) docs: record public IPM verification and Open Exchange 0.2.0 release
- [`770baab`](https://github.com/himanshu748/silentshift/commit/770baabd2c5e317918003dde05986eed476a75ef) feat: add interactive product walkthrough and verify contest evidence
- [`cd4b37c`](https://github.com/himanshu748/silentshift/commit/cd4b37c986292eadc4a6177340cade232a3795fb) docs: record final verification and Open Exchange 0.2.1 status
- [`1c3941b`](https://github.com/himanshu748/silentshift/commit/1c3941b0e9a7a2cb28e3167bec28c1bb52e0c323) docs: capture native provider metadata and clarify trace access
- [`3dc3741`](https://github.com/himanshu748/silentshift/commit/3dc37416b718aec2857e582b8f317967bd5261a8) docs: record trace evidence submission and moderation status
- [`81d1ed4`](https://github.com/himanshu748/silentshift/commit/81d1ed4257fcb5f26ecd4a5bb31bab0199801464) docs: verify public trace evidence and reconcile contest status
- [`2f4f134`](https://github.com/himanshu748/silentshift/commit/2f4f13401f8e1c5c3756f1bfb8b9e7aa5c18a5b0) docs: clarify token budgets and finish the judge replay path
- [`6e490ac`](https://github.com/himanshu748/silentshift/commit/6e490ac613edd6d9b4b11919165ccb429d4bf93f) docs: reproduce AI Hub quoted-tool defect on build 154
- [`d389b84`](https://github.com/himanshu748/silentshift/commit/d389b84c612341236e27e9abb058ae11b5df77eb) docs: reverify judge replay on declared AI Hub build 154
- [`10927cc`](https://github.com/himanshu748/silentshift/commit/10927ccb5110565760657926bc06dbe64232bc8f) docs: make public idea evidence and keyless judge recipe prominent
- [`d116d73`](https://github.com/himanshu748/silentshift/commit/d116d735f577707a7b89b7c1cdc9fa1a819960b4) docs: align release copy and unconfirmed bonus claims
- [`37480de`](https://github.com/himanshu748/silentshift/commit/37480de32f4de8890c486a6974ea1e1ea7d4c56c) docs: make the verified IPM installer readable in fresh containers
- [`c92df33`](https://github.com/himanshu748/silentshift/commit/c92df33e0d44066e95c4bfb424676d2210ae4140) docs: record clean-clone failures and remaining disk gate
- [`ed27019`](https://github.com/himanshu748/silentshift/commit/ed270195b144987f9a7a9377aeaa920feb08c3ec) docs: require a Colima-shared checkout for the judge gateway
- [`960b6b6`](https://github.com/himanshu748/silentshift/commit/960b6b6445f8b1f0ef7aaaa8c409e7d036b07170) docs: save resumed verification results and stopping point
- [`ea19d6c`](https://github.com/himanshu748/silentshift/commit/ea19d6cdd00a30e45c41e8af55d0a906295655ab) docs: verify clean-clone judge replay on build 154
- [`1c4277a`](https://github.com/himanshu748/silentshift/commit/1c4277a1bad840830c36bfaf3ebf43824c55c24a) docs: align contest copy with verified judge path
- [`e8e1e60`](https://github.com/himanshu748/silentshift/commit/e8e1e60fded08d688c263bc9485fc7419c10f15b) docs: record AI Hub bug filing and OEX submission
- [`a99b6cd`](https://github.com/himanshu748/silentshift/commit/a99b6cdebecace3309869acbe97e8555c2178724) docs: verify current-main judge gate and signed-out listing
- [`acea23a`](https://github.com/himanshu748/silentshift/commit/acea23a03627dc16f2c5d2b31c5fb8e6acacf6c0) docs: sharpen judge walkthrough and link decision evidence
- [`0d96cc0`](https://github.com/himanshu748/silentshift/commit/0d96cc0168f987b1bcba28e7b9a74d3bc05bcf81) docs: record local checks and hosted CI startup blocker
- [`adba584`](https://github.com/himanshu748/silentshift/commit/adba584546ec8f39093d819efe1745bd65d8d5d6) docs: consolidate installation into a single human-readable guide
- [`fbd3947`](https://github.com/himanshu748/silentshift/commit/fbd39471f93dba94e007e405e8e00f008df224d6) chore: optimize images (ImgBot #1)
- [`09f71b7`](https://github.com/himanshu748/silentshift/commit/09f71b7c2896e7b27adbd2b539a0fcd1867741b8) fix: import bounded CSV orders through the native production
- [`ab00ecc`](https://github.com/himanshu748/silentshift/commit/ab00ecccd931bec1c9aa6f8a9efc9953b9c88560) feat: import CSV order feeds from the native workbench
- [`df59142`](https://github.com/himanshu748/silentshift/commit/df591420c06ed081623f6178804359ceb1686964) style(web): refine CSV intake and result comparisons

The verification evidence commits are also outside the published archive:

- [`36d5e35`](https://github.com/himanshu748/silentshift/commit/36d5e3597baaf7e397ee4d70a36f86ebc4996076) test: repeat public IPM judge gate from current-main clone
- [`03b8576`](https://github.com/himanshu748/silentshift/commit/03b85764442c2b17847890cb2e1b0471454e7871) docs: record CSV repeat blocked by retained diagnostic compilation

This checklist update and any later documentation-only commits are likewise unpublished. To include their exact hashes in the current branch inventory, run:

```sh
git log --reverse --format='%H %s' d3637bbe85812035e6258320c81af93305e95560..main
```

No release was tagged, package published, registry changed or Open Exchange listing edited in this run. The owner decides whether to publish a later package; a new OEX edit may go through moderation.
