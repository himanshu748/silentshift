# SilentShift

**Catch orders that are valid JSON but mean the wrong thing, before they're delivered.**

A B2B order arrives as `20 CASE`. The approved contract says `240 EA`. Every transport and schema check passes, yet the business meaning has changed and nothing approved that change. SilentShift is an IRIS Interoperability production that holds that order. An IRIS AI Hub agent investigates it, and the operator sees why it was held.

If an approved amendment *does* allow `20 CASE`, the same order goes through. **The difference between those two outcomes is the authority behind the order, and that's the decision the AI Hub agent helps make.**

**[Watch the captioned demo](https://youtu.be/a4dOcqu89EA)** · [Download MP4](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [Open Exchange](https://openexchange.intersystems.com/package/SilentShift) · [Full install guide](INSTALL.md)

## Inspect the workflow without installing

These November 10 captures show one synthetic **recorded replay** in the local source workbench on 154U ARM64. They show the interface and persisted native messages, not fresh inference or a hosted demo. [Capture provenance and limits](docs/evidence/backend-polish-nov10/11-native-ui.json).

**1 — The policy makes the mismatch explicit.** Incoming `20 CASE`, approved `240 EA`, no authorized conversion: the order is held.

![The source workbench compares incoming 20 CASE with the approved 240 EA reference and shows the critical policy decision](docs/assets/voting-week-nov10/02-policy-evidence.jpg)

<details>
<summary>2 — Inspect the original order</summary>

![The original synthetic order payload in the source workbench](docs/assets/voting-week-nov10/01-original-order.jpg)

</details>

<details>
<summary>3 — Inspect the agent’s evidence reads and recorded recommendation</summary>

The mode is labeled recorded replay. Four case-scoped evidence reads and the recommendation are inspectable; the policy remains the final authority.

![The workbench shows the recorded native agent recommendation and case-scoped evidence reads](docs/assets/voting-week-nov10/03-native-agent.jpg)

</details>

<details>
<summary>4 — Open the native Workflow task</summary>

This critical case has an actual native task; approval is disabled. No review decision was submitted while making this capture. [Separately executed approve/reject/concurrency proof](docs/evidence/backend-polish-nov10/upgrade-review.json).

![The source Review view shows the native task and disables approval of a critical contradiction](docs/assets/voting-week-nov10/04-workflow-review.jpg)

</details>

<details>
<summary>5 — Read the provider response in native Visual Trace</summary>

Session 58 records the model, provider, prompt version, recorded mode, timing and tool call. Tokens and cost remain unknown for replay. The temporary synthetic-message read permissions used for capture were restored exactly afterward.

![Native Visual Trace Body properties show the recorded provider response metadata](docs/assets/voting-week-nov10/07-provider-native-metadata.jpg)

</details>

<a id="native-build-154-setup"></a>
<a id="installation"></a>

## For judges: two minutes, no installation

1. **Watch the first 90 seconds of the [captioned demo](https://youtu.be/a4dOcqu89EA).** Start with the unsupported `20 CASE` hold and the approved amendment. The full recording is 2:30 and predates CSV and the newer source interface.
2. **[Inspect the captured workflow above](#inspect-the-workflow-without-installing).** Compare the order and approved reference, see a native Workflow task, then open the actual Visual Trace message properties. These are recorded local synthetic cases; they require no login and are not an online demo.
3. **[Check one bonus at a time](#contest-bonuses).** Each row links to execution or publication evidence and separates it from organizer qualification.

To execute the workflow yourself, use the [keyless replay](#keyless-replay-no-model-no-api-key) after obtaining the official image, or follow [INSTALL.md](INSTALL.md) for fresh local Ollama inference. The recorded route should be `QUARANTINED`, `delivery_count=0`, with `checks=12/12; passed=true`.

## Who uses it

SilentShift is for integration operations teams handling partner order feeds. It puts the incoming value, independently approved commitment, recommendation and permitted next action in one case, reducing the need to reconstruct that comparison across payloads, contracts and logs. The `20 CASE` / `240 EA` example illustrates that task; no customer time or money savings have been measured.

<a id="local-checks-without-iris"></a>
<a id="prove-the-native-journey"></a>
<a id="optional-local-intake-and-procedural-guidance"></a>

### Published package and this branch

Public native IPM and Open Exchange remain **0.3.0**; the separate React package remains **0.2.1**. This `backend-polish-nov10` branch prepares **native 0.3.1**, which is not published or merged. It includes the earlier `push/top3` provider/cited-evidence work and backend diagnostics. [Fresh candidate verification](docs/evidence/voting-finish-nov10/candidate-031-summary.json) covers native startup, tests and replay; [live source cases](docs/evidence/voting-finish-nov10/fresh-live-five.json) and [connected browser checks](docs/evidence/voting-finish-nov10/connected-final.json) retain their exact snapshots. Only local Ollama is live-qualified; other provider adapters are configuration/protocol-tested. [Provider configuration](docs/PROVIDERS.md).

### Run it locally

Use the numbered [INSTALL.md](INSTALL.md) checklist for prerequisites, the separately licensed **154U ARM64** image, model setup, accounts and the browser workbench. It is the single full installation guide. The local keyless check below needs Git, Python/uv, a running Colima Docker profile and the already-loaded IRIS/Web Gateway images; it needs no Node build, model or application `.env`.

### Keyless replay (no model, no API key)

After starting the documented Colima profile and loading the official build-154 ARM64 and Web Gateway images:

```sh
./scripts/judge-replay.sh
```

The launcher creates new isolated test containers and private local test credentials, installs **public native IPM 0.3.0**, starts the production, runs release-matched native tests and performs two recorded replays. It prints their session IDs and Visual Trace URLs. It selects a disjoint private Docker subnet, fetches release-pinned native assertions and the official IPM installer; it never downloads an IRIS image or calls a model. **This verifies the public package, not unpublished source runtime changes.** No `.env` editing is needed for this replay. [Prerequisites, output and troubleshooting](INSTALL.md#optional-check-without-a-model).

The [fresh-main check](docs/evidence/voting-week-nov10/judge-main-nov10.json) passed native **5 classes / 12 methods**, both **12/12** replays and **207 Python tests** on the declared build. Its exact clone and scope are recorded separately from the launcher check. For a port already in use, pass `--api-port 52983`; never replace an existing container or lower disk limits.

### Open the source workbench without a model

After the [image and Compose prerequisites](INSTALL.md#optional-source-workbench-without-a-model), run:

```sh
./scripts/judge-compose.sh
```

This starts the current-source IRIS production and React workbench with private generated local accounts, then proves the recorded hold with `checks=12/12; passed=true`. It prints the workbench and Visual Trace URLs. It uses dedicated volumes and refuses another running build-154 instance in the same Docker context. [Fresh-clone execution and browser proof](docs/evidence/voting-finish-nov10/compose-final.json). This is separate from installing public native 0.3.0 above; it invokes no LLM and establishes no hosted demo.

## How the decision works

Business Service → Business Process → **IRIS AI Hub agent with scoped read-only tools** → Embedded Python policy → routing Operations.

- The agent returns `ALLOW`, `QUARANTINE` or `REQUEST_REVIEW` with evidence IDs, an explanation and an uncertainty score. Its tools can only read the current case's evidence.
- **The agent proposes; policy decides.** Automatic delivery needs a valid `ALLOW`, complete evidence citations and uncertainty of 0.35 or less. A critical contradiction is held even if the agent says `ALLOW`.
- Eligible holds become native IRIS Workflow review tasks. A reviewer can't approve a critical contradiction.
- Missing, malformed or made-up answers never cause delivery.

[Judge walkthrough](docs/JUDGE_GUIDE.md) · [Features and API](docs/FEATURES.md) · [Architecture](ARCHITECTURE.md) · [CSV order import](docs/CSV_IMPORT.md)

## Community Idea DPI-I-689: LLM tracing with Interoperability

<a id="see-it-in-visual-trace"></a>
<a id="native-provider-metadata"></a>
<a id="silentshift-iris-interoperability-vs-langfuse"></a>

Each AI Hub provider exchange is saved as a native request/response pair in the business session. It records model, provider, prompt version, timing, tool names, outcome and response-token usage when the provider reports it. Unknown cost stays null, and replay never counts recorded tokens as new usage. [How to read the trace](docs/FEATURES.md#see-it-in-visual-trace) · [Native Body capture](docs/assets/provider-success-body-safari.png) · [Field map](docs/FEATURES.md#native-provider-metadata) · [vs Langfuse](docs/FEATURES.md#silentshift-iris-interoperability-vs-langfuse)

The dedicated Open Exchange idea association is now publicly visible; organizer qualification remains **unconfirmed**. [Anonymous readback and scope](docs/evidence/top3-public-review.json).

## What the held-out comparison showed

This is the completed v2 comparison before later source-branch pipeline changes. The newer sealed evaluation is incomplete; no sealed-set result or post-tuning improvement is claimed here.

- On **48 frozen synthetic orders**, rules-only produced **33/48** correct routes; agent + policy produced **33/48, 33/48 and 30/48** across three trials.
- Rules recommended releasing **6/23** release-ineligible orders. The shipped arm made **2/23, 3/23 and 3/23 actual wrong simulator deliveries**, with more false holds: **9/25, 9/25 and 12/25**, versus the baseline's **9/25**.
- **Agent + policy did not improve correct routing in the unstructured split: 1/16 for both in every trial.** Five failed agent attempts remain counted. This does not establish an overall AI accuracy improvement.

[Every result, failure, timing and rules win](docs/EVAL_HELDOUT.md) · [Frozen labels and protocol](fixtures/v2-heldout/FROZEN.md) · [Raw native observations](evidence/heldout/summary.json). Baseline releases are counterfactual choices; only the shipped arm executed simulator deliveries. The same cases repeat across trials and are not independent production orders.

## Honest limits

- All orders are synthetic and deliver only to an IRIS simulator. There's no hosted demo and no real ERP or bank connection.
- Only **2026.3.0AI.154.0 Community / 154U ARM64** is qualified locally. Other builds and platforms are not claimed tested.
- The held-out result above does not establish an overall accuracy improvement or better unstructured routing. The version used in that comparison missed genuine prose-authority cases; every failure remains in the report. Later pipeline changes are not evidence of a measured improvement.

## Contest bonuses

**Verified** means observed behavior or publication in the linked receipt, not awarded points. Every organizer qualification/award remains unconfirmed. [Full ledger and limits](docs/SUBMISSION_CHECKLIST.md).

| Bonus | Status | One evidence link |
| --- | --- | --- |
| Native Workflow | Verified | [Queue, rejection and concurrent approval](docs/evidence/review-queue.json) |
| Custom inbound adapter | Verified | [Native file intake and recovery](docs/evidence/adapter.json) |
| IRIS Vector Search | Verified | [Native vectors and source bindings](docs/evidence/precedent-corpus.json) |
| Docker | Verified | [Fresh no-source-mount public install](docs/evidence/voting-week-nov10/judge-main-nov10.json) |
| Public IPM 0.3.0 | Verified | [Registry install, startup, tests and replays](docs/evidence/voting-week-nov10/judge-main-nov10.json) |
| Developer Community articles | Verified | [Both live articles and OEX backlinks](docs/evidence/voting-week-nov10/public-readback.json) |
| Downloadable demonstration video | Verified | [Anonymous full-file download](docs/evidence/voting-week-nov10/public-readback.json) |
| Questionnaire | Verified | [Retained submitted confirmation](docs/assets/questionnaire-submitted.png); do not resubmit |
| DPI-I-689 implementation | Pending qualification | [Native provider Body evidence](docs/evidence/provider-body-captures.json); dedicated OEX association is public |
| AI Hub bug #17 | Pending vendor/organizer confirmation | [Filed reproduction](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) |
| Embedded Python, Java/.NET PEX, online demo and Embedded Python bug bonus | Not claimed | [Scope and reasons](docs/SUBMISSION_CHECKLIST.md) |

## Developer Community articles

- [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production)
- [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery)

## License

Source: [MIT](LICENSE). The InterSystems runtime is licensed separately and isn't included. [Dependencies and attribution](docs/FEATURES.md#license-and-attribution).
