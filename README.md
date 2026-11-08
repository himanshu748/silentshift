# SilentShift

**Catch wrong business meaning before delivery.**

SilentShift is a validation workbench for integration operations teams running B2B order pipelines. It compares incoming orders with independently approved commitments and gives each held line an inspectable reason and a review path.

An order arrives as `20 CASE`. Its approved contract says `240 EA`. The JSON is valid, but no approved conversion explains the change. SilentShift holds the order and shows the operator the incoming value, the approved reference and the reason.

If an effective approved amendment authorizes `20 CASE`, the demonstrated workflow allows it. In the workbench, the operator follows the original message, governing reference, evidence reads and final route in one case. Eligible holds go to a reviewer; critical contradictions require corrected input or approved authority and a new investigation.

A native IRIS AI Hub agent recommends a disposition with evidence citations and uncertainty. Automatic delivery requires a valid `ALLOW` recommendation as well as a resolved comparison and complete evidence. Deterministic policy retains the final authority and critical-release veto.

**[Install SilentShift](INSTALL.md)** · [Watch the captioned demo](https://youtu.be/a4dOcqu89EA) · [Download MP4](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [Open Exchange](https://openexchange.intersystems.com/package/SilentShift)

<a id="native-build-154-setup"></a>
## Installation

Follow **[INSTALL.md](INSTALL.md)** for the complete installation in one file: obtain and load the licensed image, create private local credentials, prepare the local model, bootstrap IRIS, then start the workbench and investigate an order.

| What you want to do | Installation path | Model requirement |
| --- | --- | --- |
| Run new investigations and CSV imports | [Full local installation](INSTALL.md) | Local Ollama, Qwen and local embeddings; no paid provider key |
| Check native orchestration without a model | [Keyless replay](INSTALL.md#optional-check-without-a-model) | No Ollama needed; recorded provider responses, no fresh inference |

The verified native environment is **macOS/ARM64 with IRIS Community AI Hub 2026.3.0AI.154.0 (154U)**. App/workbench: **0.2.1**. Last verified **public** native IPM: **0.2.0**. The current source manifest prepares native IPM **0.3.0, not yet published or registry-installed**. [0.3.0 release notes](CHANGELOG.md) · [Owner publication instructions](docs/IPM.md#owner-only-030-publication-runbook). The proprietary runtime must be obtained separately; no newer build is claimed tested.

## Community Idea DPI-I-689: LLM tracing with Interoperability

SilentShift implements [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) by recording each admitted AI Hub provider exchange as a native request/response pair in its business-case session. The trace records model, provider, prompt version, timing, tool names, outcome and available response-token usage. Unknown cost and provider retries stay null; replay does not report recorded tokens as new usage.

### See it in Visual Trace

Use the **optional keyless replay** in [INSTALL.md](INSTALL.md#optional-check-without-a-model). It installs the public package into a separate container and prints a Visual Trace URL. [How to read the trace](docs/FEATURES.md#see-it-in-visual-trace).

### Native provider metadata

[Inspect the successful native Body capture](docs/assets/provider-success-body-safari.png) and the [failure capture](docs/assets/provider-failure-body-safari.png). They show retained live calls, not simulated portal screens. [Field map, values and limits](docs/FEATURES.md#native-provider-metadata).

### SilentShift (IRIS Interoperability) vs Langfuse

SilentShift connects model exchanges to native business messages and human review. Langfuse offers dedicated LLM evaluation, dashboards and prompt-management workflows. [Read the full comparison](docs/FEATURES.md#silentshift-iris-interoperability-vs-langfuse).

The idea implementation is verified locally; organizer qualification and the dedicated OEX association's public visibility remain pending. No awarded points are claimed.

<a id="local-checks-without-iris"></a>
<a id="prove-the-native-journey"></a>
<a id="optional-local-intake-and-procedural-guidance"></a>
## Explore the application

[Features and technical reference](docs/FEATURES.md) covers evidence inspection, Workflow review, vector precedents, partner-file intake, API examples and developer checks. [Judge walkthrough](docs/JUDGE_GUIDE.md) connects those features to recorded execution evidence.

[Import a CSV order feed from the workbench](docs/CSV_IMPORT.md): preview incoming lines against a separate approved export, then investigate them in the native production. This feature requires explicit importer permission. It was not in the last verified public IPM **0.2.0**; the **prepared, unpublished 0.3.0 native package** includes its IRIS backend/parser. The TypeScript CSV workbench remains a **separate source-built frontend**, not something installed by `zpm "install silentshift"` alone. After owner publication, verify the registry version and a fresh install before changing the public-package claim.

All supplied examples are synthetic and deliver only to an IRIS simulator. There is no hosted demo or verified external ERP/bank delivery. [Verification results](docs/JUDGE_VERIFICATION.md) · [Bonus status](docs/SUBMISSION_CHECKLIST.md).

## Developer Community articles

- [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production)
- [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery)

## License

Source: [MIT](LICENSE). The proprietary InterSystems runtime is separately licensed and excluded. [Dependencies and attribution](docs/FEATURES.md#license-and-attribution).
