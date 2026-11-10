# What a successful message can still get wrong

Draft for owner review. Not posted. The source links below refer to `push/top3`; merge or retain that branch before sharing them. There is no hosted demo URL to add yet.

---

An order arrives as `20 CASE`. The approved contract says `240 EA`. The JSON parses, the endpoint accepts it, and delivery could succeed. None of those facts establishes that the order means what the buyer approved.

That is the problem behind [SilentShift](https://openexchange.intersystems.com/package/SilentShift). It is a validation workbench for integration operations teams, built inside an InterSystems IRIS interoperability production. The useful question is not whether a model can invent a plausible CASE-to-EA conversion. It is whether the available approved evidence authorizes the change.

When an effective approved amendment authorizes `20 CASE`, the demonstrated route allows it. Without that authority, the order stays held. The operator can inspect the original message, selected references, investigation, policy result and simulator receipt together.

## The difficult boundary was authority

The native AI Hub agent reads four case-scoped tools: the current message, approved contracts, related records and similar precedents. It proposes a route with citations and uncertainty. It cannot write references, approve a review or deliver a message.

Deterministic policy owns the final route. Automatic delivery requires a valid ALLOW recommendation, resolved comparison and complete evidence. Critical contradictions cannot be approved by a reviewer. Human review is for eligible holds, with a reason, current version and idempotency key.

This distinction matters when a precedent looks convincing. A similar historical case can explain a recommendation. It cannot become current contract authority merely because a vector search ranked it highly.

## One AI Hub quirk needed a small workaround

On the tested ARM64 Community build, `2026.3.0AI.154.0 / 154U`, a valid quoted ObjectScript tool method named `find_similar_precedents` exposed a generator problem. Its declaration parsed, but the generated dispatcher emitted an unquoted call. A camel-case control compiled.

The reproduction contains two tiny classes and requires no model or network. It is filed as [AI Hub issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17); vendor confirmation remains pending. The application workaround overrides its own dispatcher, checks an exact tool-name allowlist and empty argument object, then invokes the quoted method. It does not modify a vendor class or grant a tool broader authority.

The review path also had to survive partial completion. Recording an approval and completing a native Workflow task are separate steps. If completion fails, the operator resumes the recorded decision with its original reason and key; that recovery must not manufacture another delivery.

## A trace needs the provider exchanges, not just the final answer

The implementation of [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689) wraps each admitted provider exchange in its own interoperability request and response. Those messages remain in the business case's native session, alongside evidence reads, policy and routing.

The metadata includes model, provider, prompt version, duration, tool names, outcome and available response usage. That makes it possible to distinguish a successful exchange from a failed call and connect both to the business result.

Token accounting needs restraint. Available usage belongs to the specific response that exposed it; a final SDK response is not automatically a session total. Unknown billing cost and provider retries remain null. Local Ollama avoids a paid model API for the tested path, but local compute is still a resource. Recorded playback reports no fresh inference or new token usage.

Langfuse remains a sensible choice for dedicated evaluations, prompt management and LLM dashboards. SilentShift's narrower contribution is putting provider messages and the integration's actual consequence in the same native trace.

## The comparison did not justify an accuracy headline

A plain rule baseline solves the original five examples. To test beyond them, I froze 48 synthetic orders and contractual labels before execution: structured contradictions, prose-dependent cases and clean false-positive traps. The labels were not changed after seeing results.

Rules-only returned 33/48 correct routes. Across three paired trials, agent-only returned 35/48, 34/48 and 31/48; agent plus policy returned 33/48, 33/48 and 30/48. The shipped route had fewer wrong simulator deliveries—2, 3 and 3 versus six counterfactual baseline release choices—but more false holds.

On unstructured routing, agent plus policy did not beat rules: both achieved 1/16 per trial. Five failed agent attempts remain counted. [Every failure, including cases where rules won, is listed](https://github.com/himanshu748/silentshift/blob/push/top3/docs/EVAL_HELDOUT.md).

The important limitation is that authoritative prose in the challenge set can conflict with structured reference columns. The shipped policy still treats those columns as authority. That can block a useful prose-based recommendation. The set is small, synthetic and implementation-aware; it is not independent customer-data validation.

## What I would change next

The next product question is how an operator establishes amendment authority and provenance. That needs a clearer contract and new evaluation cases, not a prompt tuned until these frozen labels pass.

For now, [the source and installation guide](https://github.com/himanshu748/silentshift/tree/push/top3) show the complete local workflow. Keyless replay exercises native orchestration with recorded responses; fresh investigations use local Ollama. The licensed runtime is obtained separately. CSV intake is bounded and requires independent source approval. All supplied examples are synthetic, and delivery remains inside the IRIS simulator.
