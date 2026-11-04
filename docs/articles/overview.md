# Catching semantic failures in an IRIS interoperability production

An integration accepts an order for `20 CASE`. The JSON parses, the required fields are present, and the destination is reachable. The approved contract, however, specifies `240 EA`.

A developer might recognize a plausible explanation: twenty cases of twelve items. That explanation becomes dangerous when the integration treats it as permission. The message contains no approved pack size, and a plausible conversion does not establish what the partner agreed to send.

SilentShift holds that order before delivery and assembles the evidence an integration operator needs to resolve it. It runs inside an InterSystems IRIS interoperability production, using a native AI Hub agent to investigate and Embedded Python policy to authorize the route. The examples below use synthetic transactions and an IRIS destination simulator.

## Define the business commitment before asking the model

The central comparison is between a message and the approved reference records effective when its business event occurred. A surprising value alone proves very little.

Consider two investigations with the same incoming quantity and unit:

| Incoming order | Reference evidence at event time | Required outcome |
| --- | --- | --- |
| `20 CASE` | Active approved contract requires `240 EA`; no authorized transformation | Hold the contradiction |
| `20 CASE` | Approved amendment requires `20 CASE`; its predecessor has expired | Permit delivery when the remaining release checks pass |

The second row prevents the detector from becoming a blanket change blocker. An old value differs, but the business has authorized the new one.

