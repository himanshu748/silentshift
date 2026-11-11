# Open Exchange — prepared 0.3.2 description correction

**Draft only: not saved or sent.** Native IPM/OEX **0.3.2** is already published; the separate source-built React workbench remains **0.2.1**. The saved listing body still says native 0.3.0. This bundle corrects that body and explains the Java exporter; it does not request another release or package publication.

Preserve the saved logo, DPI-I-689 association, IPM option/install command, existing contest registration, YouTube, MP4 and both article links. Leave Demo URL empty. Recheck the owner approval queue before editing; never cancel or duplicate a pending approval. OEX save/Send remains gated by a new exact **submit**. If correction requires a new release, stop rather than creating one.

The gallery below already exists on public main. Its November 10 recorded-replay scope stays unchanged. [Current publication proof](evidence/ipm-032-publication-nov11/publication.json).

## Fields to preserve

- Name: SilentShift
- Native version: 0.3.2 (already published; do not change the version)
- Repository: https://github.com/himanshu748/silentshift
- Video: https://youtu.be/a4dOcqu89EA
- Downloadable video: https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4
- Idea: https://ideas.intersystems.com/ideas/DPI-I-689
- IPM: checked; command `zpm "install silentshift"`
- Submit to Contest: preserve the existing registered selection; never untick

## Description body

### An order can arrive successfully and still be wrong
SilentShift is a validation workbench for integration operations teams running B2B order pipelines. It compares incoming business values with independently approved commitments, investigates discrepancies and gives the operator a reason, supporting records and a route for each case.
An order arrives as **20 CASE**. The approved contract says **240 EA**. The message is valid JSON, but there is no approved conversion. SilentShift holds it before the included destination simulator accepts it. An effective approved amendment authorizing **20 CASE** changes the outcome. The decisive difference is the governing evidence.
### Follow a case from intake to resolution
Open the investigation to compare the original message and selected reference, inspect the agent's actual evidence reads, and follow the final route. Eligible holds create native Workflow tasks. A reviewer supplies a reason and current version; recorded decisions can be resumed after a completion failure. A critical contradiction cannot be approved through the review screen.
The production accepts REST intake and ready JSON files through a custom inbound adapter. **Native IPM 0.3.2 includes bounded CSV intake and its parser.** Run the matching React workbench separately from repository source: preview an order feed against a separate approved-reference export, record the source under an explicitly authorized importer, then investigate each line. Repeating the same import recovers persisted cases and receipts. The frontend remains version 0.2.1 and is not installed by the native package. [CSV workflow and current captures](https://github.com/himanshu748/silentshift/blob/main/docs/CSV_IMPORT.md).
### The agent makes a recommendation inside the production
A native IRIS AI Hub agent reads four case-scoped evidence tools and recommends **ALLOW**, **QUARANTINE** or **REQUEST_REVIEW**, with citations and uncertainty. Automatic delivery needs a valid ALLOW recommendation, a resolved comparison and complete evidence. Deterministic policy owns the final route. Similar precedents inform the investigation; they do not replace current authority.
Each admitted provider exchange becomes a native request/response pair in the business case's Visual Trace. The messages expose model, provider, prompt version, timing, tool calls, outcome and available response usage. Unknown cost and provider retries remain null. [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689), the [reproducible example](https://github.com/himanshu748/silentshift#see-it-in-visual-trace) and [Langfuse comparison](https://github.com/himanshu748/silentshift#silentshift-iris-interoperability-vs-langfuse) explain the tracing design.
### Signed receipts after the routing decision
Native 0.3.2 adds a Java PEX business operation called after each committed routing outcome. It hashes the case, decision and evidence, then signs an immutable JSON receipt using an instance-held key. Retries reuse the original receipt and its saved investigation mode. An export failure is visible in the native trace and leaves the committed route unchanged. Signatures establish integrity under that key, not business correctness or a certified identity. [Java operation and limits](https://github.com/himanshu748/silentshift/blob/main/docs/JAVA_PEX.md) · [live case Visual Trace](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/bonus-claims-nov11/java-pex-live-trace.png).
### Inspect the recorded source workbench

These November 10 local captures show synthetic recorded replay on 154U ARM64, not new inference or a hosted app. The React interface is built separately from source and is not installed by the native IPM package.

![Original synthetic order](https://raw.githubusercontent.com/himanshu748/silentshift/main/docs/assets/voting-week-nov10/01-original-order.jpg)

![Incoming and approved values with the policy hold](https://raw.githubusercontent.com/himanshu748/silentshift/main/docs/assets/voting-week-nov10/02-policy-evidence.jpg)

![Recorded agent evidence and recommendation](https://raw.githubusercontent.com/himanshu748/silentshift/main/docs/assets/voting-week-nov10/03-native-agent.jpg)

![Native Workflow task with critical-case approval disabled](https://raw.githubusercontent.com/himanshu748/silentshift/main/docs/assets/voting-week-nov10/04-workflow-review.jpg)

![Persisted recorded provider metadata in native Visual Trace](https://raw.githubusercontent.com/himanshu748/silentshift/main/docs/assets/voting-week-nov10/07-provider-native-metadata.jpg)

### Run it locally or inspect the recorded journey
[Install from one guide](https://github.com/himanshu748/silentshift/blob/main/INSTALL.md). Fresh investigations use local Ollama and local embeddings, without a paid provider key. The optional keyless replay runs the native production with recorded provider responses and performs no fresh inference. Both paths require a separately obtained licensed IRIS image.
[Watch the captioned demo](https://youtu.be/a4dOcqu89EA) · [Download the MP4 without signing in](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4). The video demonstrates the earlier synthetic core workflow and predates CSV.
Read the technical articles: [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery).
**Open Exchange/native IPM 0.3.2; React workbench 0.2.1; tested runtime 2026.3.0AI.154.0 Community / 154U ARM64.** In a prepared namespace with IPM, the public native package installs with `zpm "install silentshift"`; account configuration and production startup are explicit setup steps. The 0.3.2 public archive was downloaded and its manifest/source inspected. A separately generated archive from the release tag passed a fresh offline installation with the application empty and stopped. The earlier public 0.3.0 install passed native tests and both recorded API replays; [the verification guide](https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_VERIFICATION.md) keeps those historical results separate from the newer archive, live-source and browser checks. No new public-registry 0.3.2 install is claimed. No newer build is claimed tested. All supplied examples are synthetic and delivery is per line to an IRIS simulator. There is no hosted demo, verified external ERP delivery, X12 support, whole-order completeness guarantee or production-readiness claim. Organizer bonus awards remain unconfirmed; [the checklist](https://github.com/himanshu748/silentshift/blob/main/docs/SUBMISSION_CHECKLIST.md) separates verified artifacts from pending qualification and Not claimed bonuses.
