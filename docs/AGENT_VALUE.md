# What the agent saw that the rules missed

On the existing **48 held-out synthetic orders**, rules-only would release **6/23** release-ineligible orders. Agent + policy produced **2/23, 3/23 and 3/23 actual wrong simulator deliveries**. Review increased from **12.5%** to **21.5%** across pooled agent trials.

**No overall accuracy gain:** correct routes were **33/48** for rules and **33/48, 33/48 and 30/48** for agent + policy. Unstructured exact routing stayed **1/16** in every trial. [Full report](EVAL_HELDOUT.md) · [original summary](../evidence/heldout/summary.json).

These are three selected November 9 observations, not new evaluation cases. In each, the raw agent matches the frozen QUARANTINE label and the baseline chooses ALLOW. Policy creates REQUEST_REVIEW instead: no simulator delivery, but still an incorrect final three-way label. This demonstrates **reviewer assist**, not autonomous resolution or a general accuracy improvement.

The pending native Workflow task retains the cited concern. No completed reviewer decision is recorded. Synthetic approved-source provenance is stipulated; no actual buyer identity or document authenticity was verified. The historical code checkpoint predates current native 0.3.2 / React 0.2.1.

The interactive static view is in [agent-value.html](site/agent-value.html). Its public Pages URL is prepared for the separately approved deployment, not claimed live by this branch.

<a id="ho-045"></a>

## HO-045 — The quantity changed in prose

Incoming: **100 EA of SKU-CERAMIC**.

> Approved purchase order PO-SYN-H019: exactly 100 EA of SKU-CERAMIC, business unit SOUTH, event-time terms. No substitutions or unit conversions unless an independently approved written change explicitly authorizes them. Signed amendment B, effective 8 November 2026: the exact quantity for this PO is reduced to 80 EA; the former 100 EA table entry is obsolete. No over-delivery is permitted.

This is verbatim `record.references[0].contract_text` from [trial 1](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-1/HO-045.json).

- **Rules-only:** ALLOW, structured assessment CLEAR. [Original baseline](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/rules-only.json), scenario `HO-045`.
- **Raw agent:** QUARANTINE. “Approved contract reduces quantity to 80 EA; 100 EA violates current authority.” Cites `reference:H019:v1`.
- **Final policy:** REQUEST_REVIEW. “Agent concerns without a verified critical contradiction require human review.”
- **Consequence:** 0 simulator deliveries; Workflow task `1184` is `pending`. Native case `5D9DCCA2-DC07-11F1-A103-A90DC9E483ED`, session `1383`. No human resolution is recorded.
- **Frozen truth:** QUARANTINE. The effective signed amendment replaces 100 EA with exactly 80 EA; the incoming 100 EA exceeds the new commitment. [Frozen dataset](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/fixtures/v2-heldout/scenarios.json).

| Existing trial | Raw agent | Final policy | Workflow task | Simulator deliveries | Original record |
| --- | --- | --- | --- | ---: | --- |
| 1 | QUARANTINE | REQUEST_REVIEW | 1184 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-1/HO-045.json) |
| 2 | QUARANTINE | REQUEST_REVIEW | 2298 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-2/HO-045.json) |
| 3 | QUARANTINE | REQUEST_REVIEW | 3400 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-3/HO-045.json) |

<a id="ho-030"></a>

## HO-030 — The buyer cancelled the order

Incoming: **54 EA of SKU-CERAMIC**.

> Approved buyer instruction, issued 8 November at 12:00 UTC for this PO: cancel the order in full. Do not dispatch any goods under the original 54 EA commitment.

This is verbatim `record.references[0].buyer_po_note` from [trial 1](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-1/HO-030.json).

- **Rules-only:** ALLOW, structured assessment CLEAR. [Original baseline](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/rules-only.json), scenario `HO-030`.
- **Raw agent:** QUARANTINE. “Approved contract mandates full cancellation of original order commitment.” Cites `reference:H021:v1`.
- **Final policy:** REQUEST_REVIEW. “Agent concerns without a verified critical contradiction require human review.”
- **Consequence:** 0 simulator deliveries; Workflow task `838` is `pending`. Native case `B32F3862-DC06-11F1-A103-A90DC9E483ED`, session `970`. No human resolution is recorded.
- **Frozen truth:** QUARANTINE. The approved cancellation withdraws the 54 EA commitment before the event; dispatch of this order is prohibited. [Frozen dataset](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/fixtures/v2-heldout/scenarios.json).

| Existing trial | Raw agent | Final policy | Workflow task | Simulator deliveries | Original record |
| --- | --- | --- | --- | ---: | --- |
| 1 | QUARANTINE | REQUEST_REVIEW | 838 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-1/HO-030.json) |
| 2 | QUARANTINE | REQUEST_REVIEW | 1952 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-2/HO-030.json) |
| 3 | QUARANTINE | REQUEST_REVIEW | 3070 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-3/HO-030.json) |

<a id="ho-017"></a>

## HO-017 — The old part was explicitly prohibited

Incoming: **28 EA of SKU-OLD-CLAMP**.

> Signed buyer correction, effective 8 November: replace SKU-OLD-CLAMP with SKU-NEW-CLAMP for all 28 EA. The old clamp must not be supplied. The table has not yet been refreshed.

This is verbatim `record.references[0].buyer_po_note` from [trial 1](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-1/HO-017.json).

- **Rules-only:** ALLOW, structured assessment CLEAR. [Original baseline](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/rules-only.json), scenario `HO-017`.
- **Raw agent:** QUARANTINE. “Approved contract mandates no substitution; old clamp must not be supplied.” Cites `reference:H022:v1`.
- **Final policy:** REQUEST_REVIEW. “Agent concerns without a verified critical contradiction require human review.”
- **Consequence:** 0 simulator deliveries; Workflow task `536` is `pending`. Native case `1B3FF51D-DC06-11F1-A103-A90DC9E483ED`, session `611`. No human resolution is recorded.
- **Frozen truth:** QUARANTINE. The effective buyer correction prohibits the old product; this order still supplies SKU-OLD-CLAMP. [Frozen dataset](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/fixtures/v2-heldout/scenarios.json).

| Existing trial | Raw agent | Final policy | Workflow task | Simulator deliveries | Original record |
| --- | --- | --- | --- | ---: | --- |
| 1 | QUARANTINE | REQUEST_REVIEW | 536 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-1/HO-017.json) |
| 2 | QUARANTINE | REQUEST_REVIEW | 1650 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-2/HO-017.json) |
| 3 | QUARANTINE | REQUEST_REVIEW | 2764 | 0 | [Raw JSON](https://github.com/himanshu748/silentshift/blob/7ae03be03ac6721639e83bdd9e3ed07a5350649e/evidence/heldout/trial-3/HO-017.json) |

## Read the wider result

Examples were selected after results were known. The same 48 cases repeat across three paired agent trials; they are not 144 independent orders. The review denominators are 6/48 and 31/144. Three trials do not establish statistical superiority. Rules also beat the agent on cases retained in the [complete failure table](EVAL_HELDOUT.md#every-failure). No label or raw observation was changed. No model, native API, policy or evaluation was run to build this presentation.
