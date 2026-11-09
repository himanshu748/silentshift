# SilentShift

**Catch orders that are valid JSON but mean the wrong thing, before they're delivered.**

A B2B order arrives as `20 CASE`. The approved contract says `240 EA`. Every transport and schema check passes, yet the business meaning has changed and nothing approved that change. SilentShift is an IRIS Interoperability production that holds that order. An IRIS AI Hub agent investigates it, and the operator sees why it was held.

If an approved amendment *does* allow `20 CASE`, the same order goes through. **The difference between those two outcomes is the authority behind the order, and that's the decision the AI Hub agent helps make.**

**[Watch the captioned demo](https://youtu.be/a4dOcqu89EA)** · [Download MP4](https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4) · [Open Exchange](https://openexchange.intersystems.com/package/SilentShift) · [Full install guide](INSTALL.md)

![The source-built SilentShift home page, with a labeled synthetic order comparison](evidence/browser/top3-multipage/home-light-desktop.png)

## What the held-out comparison showed

- On **48 frozen synthetic orders**, rules-only produced **33/48** correct routes; agent + policy produced **33/48, 33/48 and 30/48** across three trials.
- Rules recommended releasing **6/23** release-ineligible orders. The shipped arm made **2/23, 3/23 and 3/23 actual wrong simulator deliveries**, with more false holds: **9/25, 9/25 and 12/25**, versus the baseline's **9/25**.
- **Agent + policy did not improve correct routing in the unstructured split: 1/16 for both in every trial.** Five failed agent attempts remain counted. This does not establish an overall AI accuracy improvement.

[Every result, failure, timing and rules win](docs/EVAL_HELDOUT.md) · [Frozen labels and protocol](fixtures/v2-heldout/FROZEN.md) · [Raw native observations](evidence/heldout/summary.json). Baseline releases are counterfactual choices; only the shipped arm executed simulator deliveries. The same cases repeat across trials and are not independent production orders.

<a id="native-build-154-setup"></a>
<a id="installation"></a>

## For judges: two minutes to understand the workflow

1. **Watch the [demo video](https://youtu.be/a4dOcqu89EA).** You'll see the held `20 CASE` order, then the approved amendment that lets it through. The video predates the new source workbench and CSV importer.
2. **Run it without a model or API key.** Use the keyless replay (commands below). It installs the public IPM package, runs the native tests and replays one recorded investigation. It should end with `checks=12/12; passed=true`, `routing=QUARANTINED` and `delivery_count=0`.
3. **Open the printed Visual Trace URL.** Each AI Hub model call is a native request/response message inside the business session. This is [Ideas Portal DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689).
4. **Want live inference?** Follow the [full install](INSTALL.md). It uses a local Ollama model, with no paid API key.

<a id="native-build-154-setup"></a>
<a id="local-checks-without-iris"></a>
<a id="prove-the-native-journey"></a>
<a id="optional-local-intake-and-procedural-guidance"></a>

### Published package and this branch

Public native IPM and Open Exchange remain **0.3.0**; the separate React package remains **0.2.1**. The new multi-page workbench, configurable providers and bounded demo gateway are on **`push/top3`**, not a newly published package. Use that source checkout for these changes. The gate for current native source covers fresh recorded replay and local Ollama; OpenAI, Gemini and OpenRouter are configuration/protocol-tested only, not verified against their services. [Source verification](docs/evidence/top3-quality.json) · [Provider configuration](docs/PROVIDERS.md).

### What you need

| | |
| --- | --- |
| IRIS image | **IRIS Community AI Hub 2026.3.0AI.154.0 (build 154), ARM64**, from the [EAP portal](https://evaluation.intersystems.com/Eval/early-access/AIHub). Tested on macOS/Apple Silicon only. |
| LLM provider | **Local Ollama** (`qwen3-silentshift:4b-instruct`), set by `SILENTSHIFT_MODEL` and `SILENTSHIFT_LLM_BASE_URL` in `.env`. **No API key needed.** The keyless replay needs no model at all. |
| Tools | Git, Python 3.11+, uv, Docker (Colima) with Compose 2. Node.js 22.12+ only for the browser workbench. |

### Load and retag the image

```sh
git clone https://github.com/himanshu748/silentshift.git
cd silentshift
docker load -i "/absolute/path/to/official-build154-docker.tar.gz"
docker tag "<image name printed by docker load>" silentshift-iris:2026.3.0AI.154.0
docker pull containers.intersystems.com/intersystems/webgateway:2026.1
cp -n .env.example .env && chmod 600 .env
```

In `.env`, set `IRIS_IMAGE=silentshift-iris:2026.3.0AI.154.0` and three different local passwords (12+ characters). [Details](INSTALL.md#3-set-your-local-passwords).

### Keyless replay (no model, no API key)

```sh
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
chmod 644 .local/ipm/vendor/zpm-0.10.10.xml
PUBLIC_IPM_VERSION=0.3.0
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest \
  --version "$PUBLIC_IPM_VERSION" \
  --execution-mode recorded-replay --container silentshift-bonus-registry-judge \
  --api-port 52843 --execute
uv run python scripts/trace_example.py \
  --api http://127.0.0.1:52843/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-registry-judge
```

Expect `unit_suite_passed: true` and `replay_passed: true` from the first command. The second prints `checks=12/12; passed=true` and the Visual Trace URL. On Colima, run `colima start --profile silentshift` and `export DOCKER_CONTEXT=colima-silentshift` first, as shown in [INSTALL.md](INSTALL.md#1-get-the-source-and-start-docker).

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

## Honest limits

- All orders are synthetic and deliver only to an IRIS simulator. There's no hosted demo and no real ERP or bank connection.
- Only **2026.3.0AI.154.0 Community / 154U ARM64** is qualified locally. Other builds and platforms are not claimed tested.
- The held-out result above does not establish an overall accuracy improvement or better unstructured routing. The policy's structured-authority boundary misses genuine prose-authority cases; every failure remains in the report.

## Developer Community articles

- [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production)
- [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery)

## License

Source: [MIT](LICENSE). The InterSystems runtime is licensed separately and isn't included. [Dependencies and attribution](docs/FEATURES.md#license-and-attribution).
