# Try SilentShift

An order can pass its JSON and transport checks while changing the meaning of a purchase. SilentShift investigates that gap before the included destination simulator accepts it. The core runs inside InterSystems IRIS: Business Service → Business Process → native AI Hub agent and scoped tools → Embedded Python policy → routing Operations.

The strongest demonstration is a pair of orders: hold a unit change without authority, then allow a change backed by an effective approved amendment. Conflicting references remain a separate review outcome. The browser shows the evidence behind each result.

## Inspect an actual result

These screenshots show persisted synthetic records from local Community AI Hub154U and Qwen3 4B inference. They are captures of the working application, not live hosted access.

![Currency fields disagree with an approved contract; server policy holds the message](assets/native-currency-quarantine.png)

![A browser-injected approved amendment was allowed and delivered to the simulator](assets/native-approved-delivery.png)

The second screenshot is case `D39226FC-D6B8-11F1-956F-F285F08CEB87`, native trace42. It was injected through Scenario Lab after the fresh-volume benchmark. Delivery is to the IRIS simulator, not an external ERP or bank.

## Reproduce the complete journey

1. Follow the [README setup](../README.md#native-build-154-setup), including the separately licensed EAP image and local model. Bootstrap never invokes a model or seeds operational cases.
2. Start the workbench, connect with the local configured account, and open **Scenario Lab**.
3. Choose **Quantity mismatch**. Inspect the submitted quantity/unit and independent contract, then click **Inject into IRIS** once. Keep the displayed run ID. Inspect the returned investigation: a critical contradiction must be held with zero simulator deliveries. The agent cannot infer a CASE→EA conversion.
4. Choose **Approved amendment** and inject once. Inspect both the earlier contract and effective amendment, the native agent's actual reads, the release checks and the delivered case. Retrying the same injection must reuse its case and receipt.
5. Run the conflict example. Without sufficient approved authority, its final route must be **Review**. A model concern alone is not proof of a critical contradiction.
6. Inspect **Timeline**, **Payload**, **Agent** and the recorded native trace ID. Visual Trace requires a portal account with the appropriate interoperability permissions; application viewer rights do not grant administrative access.

To capture all five scenarios plus replay and critical-release checks, use local inference and run:

```sh
uv run --env-file .env python scripts/verify_native.py --allow-model-calls
```

This performs real model work. Scenario E deliberately injects a labeled hostile validator proposal after a native answer; the original model response remains separate. It demonstrates containment of unsafe input to policy, not a claim that the model spontaneously produced that attack.

## Measured results and limits

The [machine-readable public summary](evidence/native-summary.json) includes all four retained trials and hashes of their full local exports. Raw local evidence and runtime images remain outside Git.

| Native trial | Model proposals | Final outcomes | Unsafe simulator releases |
|---|---:|---:|---:|
| Initial1.7B trial | Incomplete; one empty answer | Benchmark rejected | No deliveries observed |
| First4B trial, policy1.0 | 2/5 | 3/5 | 0/4 |
|4B, policy1.1 | 4/5 | 5/5 | 0/4 |
| Fresh-volume4B repeat, policy1.1 | 5/5 | 5/5 | 0/4 |

These are five frozen synthetic cases per trial. The deterministic baseline also solves all five; no AI accuracy uplift is demonstrated. The agent provides an inspectable, evidence-bound recommendation and can veto release; deterministic policy constrains what may happen afterward. Session-wide token totals and billing cost are unavailable; the final response's token usage is a narrower measurement. The clean repeat's mean agent time was24,664.2ms, p9537,431ms across five cases, not a throughput result.

The fresh installation began with zero cases and evaluations. Its trace IDs were2,10,18,26,34, with one delivery for the approved amendment and zero for the other four cases. Separate native checks exercised permission denials, malformed/blank reviews, optimistic versions, concurrent idempotent approval, human rejection, restart persistence and oversized evidence containment. See [build status](BUILD_STATUS.md) for their exact scopes.

## What to assess against the rubric

| Official criterion | Inspect |
|---|---|
| Complexity | A complete native production, scoped tool retrieval, versioned independent references and transaction-protected simulator effects. |
| Clarity of Instructions | Exact runtime/provider, load/start/check commands, five-case verifier and this walkthrough. |
| Developer Experience | Local inference, source-only distribution, empty-volume installation evidence, typed API and separate host/native/browser checks. |
| Applicability | Pre-delivery contradictions in orders/payments, effective amendments and conflicting authority; all supplied data is synthetic. |
| Usability | Evidence comparison, distinct quarantine/review/delivered states, explicit reviewer gates, desktop/mobile and keyboard behavior. |

This maps observable evidence to the [official criteria](https://openexchange.intersystems.com/contest/49); it does not predict a judge's score. Public deployment, provider-side cancellation, broad repeated-trial performance and real external delivery remain outside the verified boundary.
