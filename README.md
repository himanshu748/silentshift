# SilentShift

**Find the business contradiction behind a successful integration.**

SilentShift helps integration operations teams inspect B2B orders against independently approved commitments before delivery. An order says **20 CASE**; its contract says **240 EA**. The message passes technical validation, but no approved conversion authorizes the change. The operator sees the two values, their sources and a held order with no simulator delivery. An effective approved amendment authorizing **20 CASE** changes the outcome.

The investigation runs inside InterSystems IRIS Interoperability. Native AI Hub reads case-scoped evidence and recommends a route. Deterministic policy retains the final authority; eligible holds go to native Workflow review, while critical contradictions cannot be approved.

**[Install from one guide](INSTALL.md)** · [Watch the captioned demo](https://youtu.be/a4dOcqu89EA) · [Open Exchange](https://openexchange.intersystems.com/package/SilentShift)

The app runs locally. There is no hosted demo. The video records the earlier core workflow and predates the new workbench and CSV importer.

![The source-built SilentShift home page with an interactive, explicitly synthetic order comparison](evidence/browser/top3-multipage/home-light-desktop.png)

## What the held-out comparison showed

- On **48 frozen synthetic orders**, rules-only produced **33/48** correct routes; agent + policy produced **33/48, 33/48 and 30/48** across three trials.
- Rules recommended releasing **6/23** release-ineligible orders. The shipped arm made **2/23, 3/23 and 3/23 actual wrong simulator deliveries**, with more false holds: **9/25, 9/25 and 12/25**, versus the baseline's **9/25**.
- **Agent + policy did not improve correct routing in the unstructured split: 1/16 for both in every trial.** Five failed agent attempts remain counted. This does not establish an overall AI accuracy improvement.

[Every result, failure, timing and rules win](docs/EVAL_HELDOUT.md) · [Frozen labels and protocol](fixtures/v2-heldout/FROZEN.md) · [Raw native observations](evidence/heldout/summary.json). Baseline releases are counterfactual choices; only the shipped arm executed simulator deliveries. The same cases repeat across trials and are not independent production orders.

<a id="native-build-154-setup"></a>
<a id="installation"></a>
## The short judge path

Follow [INSTALL.md](INSTALL.md), then connect with your configured local IRIS account. Fresh inference needs the local Ollama model and embeddings. The alternative keyless path uses recorded responses and does not prove fresh inference or the amendment case.

1. Open **Scenario Lab → Quantity mismatch** and inject once. Inspect `20 CASE`, the independently approved `240 EA` reference, the critical finding and **zero deliveries**. Local inference may take longer than a quick inspection.
2. Run **Approved amendment**. Follow the effective reference to the allowed route and its single simulator receipt. The change is approved authority, not a guessed conversion.
3. Open the case's native **Visual Trace**. Each admitted provider exchange is its own request/response pair in the business-case session. Inspect model, provider, prompt version, duration, tool calls and available response usage. Unknown cost and provider retries stay null.
4. Inspect **Review** and **CSV Import**. Review requires permission, a reason and the current case version. CSV preview uses a separate approved-reference export; commit requires explicit importer permission. Precedents add evidence and cannot override current authority.

[Full walkthrough](docs/JUDGE_GUIDE.md) · [CSV guide](docs/CSV_IMPORT.md) · [Verified source, commands and limits](docs/BUILD_STATUS.md).

<a id="local-checks-without-iris"></a>
<a id="prove-the-native-journey"></a>
<a id="optional-local-intake-and-procedural-guidance"></a>
## What is technically interesting

- **AI Hub is inside the production.** A Business Service and Business Process coordinate native investigation, read-only evidence tools, policy and routing Operations.
- **LLM calls are business trace messages.** [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) connects provider exchanges to the case's evidence, review and delivery/hold. [Reproduce it and compare with Langfuse](docs/NATIVE_AI_HUB.md). The dedicated OEX association is publicly visible; organizer qualification remains unconfirmed.
- **Authority is explicit.** The model proposes; policy authorizes. Review versioning and idempotency preserve a recorded decision and a single simulator receipt in the verified workflow.

## Versions and limits

Only **2026.3.0AI.154.0 Community / 154U ARM64** is qualified locally. Obtain its separately licensed image from InterSystems; it is not bundled or publicly redistributed. Other builds and platforms are not claimed tested.

Public native IPM and OEX release remain **0.3.0**; the separate React package remains **0.2.1**. Provider configuration and the new multi-page workbench are changes on `push/top3`, not a newly published native package. Use the matching source checkout for those changes. External OpenAI, Gemini and OpenRouter service execution remains unverified; no paid provider is needed for the tested local path.

All supplied examples are synthetic. Delivery is per line to an IRIS simulator, not an external ERP or bank. There is no X12 parser, whole-order completeness guarantee, hosted demo or production-readiness claim. The held-out prose-authority failures are a real limitation of the shipped structured-authority policy.

## Community Idea DPI-I-689: LLM tracing with Interoperability

SilentShift implements [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) by recording each admitted AI Hub provider exchange as a native request/response pair in its business-case session. The trace records model, provider, prompt version, timing, tool names, outcome and available response-token usage. Unknown cost and provider retries stay null; replay does not report recorded tokens as new usage.

### See it in Visual Trace

Use the **optional keyless replay** in [INSTALL.md](INSTALL.md#optional-check-without-a-model). It installs the public package into a separate container and prints a Visual Trace URL. [How to read the trace](docs/FEATURES.md#see-it-in-visual-trace).

### Native provider metadata

[Inspect the successful native Body capture](docs/assets/provider-success-body-safari.png) and the [failure capture](docs/assets/provider-failure-body-safari.png). They show retained live calls, not simulated portal screens. [Field map, values and limits](docs/FEATURES.md#native-provider-metadata).

### SilentShift (IRIS Interoperability) vs Langfuse

SilentShift connects model exchanges to native business messages and human review. Langfuse offers dedicated LLM evaluation, dashboards and prompt-management workflows. [Read the full comparison](docs/FEATURES.md#silentshift-iris-interoperability-vs-langfuse).

The idea implementation is verified locally, and the dedicated OEX association is publicly visible. Organizer qualification remains unconfirmed; no awarded points are claimed.

## Developer Community articles

- [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production)
- [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery)

## License

Source: [MIT](LICENSE). The proprietary InterSystems runtime is separately licensed and excluded. [Dependencies and attribution](docs/FEATURES.md#license-and-attribution).