The [assessment engine](https://github.com/himanshu748/silentshift/blob/main/python/silentshift/engine.py) makes this distinction before routing. Reference validity uses a half-open interval:

```text
effective_from <= occurred_at < effective_to
```

An open-ended reference omits the upper bound. Overlapping approved records that disagree produce unresolved evidence; the engine cannot select whichever record makes delivery convenient. An amendment must also have a retrieved approved predecessor with a valid temporal relationship. Matching the current value is insufficient if that lineage is missing.

Authority is explicit. Reference records come from the server's reference store; message fields cannot promote themselves to approved evidence. Peer records may expose a concern, but even agreeing peers cannot grant release authority.

Representation also belongs to the contract. In the payment example, `12550` minor EUR units and `125.50` major units describe the same numeric amount after a conversion. An interface expecting major units can still receive the wrong representation. SilentShift compares the declared amount and scale using exact decimal values and preserves the original payload. Its normalization helpers do not repair or rewrite a transaction during routing.

## Give the agent a bounded investigation

The agent helps the operator connect the message, reference records and relevant history. Its tools expose four narrow reads:

| Tool | Evidence it contributes |
| --- | --- |
| `GetCurrentMessage` | The transaction under investigation |
| `GetApprovedContracts` | Approved contract evidence for that case |
| `GetRelatedRecords` | Related records already bound to the investigation |
| `find_similar_precedents` | Up to three resolved cases or approved amendments, with source IDs and similarity scores |

The [tool implementation](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/AI/EvidenceTools.cls) binds access to a server-selected case. The model cannot supply an arbitrary case ID, execute SQL, amend a contract or call the destination.

The native `%AI.Agent` reads those tools and returns a small proposal: `decision`, `evidence_ids`, `explanation` and `uncertainty`. The allowed decisions are `ALLOW`, `QUARANTINE` and `REQUEST_REVIEW`. The response is parsed and validated before it can influence routing. Unknown evidence IDs, an unexpected schema or malformed output cannot become a release decision.

The local agent uses Ollama `qwen3-silentshift:4b-instruct` with a six-iteration session limit. The current [`Investigator`](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/AI/Investigator.cls) requests at most **192 output tokens per exchange**; the [`provider ingress`](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Provider/API.cls) independently rejects budgets above **700 tokens**. The admission ceiling is separate from the configured request budget, and neither is a measured session total. The enclosing production wait is separately bounded; expiry leaves the case held. That timeout does not establish that the provider has cancelled its work.

## Keep relevance separate from authority

Precedent retrieval answers a useful operator question: has a similar case been resolved before? Local `all-minilm:22m` embeddings populate 384-dimensional native IRIS `VECTOR` columns; cosine search returns source records and scores.

A high score measures similarity. It cannot establish that the current partner has an approved conversion, that an amendment was effective at this event time, or that yesterday's release applies today.

SilentShift therefore keeps precedent retrieval outside the authoritative contract comparison. A retrieved delivery can inform the recommendation and guide the operator to a prior resolution. It cannot remove a critical finding. A [native veto test](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/precedent-veto.json) retrieved earlier deliveries and then supplied a valid-looking `ALLOW` proposal for a current critical contradiction. Policy retained the hold.

This boundary lets retrieval add context without making historical mistakes self-reinforcing.

## Authorize delivery at the production boundary

The processing path stays inside IRIS:

```text
Partner Business Service
  → Semantic Business Process
      → reference reads + native AI Hub investigation
      → Embedded Python assessment and policy
  → destination Operation OR quarantine/review
```

The agent's proposal passes through [`validate_policy`](https://github.com/himanshu748/silentshift/blob/main/python/silentshift/engine.py). Automatic delivery requires a resolved comparison to approved evidence, a complete valid recommendation, all required evidence citations, uncertainty at or below `0.35`, and no critical contradiction or duplicate event. The agent must also propose `ALLOW`.

A model concern can keep an otherwise eligible case in review. It cannot turn inconclusive evidence into a verified business contradiction. Conversely, an optimistic explanation cannot release a case that deterministic assessment has classified as critical.

The destination [rechecks authorization](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Store.cls) before persisting a unique simulator receipt. This matters because the final effect deserves its own guard, even when earlier processing has already evaluated policy.

For the operator, the result is one investigation containing the original payload, reference snapshot, tool reads, policy checks and destination receipt. Eligible holds can proceed through native Workflow review; critical contradictions remain blocked from approval. The [companion article](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery) follows the failure and recovery behavior of that human decision.

![An approved amendment and its simulator delivery in SilentShift](https://raw.githubusercontent.com/himanshu748/silentshift/main/docs/assets/native-approved-delivery.png)

## Trace the recommendation to the business outcome

An operator investigating a held order needs to distinguish a provider failure, a missing reference, an invalid proposal and a deliberate policy veto.

SilentShift records each actual local LLM HTTP exchange as a typed interoperability request/response pair in the original case session. Visual Trace connects those pairs to native tool reads and the final route. The [recorded examples](https://github.com/himanshu748/silentshift/blob/main/docs/AI_TRACING.md) include a successful investigation and a real upstream HTTP 400 that left the case held with zero deliveries.

Persistent provider messages contain metadata rather than raw prompt and response bodies: model, instruction version, correlation, duration, HTTP outcome and bounded tool-call metadata. Usage belongs to the particular response when available. Session totals, billing cost and provider retry classification remain unavailable. These distinctions prevent a trace from implying measurements it never collected.

## Read the result at two levels

The [clean installed production run](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/ipm-clean-install.json) produced four of five expected model proposals and all five expected final routes. The approved amendment delivered once; the other four cases had zero deliveries. In the conflicting-reference case, the model proposed quarantine while deterministic policy preserved the required review route.

Those results test two different contracts: whether the agent produced the expected proposal, and whether the application contained or delivered correctly. Reporting only the final five-of-five result would hide the model disagreement.

The five frozen scenarios are also solved by the rule-only baseline. They demonstrate the integrated investigation and containment behavior; they do not establish an AI accuracy improvement or production readiness. External destinations, broader datasets and production capacity remain untested.

To inspect the difference yourself, follow the [native build-154 setup](https://github.com/himanshu748/silentshift#native-build-154-setup), then run scenarios A and C in the workbench. Compare their effective references before reading the recommendation. A should remain held; C should have one simulator receipt. The [2:30 captioned demo](https://youtu.be/a4dOcqu89EA) shows that sequence and the native components behind it.

[Open Exchange application](https://openexchange.intersystems.com/package/SilentShift) · [Source and installation](https://github.com/himanshu748/silentshift) · [Reproduction guide](https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_GUIDE.md)
