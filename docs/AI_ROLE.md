# The AI agent's role

SilentShift uses an IRIS AI Hub agent to investigate held partner orders. The agent does not decide whether an order is delivered.

## What the agent does

When policy holds an order, the agent investigates the current case. It can only read that case's evidence. It cites contract clauses and other evidence it actually read, then proposes a route — `ALLOW`, `QUARANTINE` or `REQUEST_REVIEW` — with an explanation, evidence IDs and an uncertainty score.

[Try the hosted replay](https://34.239.152.223.sslip.io/demo/) to see one recorded investigation, the native policy decision and a signed receipt. The proposal is recorded; there is no fresh model inference. [Scope and expiry](ONLINE_DEMO.md).

Selected examples of reviewer assist, with original clauses and cited recommendations, are in [AGENT_VALUE.md](AGENT_VALUE.md).

## What the agent does not do

**The agent never decides routing.** Native IRIS policy decides, and a signed Java PEX receipt records the committed outcome. Export failure preserves the existing route.

Automatic delivery needs a valid `ALLOW`, complete evidence citations and uncertainty of 0.35 or less. A critical contradiction is held even if the agent says `ALLOW`. Missing, malformed or made-up answers never cause delivery. Eligible holds can become native IRIS Workflow review tasks; a reviewer can't approve a critical contradiction.

## What the held-out evidence shows

These figures come only from the completed v2 comparison of **48 frozen synthetic orders**, documented in [EVAL_HELDOUT.md](EVAL_HELDOUT.md). That run used source-loaded native **0.3.0** in the evaluation container. This is historical evidence, not a new evaluation of published 0.3.3. The later sealed evaluation is incomplete; no sealed-set result or post-tuning improvement is claimed here. All orders are synthetic and deliver only to an IRIS simulator.

- **Correct routes:** rules-only **33/48**; agent + policy **33/48**, **33/48** and **30/48** across three trials. There was no overall accuracy gain, and one trial was worse.
- **Wrong deliveries:** rules-only recommended releasing **6/23** release-ineligible orders (counterfactual choices). Agent + policy made **2/23**, **3/23** and **3/23** actual wrong simulator deliveries.
- **False holds:** rules-only **9/25**; agent + policy **9/25**, **9/25** and **12/25**.
- **Unstructured exact routing:** **1/16** for rules-only and **1/16** for agent + policy in every trial. Five failed agent attempts remain counted.
- Review rose from **12.5%** (6/48) to **21.5%** (31/144 pooled agent trials). The same 48 cases repeat across trials; they are not 144 independent orders.

In short: fewer wrong deliveries, more holds and review, no gain in overall or unstructured routing accuracy.

## Why this design is deliberate

In commerce, a wrong delivery is costlier than an explained hold. The agent proposes; policy enforces; every committed decision is auditable in native Visual Trace and a signed receipt. The trade-off is intentional and should stay visible: the design is safer on this set, not more accurate.

[Full results, failures, timing and limits](EVAL_HELDOUT.md).
