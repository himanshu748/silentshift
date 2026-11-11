# SilentShift

**Catch orders that are valid JSON but mean the wrong thing, before they're delivered.**

A B2B order arrives as `20 CASE`. The approved contract says `240 EA`. Every transport and schema check passes, yet the business meaning has changed and nothing approved that change. SilentShift is an IRIS Interoperability production that holds that order. An IRIS AI Hub agent investigates it, and the operator sees why it was held.

If an approved amendment *does* allow `20 CASE`, the same order goes through. **The difference between those two outcomes is the authority behind the order, and that's the decision the AI Hub agent helps make.**

**[Explore the recorded evidence tour](https://himanshu748.github.io/silentshift/)** · [Watch the captioned demo](https://youtu.be/a4dOcqu89EA) · [Download MP4](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [Open Exchange](https://openexchange.intersystems.com/package/SilentShift) · [Full install guide](INSTALL.md)

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
2. **[Explore the interactive recorded-evidence gallery](https://himanshu748.github.io/silentshift/#workbench)** or [inspect the captures above](#inspect-the-workflow-without-installing). Compare the order and approved reference, see a native Workflow task, then open the actual Visual Trace message properties. This static tour uses recorded local synthetic cases; it requires no login and does not run a hosted native production.
3. **[Check one bonus at a time](#contest-bonuses).** Each row links to execution or publication evidence and separates it from organizer qualification.

To execute the workflow yourself, use the [keyless replay](#keyless-replay-no-model-no-api-key) after obtaining the official image, or follow [INSTALL.md](INSTALL.md) for fresh local Ollama inference. The recorded route should be `QUARANTINED`, `delivery_count=0`, with `checks=12/12; passed=true`.

## Who uses it

SilentShift is for integration operations teams handling partner order feeds. It puts the incoming value, independently approved commitment, recommendation and permitted next action in one case, reducing the need to reconstruct that comparison across payloads, contracts and logs. The `20 CASE` / `240 EA` example illustrates that task; no customer time or money savings have been measured.

<a id="local-checks-without-iris"></a>
<a id="prove-the-native-journey"></a>
<a id="optional-local-intake-and-procedural-guidance"></a>

A [local receipt inspector](docs/RECEIPT_INSPECTOR.md) independently checks a real synthetic Java PEX export and demonstrates how tampering breaks its signature. It runs in your browser without IRIS or a model; publication to Pages remains a separate step.

A [guided recorded-case tour](docs/RECORDED_TOUR.md) compares the actual unsupported-order hold and approved-amendment release, with model proposals, policy checks and signed receipts. It is a local static viewer; publishing the new Pages files remains gated.

### Published package and this branch

**Native IPM and Open Exchange publish 0.3.2, including the [Java PEX receipt exporter](docs/JAVA_PEX.md).** After a routing outcome is committed, the production requests an immutable signed receipt. Export failure preserves the existing route. The separately built React workbench remains **0.2.1**.

[Anonymous publication proof](docs/evidence/ipm-032-publication-nov11/publication.json) confirms the public archive's manifest and receipt-mode source. A [fresh offline archive install from the release tag](docs/evidence/ipm-032-final-nov11/summary.json) passed in an empty, stopped instance; the later [fresh public 0.3.2 gate](docs/evidence/voting-nov11-judge/summary.json) independently passed production startup, the native suite and both keyless replays. The [receipt-mode regression](docs/evidence/receipt-mode-nov11/summary.json) and [earlier live citation checks](docs/CITATION_COMPLETENESS.md) retain their separate source snapshots. Only local Ollama is live-qualified; other provider adapters are configuration/protocol-tested. [Provider configuration](docs/PROVIDERS.md).

### Run it locally

Use the numbered [INSTALL.md](INSTALL.md) checklist for prerequisites, the separately licensed **154U ARM64** image, model setup, accounts and the browser workbench. It is the single full installation guide. The local keyless check below needs Git, Python/uv, a running Colima Docker profile and the already-loaded IRIS/Web Gateway images; it needs no Node build, model or application `.env`.

### Keyless replay (no model, no API key)

After starting the documented Colima profile and loading the official build-154 ARM64 and Web Gateway images:

```sh
./scripts/judge-replay.sh
```

The launcher creates new isolated test containers and private local test credentials, installs **public native IPM 0.3.2**, starts the production, runs release-matched native tests and performs two recorded replays. It prints their session IDs and Visual Trace URLs. It selects a disjoint private Docker subnet, fetches release-pinned native assertions and the official IPM installer; it never downloads an IRIS image or calls a model. **This verifies public 0.3.2 using the assertion source pinned to its release tag; it does not install the current source checkout.** No `.env` editing is needed for this replay. [Prerequisites, output and troubleshooting](INSTALL.md#optional-check-without-a-model).

The [fresh-main check](docs/evidence/voting-week-nov10/judge-main-nov10.json) passed native **5 classes / 12 methods**, both **12/12** replays and **207 Python tests** on the declared build. Its exact clone and scope are recorded separately from the launcher check. For a port already in use, pass `--api-port 52983`; never replace an existing container or lower disk limits.

### Open the source workbench without a model

After the [image and Compose prerequisites](INSTALL.md#optional-source-workbench-without-a-model), run:

```sh
./scripts/judge-compose.sh
```

This starts the current-source IRIS production and React workbench with private generated local accounts, then proves the recorded hold with `checks=12/12; passed=true`. It prints the workbench and Visual Trace URLs. It uses dedicated volumes and refuses another running build-154 instance in the same Docker context. [Fresh-clone execution and browser proof](docs/evidence/voting-finish-nov10/compose-final.json). This is separate from the release-matched public native 0.3.2 replay above; it invokes no LLM and establishes no hosted demo.

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

**Claimed** means requested for organizer review, supported by the linked code or observed artifact. It does not mean points have been awarded. [Full ledger and limits](docs/SUBMISSION_CHECKLIST.md#every-bonus). Only **2026.3.0AI.154.0 / 154U ARM64** is locally qualified.

| Bonus | Points requested | Status | Direct evidence |
| --- | ---: | --- | --- |
| Docker | 2 | Claimed | [Compose](compose.judge.yaml) · [fresh native container execution](docs/evidence/voting-finish-nov10/compose-final.json) |
| IPM deployment: `zpm "install silentshift"` | 2 | Claimed | [Public 0.3.2 archive](https://pm.community.intersystems.com/download/silentshift/-/silentshift-0.3.2.tgz) · [manifest/source readback](docs/evidence/ipm-032-publication-nov11/publication.json); [literal public install/startup/replays](docs/evidence/voting-week-nov10/judge-main-nov10.json) is the earlier 0.3.0 run |
| Native Workflow Engine | 2 | Claimed | [Native coordinator](src/SilentShift/Workflow/Coordinator.cls) · [approve/reject/concurrency execution](docs/evidence/review-queue.json) |
| Custom adapter: PartnerJSON | 2 | Claimed | [Ens.InboundAdapter subclass](src/SilentShift/Adapter/PartnerJSON.cls) · [native file intake and recovery](docs/evidence/adapter.json) |
| IRIS Vector Search | 2 | Claimed | [Native VECTOR column](src/SilentShift/Data/Precedent.cls) · [cosine retrieval](src/SilentShift/Precedents.cls) · [executed corpus](docs/evidence/precedent-corpus.json) |
| Embedded Python | 3 | Claimed | [Assessment and policy: Language = python](src/SilentShift/Bridge.cls) · [production call sites](src/SilentShift/Process/Semantic.cls) · [native execution/source audit](docs/evidence/bonus-claims-nov11/embedded-python.json) |
| Community idea DPI-I-689 | 4 | Claimed; qualification pending | [Idea](https://ideas.intersystems.com/ideas/DPI-I-689) · [Visual Trace recipe and Langfuse comparison](#community-idea-dpi-i-689-llm-tracing-with-interoperability) · [native message bodies](docs/evidence/provider-body-captures.json) · [public OEX association](https://openexchange.intersystems.com/package/SilentShift) |
| First AI Hub bug | 2 | Claimed; vendor/organizer confirmation pending | [Issue #17: standalone reproduction and compiler log](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) |
| First Developer Community article | 2 | Claimed | [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) |
| Second Developer Community article | 1 | Claimed | [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery) |
| Video | 3 | Claimed | [YouTube](https://youtu.be/a4dOcqu89EA) · [download the same MP4 without sign-in](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [full-file/hash/media check](docs/evidence/bonus-claims-nov11/video.json). The 2:30 synthetic-workflow recording predates CSV. |
| Questionnaire | 1 | Claimed | [Submitted confirmation](docs/assets/questionnaire-submitted.png); already submitted, do not resubmit |
| Java PEX | 3 | Claimed; published in native 0.3.2; qualification pending | [Java operation](java/src/main/java/SilentShift/PEX/ReceiptExporter.java) · [production wiring](src/SilentShift/Production.cls) · [native test](tests/iris/PEXChecks.cls) · [receipt-mode regression](docs/evidence/receipt-mode-nov11/summary.json) · [fresh offline install](docs/evidence/ipm-032-final-nov11/summary.json) · [live Visual Trace](docs/evidence/bonus-claims-nov11/java-pex-live-trace.png) |
| Online demo | — | Not claimed | The published evidence tour is static recorded material, not a running native app |
| Embedded Python bug | — | Not claimed | [Signal-11 candidate is not isolated or attributed](docs/bug-reports/callback-signal11-candidate.md) |

[Official criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). No awarded score, ranking, newer build or live hosting is claimed.

## Developer Community articles

- [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production)
- [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery)

## License

Source: [MIT](LICENSE). The InterSystems runtime is licensed separately and isn't included. [Dependencies and attribution](docs/FEATURES.md#license-and-attribution).
