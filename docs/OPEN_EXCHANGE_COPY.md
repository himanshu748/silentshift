# Open Exchange description and product copy

## November 9 public readback and prepared correction

The anonymous listing shows release **0.3.0**, its CSV release notes and the dedicated **Ideas to the app → DPI-I-689** association. Its description body still contains the older **0.2.0 / source-only CSV** sentences. That is a visible inconsistency, not proof that the replacement description has been approved. Organizer idea qualification and awards remain unconfirmed. [Public listing](https://openexchange.intersystems.com/package/SilentShift).

The replacement below is ready for owner review. Do not save another edit from this task: preserve Submit to Contest and existing approval. No new package version is published. Public native IPM remains **0.3.0**; the React workbench remains **0.2.1**. New provider configuration and the multi-page interface are source-branch changes and must not be presented as contents of the public native archive.

## Prepared 0.3.0 description — not resubmitted in this pass

This replacement was prepared after the public install passed. The November 9 anonymous readback still has legacy body text; approval of this complete replacement is **not confirmed**. No owner fields, approval state or contest selection were changed in this pass.

### An order can arrive successfully and still be wrong
SilentShift is a validation workbench for integration operations teams running B2B order pipelines. It compares incoming business values with independently approved commitments, investigates discrepancies and gives the operator a reason, supporting records and a route for each case.
An order arrives as **20 CASE**. The approved contract says **240 EA**. The message is valid JSON, but there is no approved conversion. SilentShift holds it before the included destination simulator accepts it. An effective approved amendment authorizing **20 CASE** changes the outcome. The decisive difference is the governing evidence.
### Follow a case from intake to resolution
Open the investigation to compare the original message and selected reference, inspect the agent's actual evidence reads, and follow the final route. Eligible holds create native Workflow tasks. A reviewer supplies a reason and current version; recorded decisions can be resumed after a completion failure. A critical contradiction cannot be approved through the review screen.
The production accepts REST intake and ready JSON files through a custom inbound adapter. **Native IPM 0.3.0 includes bounded CSV intake and its parser.** Run the matching React workbench separately from repository source: preview an order feed against a separate approved-reference export, record the source under an explicitly authorized importer, then investigate each line. Repeating the same import recovers persisted cases and receipts. The frontend remains version 0.2.1 and is not installed by the native package. [CSV workflow and current captures](https://github.com/himanshu748/silentshift/blob/main/docs/CSV_IMPORT.md).
### The agent makes a recommendation inside the production
A native IRIS AI Hub agent reads four case-scoped evidence tools and recommends **ALLOW**, **QUARANTINE** or **REQUEST_REVIEW**, with citations and uncertainty. Automatic delivery needs a valid ALLOW recommendation, a resolved comparison and complete evidence. Deterministic policy owns the final route. Similar precedents inform the investigation; they do not replace current authority.
Each admitted provider exchange becomes a native request/response pair in the business case's Visual Trace. The messages expose model, provider, prompt version, timing, tool calls, outcome and available response usage. Unknown cost and provider retries remain null. [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689), the [reproducible example](https://github.com/himanshu748/silentshift#see-it-in-visual-trace) and [Langfuse comparison](https://github.com/himanshu748/silentshift#silentshift-iris-interoperability-vs-langfuse) explain the tracing design.
### What the held-out comparison shows
On 48 frozen synthetic orders, rules-only produced **33/48** correct routes; agent + policy produced **33/48, 33/48 and 30/48** across three paired trials. Its wrong simulator deliveries were **2/23, 3/23 and 3/23**, versus six counterfactual baseline release choices. The reduction came with more false holds. **There was no overall correct-routing improvement and no unstructured-routing improvement: 1/16 for both per trial.** Five failed agent attempts remain counted. [Every failure and limitation](https://github.com/himanshu748/silentshift/blob/push/top3/docs/EVAL_HELDOUT.md). This source-branch comparison is not a new public package release or a population accuracy estimate.
The source workbench has separate public product pages and keeps its native case, review and CSV journeys. New provider configuration and frontend work belong to the source branch; they are not claimed as contents of the public native 0.3.0 archive. External provider service execution remains unverified.
### Run it locally or inspect the recorded journey
[Install from one guide](https://github.com/himanshu748/silentshift/blob/main/INSTALL.md). Fresh investigations use local Ollama and local embeddings, without a paid provider key. The optional keyless replay runs the native production with recorded provider responses and performs no fresh inference. Both paths require a separately obtained licensed IRIS image.
[Watch the captioned demo](https://youtu.be/a4dOcqu89EA) · [Download the MP4 without signing in](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [Current verification and commands](https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_VERIFICATION.md). The video demonstrates the earlier synthetic core workflow and predates CSV.
Read the technical articles: [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery).
**Open Exchange/native IPM 0.3.0; React workbench 0.2.1; tested runtime 2026.3.0AI.154.0 Community / 154U ARM64.** In a prepared namespace with IPM, the public native package installs with `zpm "install silentshift"`; account configuration and production startup are explicit setup steps. A fresh public 0.3.0 install passed the full native test suite and two recorded API replays; the linked verification guide separates those results from the live source and browser checks. No newer build is claimed tested. All supplied examples are synthetic and delivery is per line to an IRIS simulator. There is no hosted demo, verified external ERP delivery, X12 support, whole-order completeness guarantee or production-readiness claim. Organizer bonus awards remain unconfirmed; [the checklist](https://github.com/himanshu748/silentshift/blob/main/docs/SUBMISSION_CHECKLIST.md) separates verified artifacts from pending qualification and Not claimed bonuses.


## Historical listing copy and preparation

**Historical pre-publication note, November 8, 2026:** this document preserves the actual **approved 0.2.1 OEX listing copy** and its dated moderation evidence. The native `module.xml` is separately **prepared at 0.3.0**, **not** publicly published; last observed public native IPM was **0.2.0**. The new candidate does not alter the approved OEX text, video, idea field or any owner-side setting. Only the owner decides when to submit a new package release. [Release scope](../CHANGELOG.md) · [Owner-only steps](IPM.md#owner-only-030-publication-runbook) · [Completed native/browser candidate gate](evidence/candidate-030.json). After a 0.3.0 public release is independently confirmed, this section remains a historical copy of what was approved, not evidence that a newer OEX description was accepted.

## Historical preparation — superseded by publication

The native **0.3.0 source candidate is verified**, but publication is still the owner's decision. Use the [changelog](../CHANGELOG.md) and [OEX release steps](IPM.md#owner-only-030-publication-runbook). After an independently verified registry 0.3.0 install, change the current package paragraph to say that the native CSV backend is included in public 0.3.0, while the React workbench is built separately. Preserve the demo, both articles, DPI-I-689, Submit to Contest, IPM and every honest limit. No OEX edit was made in this preparation pass. The saved text below remains the historical public 0.2.0 state.

## Earlier approved description — November 8, 2026 (UTC)

Saved through **Save → Send for approval → Send edits**, without creating a release. Open Exchange confirmed submission, then emailed approval at **08:26 UTC**. The new description is visible anonymously. Release **0.2.1**, native IPM **0.2.0**, contest/IPM selections, dedicated idea URL, video and both article fields were retained; Demo URL stays empty. [Submission and mail receipt](evidence/oex-update-nov8.json) · [owner screenshot](evidence/oex-update-nov8-owner.jpg).

The owner page shows **Ideas to the app** with DPI-I-689. Anonymous retrieved text still lacks that dedicated section, although the description links the idea, Visual Trace recipe and Langfuse comparison. The Open Exchange team has been sent the downloadable demo and asked to confirm the 4-point idea qualification. No awarded points or organizer acknowledgement is asserted.

An automatic IPM notification followed the description-only submission: `ERROR #5001: Version 0.2.0 of Package silentshift is already published`. No new package version was requested. A subsequent [streamed public archive check](evidence/oex-update-nov8-ipm.json) returned the identical existing package. The email asks whether corrective action is needed without requesting another publication.

Short description (within the editor's limit):

> Catch wrong business meaning in B2B orders before delivery.

## Full description — saved November 8

### An order can arrive successfully and still be wrong

SilentShift is a validation workbench for integration operations teams running B2B order pipelines. It compares incoming business values with independently approved commitments, investigates discrepancies and gives the operator a reason, supporting records and a route for each case.

An order arrives as **20 CASE**. The approved contract says **240 EA**. The message is valid JSON, but there is no approved conversion. SilentShift holds it before the included destination simulator accepts it. An effective approved amendment authorizing **20 CASE** changes the outcome. The decisive difference is the governing evidence.

### Follow a case from intake to resolution

Open the investigation to compare the original message and selected reference, inspect the agent's actual evidence reads, and follow the final route. Eligible holds create native Workflow tasks. A reviewer supplies a reason and current version; recorded decisions can be resumed after a completion failure. A critical contradiction cannot be approved through the review screen.

The production accepts REST intake and ready JSON files through a custom inbound adapter. **Current GitHub source also includes a bounded CSV workbench:** preview an order feed against a separate approved-reference export, record the source under an explicitly authorized importer, then investigate each line. Repeating the same import recovers persisted cases and receipts. CSV is source-only and is **not included in public native IPM 0.2.0**. [CSV workflow and current captures](https://github.com/himanshu748/silentshift/blob/main/docs/CSV_IMPORT.md).

### The agent makes a recommendation inside the production

A native IRIS AI Hub agent reads four case-scoped evidence tools and recommends **ALLOW**, **QUARANTINE** or **REQUEST_REVIEW**, with citations and uncertainty. Automatic delivery needs a valid ALLOW recommendation, a resolved comparison and complete evidence. Deterministic policy owns the final route. Similar precedents inform the investigation; they do not replace current authority.

Each admitted provider exchange becomes a native request/response pair in the business case's Visual Trace. The messages expose model, provider, prompt version, timing, tool calls, outcome and available response usage. Unknown cost and provider retries remain null. [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689), the [reproducible example](https://github.com/himanshu748/silentshift#see-it-in-visual-trace) and [Langfuse comparison](https://github.com/himanshu748/silentshift#silentshift-iris-interoperability-vs-langfuse) explain the tracing design.

### Run it locally or inspect the recorded journey

[Install from one guide](https://github.com/himanshu748/silentshift/blob/main/INSTALL.md). Fresh investigations use local Ollama and local embeddings, without a paid provider key. The optional keyless replay runs the native production with recorded provider responses and performs no fresh inference. Both paths require a separately obtained licensed IRIS image.

[Watch the captioned demo](https://youtu.be/a4dOcqu89EA) · [Download the MP4 without signing in](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [Current verification and commands](https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_VERIFICATION.md). The video demonstrates the earlier synthetic core workflow and predates CSV.

Read the technical articles: [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery).

**App/workbench 0.2.1; public native IPM 0.2.0; tested runtime 2026.3.0AI.154.0 Community / 154U ARM64.** In a prepared namespace with IPM, the public native package installs with `zpm "install silentshift"`; account configuration and production startup are explicit setup steps. No newer build is claimed tested. All supplied examples are synthetic and delivery is per line to an IRIS simulator. There is no hosted demo, verified external ERP delivery, X12 support, whole-order completeness guarantee or production-readiness claim. Organizer bonus awards remain unconfirmed; [the checklist](https://github.com/himanshu748/silentshift/blob/main/docs/SUBMISSION_CHECKLIST.md) separates verified artifacts from pending qualification and Not claimed bonuses.

## Historical submission — November 5

**Saved and sent for approval on November 5, 2026.** App/workbench release **0.2.1**, public native IPM **0.2.0**, verified runtime **2026.3.0AI.154.0 Community, ARM64 (154U)**. The custom Markdown description below replaced README import and was read back after reload. Contest/IPM selections, dedicated DPI-I-689 URL, video and both articles were preserved. No new release was created and no approval was cancelled. [Receipt](evidence/oex-submitted-nov5.json) · [confirmation screenshot](assets/oex-submitted-nov5.png).

The November 5 signed-out browser check showed the submitted description, **Awaiting Review**, and the idea link in the description. The dedicated **Ideas to the app** section is absent. Public description visibility does not establish moderator approval. The AI Hub bug is [filed as #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17), with no replies at this check; it is not vendor-confirmed or awarded. DC articles were unchanged.

## Fields to retain or correct

| Field | Value |
| --- | --- |
| App name | SilentShift |
| App release | 0.2.1 |
| Short description | Catch wrong business meaning before delivery: native IRIS AI Hub investigation, deterministic policy and recoverable human review. |
| Repository | https://github.com/himanshu748/silentshift |
| Ideas Portal link — dedicated field | https://ideas.intersystems.com/ideas/DPI-I-689 |
| YouTube | https://youtu.be/a4dOcqu89EA |
| Native IPM package | silentshift 0.2.0; `zpm "install silentshift"` |
| Submit to Contest | Keep checked for contest 49 |
| Publish in Package Manager | Keep checked; do not relabel native 0.2.0 as 0.2.1 |
| Demo URL | Empty; online demo Not claimed |
| Article one | https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production |
| Article two | https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery |

## Historical full description — submitted text

### Catch wrong business meaning before delivery

An order arrives as **20 CASE**. Its approved contract says **240 EA**. The JSON is valid, but no approved conversion explains the change. SilentShift holds the order before the included destination simulator accepts it, then gives the integration operator the original message, contract and reason in one investigation.

The same incoming value can be legitimate: an effective approved amendment authorizing **20 CASE** lets it proceed. A native IRIS AI Hub agent investigates independent reference records through four read-only tools. Deterministic Embedded Python policy makes the final routing decision. Similar precedents add context; they cannot override the current contract or release a critical contradiction.

Operators can compare payload and reference values, inspect the agent's actual reads, follow the native trace, and resolve eligible holds through a recoverable Workflow review. Review decisions require a reason and a current version. Critical contradictions retain their release veto; concurrent identical approvals produce one simulator receipt. A custom inbound adapter brings ready files into the same production as REST intake.

### See every model exchange in its business context

SilentShift implements [Community Idea DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689): every admitted provider exchange becomes a native request/response pair in the case's interoperability session. Visual Trace exposes model, provider, prompt version, forwarding duration, tool names, HTTP outcome and returned usage when available. Unknown cost and provider retries remain null. Recorded replay explicitly omits current token usage because it performs no new inference.

The [README's keyless judge recipe](https://github.com/himanshu748/silentshift#see-it-in-visual-trace) installs the public native package, starts the real production, runs its native tests and replays the unsupported-unit order through the actual agent and tools. It prints the case session and Visual Trace URL. The [November 5 fresh-clone check](https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_VERIFICATION.md) passed public installation, production startup, all five native test classes / 12 methods and two 12-check replays. Both orders stayed held with zero deliveries. No provider key or fresh inference was used. This requires a locally available licensed build-154 image; it is not a hosted demo. Inspect the [native message-body screenshots](https://github.com/himanshu748/silentshift#native-provider-metadata) and the [comparison with Langfuse](https://github.com/himanshu748/silentshift#silentshift-iris-interoperability-vs-langfuse), including Langfuse's strengths in evals, dashboards and prompt management.

### Run or watch

**App/workbench: 0.2.1. Public native IPM package: 0.2.0. Verified runtime: InterSystems IRIS Community AI Hub 2026.3.0AI.154.0, ARM64 (154U).** No newer runtime is declared verified. In a prepared namespace with IPM, install the native backend with:

```objectscript
zpm "install silentshift"
```

[Installation and explicit production setup](https://github.com/himanshu748/silentshift/blob/main/docs/IPM.md) · [Source and README](https://github.com/himanshu748/silentshift) · [Captioned 1080p demo video](https://youtu.be/a4dOcqu89EA)

Read the technical articles: [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery).

### Evidence and contest status

Native Workflow, the custom adapter, Embedded Python, IRIS Vector Search, Docker, public IPM installation, both articles, the video and the questionnaire have recorded execution or publication evidence. **All organizer bonus awards remain unconfirmed.** DPI-I-689 implementation evidence is public; the dedicated OEX association remains pending public visibility at the last check. One AI Hub generator defect reproduces on build 154U and is [filed as issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17); vendor confirmation and organizer qualification remain pending. **Online demo, Java/.NET PEX and an Embedded Python bug bonus are Not claimed.** The [bonus checklist](https://github.com/himanshu748/silentshift/blob/main/docs/SUBMISSION_CHECKLIST.md) links each claim to its evidence.

All examples use synthetic data and an IRIS destination simulator. Recorded replay proves native orchestration and policy behavior, not fresh inference or model accuracy. Separate live local-Ollama evidence retains five expected final routes. No real ERP/bank delivery, production readiness or awarded score is asserted.

## Historical submission receipt and next check

1. Open Exchange confirmed **saved successfully**, then **sent for approval successfully** through **Send for approval → Send edits**. The update changed the description only; app 0.2.1 and native package 0.2.0 were retained.
2. After reload, the description matched this copy and **Submit to Contest**, **Publish in Package Manager**, DPI-I-689, video and both article fields retained their expected values. The online demo URL is empty.
3. The signed-out listing displays the new description and **Awaiting Review**, but no dedicated **Ideas to the app** section. Wait for moderation; never click **Cancel approval**. If the association is still missing after approval, ask OEX support to inspect the saved field. No OEX edit was made during this check.
4. The November 4 published release notes remain a historical snapshot; their draft-bug statement predates the November 5 filing. The submitted current description links the filed issue. No new release was created just to rewrite that history.

**Developer Community and questionnaire:** no duplicate submissions or edits are needed. **AI Hub bug:** [issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) is already filed; wait for vendor triage and organizer qualification. The historical callback-crash candidate remains unready and unclaimed.
