# SilentShift: B2B order validation pilot

**Proposed product direction, November 6, 2026.** This is a pilot specification, not shipped functionality or customer validation. The contest build remains frozen: app 0.2.1, native IPM 0.2.0, verified IRIS 2026.3.0AI.154.0 / 154U ARM64. Existing execution evidence stays in [JUDGE_VERIFICATION.md](JUDGE_VERIFICATION.md).

**Implementation started locally:** the [CSV prototype](../pilot/README.md) prepares bounded feeds and imports independent approved references into the native production. It submits individual order lines through the existing agent and policy, preserving event identity and source provenance. It remains separate from the public IPM package. Whole-order enforcement, X12 and hosting remain unimplemented; current verification is recorded in [BUILD_STATUS.md](BUILD_STATUS.md).

## Customer and job

An integration operations team receives partner orders through an existing EDI translator, file exchange or API. Before those orders enter fulfillment, the team needs to identify unsupported changes to quantity, unit, product, business unit or effective order terms, and explain why an order is held.

The initial buyer and user hypothesis is the integration operations lead at a distributor or manufacturer. This audience and willingness to adopt have not been validated with interviews or a pilot.

### Reach buyers beyond IRIS installations

Position the product around the partner-order workflow, with CSV/API boundaries that fit the team's existing translator and ERP. IRIS remains an implementation dependency operated by the supplier or an agreed deployment partner; customers should not need IRIS expertise to interpret a discrepancy. This distribution model is proposed and depends on suitable runtime licensing, deployment and support. The current source distribution still requires an operator-managed IRIS installation.

The initial prospect hypothesis is a team with recurring manual order exceptions, a named owner of the approved reference data and authority to evaluate a de-identified feed. Target one feed and one exception workflow before proposing a platform replacement. A larger enterprise deployment may require procurement, security review, reference-data governance and integration ownership; none of these sales-cycle assumptions has been measured for SilentShift.

Use a bounded shadow assessment to test demand before investing in broader format support or a hosted service. The commercial decision is whether the team finds the discrepancies useful enough to sponsor a pilot. Production delivery control comes later. No pricing, customer commitments, shortened sales cycle or return on investment is established.

**Proposed positioning:** SilentShift checks incoming B2B orders against approved order records before fulfillment. When an order disagrees, operators see the original value, the authoritative reference and the reason for the hold. An effective approved amendment can explain a legitimate change; a past delivery cannot authorize a new one.

## Start with one CSV order feed

Use one partner, one documented CSV layout and one independently sourced approved-order export. The partner feed and authority export must not be derived from each other. Obtain a de-identified historical sample with known accepted orders, genuine discrepancies and approved changes; if only synthetic files are available, label the exercise a format demonstration.

The first pilot should run in shadow mode beside the existing integration: produce a discrepancy queue and proposed disposition without controlling ERP or warehouse delivery. Shadow mode is proposed and requires implementation and qualification; it does not remove runtime licensing requirements.

| Boundary | Required behavior before pilot use |
| --- | --- |
| File intake | Pin encoding, delimiter, quoting, required headers, file/row limits and mapping version; preserve original file hash and row number |
| Business identity | Bind partner, source event, order and line IDs; distinguish an exact repeat from changed content under an existing identity |
| Numeric values | Keep quantities as exact decimal strings and units explicit; never infer a pack conversion from numeric coincidence |
| Time | Preserve the source timestamp and timezone; select references effective at event time; label late arrivals explicitly |
| Approved references | Import a separately supplied order/line reference with revision, approval provenance and effective interval; conflicting authority requires review |
| Normalization | Produce the existing bounded internal event from an explicit mapping; preserve source values alongside normalized values |
| Whole-order result | Hold the order when any line is unresolved; do not equate a per-line case result with atomic whole-order delivery |
| Operator review | Show source row, current and approved values, reference revision, decision and reason; preserve critical-release veto, versioning and idempotency |
| Export | Emit shadow results keyed by source file/order/line; no downstream mutation or automatic correction in the initial pilot |

The current engine models one product/event per case. The CSV prototype adds transactional reference import, immutable revisions and a submitted-line summary; it does not enforce whole-order delivery or prove that a feed contains every line. Existing JSON ready-file intake is [verified](PARTNER_INBOX.md). The complete customer-pilot contracts above have not been qualified.

## Add X12 through a trading-partner mapping

X12 identifies **850** as the Purchase Order transaction set. Its [official overview](https://x12.org/node/4392) and [basic purchase-order example](https://x12.org/examples/004010x357/example-01-basic-purchase-order) are references for scoping; they do not establish a complete partner implementation guide.

Prefer the team's existing EDI translator to produce the canonical order input. Qualify one declared transaction version and trading-partner guide before supporting another. Keep envelope/control identifiers, order/line identity and translator mapping version in provenance. Do not advertise general EDI/X12 support from a handwritten segment splitter or a single sample. A native X12 parser, acknowledgements and transport protocols would each need their own scope and validation.

## Separate deployment access from product proof

| Gate | Evidence required |
| --- | --- |
| Runtime portability | Qualify a currently obtainable vendor build in a separate environment using full native tests, keyless replay, live local-model cases, Workflow, vector search and file intake; retain exact version/architecture outputs |
| Current build declaration | Continue declaring only tested 154U until the new build passes. Neither a compile nor a health response establishes compatibility |
| Hosting rights | Written vendor confirmation or a licence explicitly allowing the intended hosted demonstration/pilot; the existing [EAP hosting review](HOSTING_REVIEW.md) leaves this unresolved |
| Hosted replay demo | Run the real IRIS application under that licence, show a persistent replay banner, isolate/reset synthetic data and prevent public review mutations; verify the complete browser/API journey |
| Live partner data | Use a separately authorized private environment with agreed access, retention and deletion; keep it separate from a public synthetic demo |
| Downstream delivery | Define whole-order release and destination idempotency/acknowledgement semantics, then test uncertain outcomes before enabling effects |

No host, subscription, runtime upgrade or deployment is authorized by this specification. A hosted replay demonstration would improve access, while a real-data shadow pilot would establish whether the checks help the team's workflow. Those are separate milestones.

## Pilot acceptance

Freeze the sample and expected labels before the qualification run. The integration owner adjudicates each suspected discrepancy against actual approved records; unresolved labels stay unresolved. Record every input row, case and order outcome, including parse failures and missing references.

Measure discrepancy precision, missed known discrepancies, review rate, time to resolve an exception, throughput and latency, each with its denominator and workload. Compare the same labeled orders with the team's existing checks or a declared rule-only baseline. Record agent-off and agent-on behavior separately; do not call the five synthetic contest cases a production accuracy benchmark.

Before enabling any delivery effect, demonstrate that:

- An unsupported change holds the entire order, while an effective approved amendment permits the intended change.
- A missing/conflicting reference, malformed input or unavailable model cannot create an automatic release.
- Exact replays create no duplicate order effect; changed input under the same identity is visibly rejected or treated as an explicit revision.
- Review records survive restart and concurrent decisions produce one permitted effect at most within the declared destination contract.
- The operator can trace each conclusion back to the source row and the independently approved reference.

These are acceptance requirements, not results already obtained on customer data.

## Immediate next deliverable

Qualify the bounded CSV connector and independent approved-order import on an authorized de-identified feed. Agree the trading-partner mapping and approval provenance first, then compare discrepancy results with adjudicated examples. Keep whole-order delivery, X12 breadth, public hosting and real downstream effects as separate gates.

The missing external inputs are one representative order-feed layout, its independent approved-reference layout and a source of adjudicated examples. No customer data or operational impact is currently claimed.
