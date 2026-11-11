# A valid signature does not make an integration decision correct

An order can arrive successfully and still ask for the wrong thing. SilentShift's small example is an incoming `20 CASE` line against an approved `240 EA` commitment, without an approved conversion. The JSON is valid. The integration has accepted the message. The business comparison is still unresolved.

That is the problem SilentShift explores inside an IRIS Interoperability production. An AI Hub agent investigates the case using read-only evidence tools. A deterministic assessment and policy control routing. Human review is available for eligible holds, and the original payload, reference snapshots and outcomes remain inspectable. Everything in the demonstration is synthetic; delivery means the included destination simulator, not an external ERP.

The most useful recorded moment is not a perfect model answer. In one retained native case, the agent proposed ALLOW even though the incoming units contradicted the approved reference. The deterministic policy rejected release and the case was quarantined. In the approved-amendment case, a different effective reference allowed delivery. Both records are preserved. A walkthrough that replaced the bad proposal with an ideal answer would hide the reason for the policy boundary.

## Keep the authority outside the proposal

The agent can read the bound message, contracts, related records and similar precedents. It cannot grant itself permission to release an order. Missing citations, unresolved comparisons and critical contradictions are checked outside the model. A reviewer cannot use the review screen to bypass a critical contradiction.

This separation also matters when improving model output. An earlier approved-amendment repeat proposed ALLOW but omitted a required record from its citation manifest. The policy held it. The later local Ollama response-format constraint preserves the supplied evidence manifest; it does not append a citation after receiving an answer or change a failed policy check into a pass. It addresses an output-format failure, not general reasoning quality. The earlier failure remains in the evidence.

The held-out comparison is another useful limit. It did not establish better overall or unstructured routing than the plain-rule baseline. The later citation fix does not retroactively improve those results. Two working examples explain a mechanism; they do not establish accuracy on future partner feeds.

## Put provider calls in the business trace

SilentShift records provider exchanges as Interoperability request/response messages under the case session. That makes the proposal's model, provider, prompt version, timing, tool activity and outcome accessible alongside the routing and review steps. Unknown usage or cost remains unknown; an absent billing value is not a zero-cost measurement.

Live local Ollama investigations and keyless recorded responses are different modes. The keyless path exercises the production with recorded provider answers and makes no new model call. The public-package verification is useful precisely because a reviewer can run it without configuring a paid provider. It should never be presented as fresh inference.

This tracing work implements [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689). The README contains a reproducible example and a comparison with Langfuse. IRIS keeps the business workflow and native trace together. Langfuse remains a sensible choice when its evaluation, prompt-management and analytics capabilities are the main requirement.

## Add a receipt after the decision

Java PEX exports an integrity record after a routing operation commits its outcome. The payload includes the case ID, persisted decision, evidence hashes, original investigation mode and synthetic-data flag. Java computes its SHA-256 and signs the envelope with an instance-held RSA key.

Retries return the immutable original rather than create a new timestamp and signature. Receipt mode is derived from the persisted investigation; changing a server setting must not relabel an earlier case. Export failure is visible and leaves the committed route unchanged. That preserves routing behavior, but it also means an export outage can leave an audit gap. There is no claim of guaranteed recovery or tamper-proof storage.

A browser inspector now makes these limits tangible. It recomputes the payload hash, verifies the actual Java signature, and rejects an edited copy. It also distinguishes signature validity from signing identity. A public key embedded in a receipt cannot authenticate itself; an independent expected fingerprint is needed. Even a correctly pinned signature cannot prove the underlying contract was authoritative or the business decision was right.

## Make the evidence easy to read

The recorded-case tour lets a reader follow intake, reference authority, proposal/policy and receipt without starting IRIS. It retains actual saved values and source hashes. It does not synthesize new decisions, run a model or qualify as a hosted native demo.

The current native release is 0.3.2; the React workbench is built separately as 0.2.1. Only build 154U ARM64 is locally qualified. The single install guide and keyless launcher provide the native route for readers who want to inspect the production themselves.

[SilentShift on Open Exchange](https://openexchange.intersystems.com/package/SilentShift) · [Source and judge path](https://github.com/himanshu748/silentshift) · [Existing captioned demonstration](https://youtu.be/a4dOcqu89EA)

**Drafting note — remove before posting:** the new recorded tour/receipt utility must be merged and verified before this text is posted. Add their live URLs only after a separately approved Pages deployment. No hosted native demo URL exists. No article bonus beyond the existing first and second articles is requested. Posting remains gated.
