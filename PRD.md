# SilentShift

**Catch the lies hidden inside successful integrations.**

## User and outcome

An enterprise integration engineer must contain a transaction whose transport and schema succeed but whose meaning contradicts an independent approved business record. The operator needs inspectable evidence, a reproducible failure and a safe release path for legitimate changes.

The selected product is stable. This implementation is a single-tenant synthetic-data contest demonstrator, not a production ERP or a claim of market validation. It must use native InterSystems IRIS interoperability and AI Hub build 154. No external Python-to-LLM substitute, hidden mock endpoint, invented operational history or paid usage is acceptable.

## Primary journey

1. An authenticated operator selects a versioned Scenario Lab fixture or submits a bounded partner event.
2. An IRIS Business Service accepts and deduplicates it, preserving the original payload and receipt time.
3. A Business Process obtains independent reference records, performs Embedded Python checks, and invokes a native AI Hub investigation through an Operation.
4. The agent retrieves only case-scoped message, contract and related evidence and proposes structured `ALLOW`, `QUARANTINE` or `REQUEST_REVIEW` with citations and uncertainty.
5. Deterministic policy validates schema, evidence coverage and safety before a routing Operation creates a delivery or quarantine receipt.
6. The operator inspects the evidence and native trace. An authorized reviewer may release a held noncritical case only with a valid safe policy assessment, or reject it, with a reason and an idempotency key.

## Scope and acceptance

| Capability | Observable acceptance |
|---|---|
| Native foundation | Ingest through a real `Ens.BusinessService`, traverse a real `Ens.BusinessProcess`, and persist routing through Operations; capture trace IDs. |
| Native agent | Build 154 `%AI.Agent` makes read-only tool calls and returns a persisted structured proposal within bounded iterations. |
| Semantic assessment | Distinguish invalid, suspicious, verified contradiction, legitimate approved change, insufficient evidence and clear data; unusual values alone are not proof. |
| Safety | No critical contradiction, duplicate effect, malformed response, absent evidence or unverified transformation reaches downstream. |
| Reviews | Server-enforced reviewer resource, reason, optimistic version and idempotency; critical contradictions require corrected event/reference and a new investigation. |
| Five scenarios | Quantity units and currency scaling held; approved amendment allowed; conflicting peers reviewed; injected unsafe agent output blocked. Every native run records observed results. |
| Evidence | Original message, reference snapshot, findings, tool reads, raw/validated proposal, policy checks, timeline, routing and reviewer actions are inspectable. |
| Evaluation | Frozen fixture version and ground truth; rule-only, native proposal and final policy results, denominators, unsafe releases, reviews, false quarantine, latency and nullable usage. No unrun benchmark metrics. |
| Interface | Investigations, Scenario Lab, Overview, Messages, Evaluations, Policies and Health read real APIs; desktop/mobile, keyboard, loading, empty and disconnected paths verified. |
| Reproducibility | Source-only Docker setup, externally loaded official image, clean-install/native verification commands and explicit environment gates. |
| Submission | Public open-source repository, actual OEX application and separate verified contest entry before the official deadline. |

## Data and scenarios

Orders carry event/correlation IDs, source, occurrence time, contract, product, quantity, unit and business unit. Payments carry amount as a decimal string, currency and explicit major/minor scale. Quantity and amount accept exact decimal strings or integers; JSON floating-point business values are rejected because binary rounding can erase a contradiction. The server selects versioned reference records by contract, never trusts partner-provided references. Independent reference fixtures are synthetic, labeled and seeded separately from partner messages.

Required semantic coverage: quantity/unit, currency/scale, product mapping, business unit, timestamp semantics, stale events, duplicates, contracts and conflicting reference authority. Effective dates decide whether an approved amendment actually applies. Decimal arithmetic must not silently coerce malformed or nonfinite values.

The five frozen examples are demonstrations, not evidence of general accuracy. Adversarial scenario E tests the final validator with an explicitly labeled fault-injection proposal after a native investigation; it never silently pretends the model generated the adversarial response.

## Non-goals and constraints

No generic chatbot, monitoring clone, complete ERP, self-authorized transforms, unrestricted agent mutations, multi-tenant hosting, production reliability claim or speculative infrastructure. Optional vector search, custom adapters, workflow, IPM packaging and generated regression tests follow P0 proof. A video or online bonus cannot compensate for a broken native path.

## Release gate

The project remains incomplete until native runtime, scenarios, safety, clean setup and contest confirmation are observed. `docs/BUILD_STATUS.md` is the evidence ledger. Official rules, dates and unresolved eligibility are in `docs/CONTEST_COMPLIANCE.md`.
