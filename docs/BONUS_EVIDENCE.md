# Bonus evidence

Checked **2026-11-03** against the [official bonus announcement and organizer replies](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). The list may change. **5 potential points have local implementation evidence; organizer awards are unconfirmed.** Future points below are not earned. Bonuses are described as voting points, not a published weighting of the five Expert Jury dimensions.

| Bonus | Points | Published requirement | SilentShift evidence/status |
|---|---:|---|---|
| Embedded Python | 3 | Use Embedded Python | LOCALLY_VERIFIED / AWARD_UNCONFIRMED: [Bridge.cls](../src/SilentShift/Bridge.cls), [engine.py](../python/silentshift/engine.py); actual production assessments/policy in the five-case native and fresh-install records |
| Docker | 2 | IRIS runs in Docker | LOCALLY_VERIFIED / AWARD_UNCONFIRMED: official ARM64 Community154U, gateway and bootstrap; fresh-volume empty start and run `0503b649-ee6f-495e-be37-166db508377c` passed |
| Custom adapter | 2 | Custom inbound/outbound adapter used in production | NOT_STARTED; ordinary Business Service alone is insufficient |
| Vector Search | 2 | Use IRIS vector search | NOT_STARTED; require actual retrieval and evidence |
| Workflow Engine | 2 | Use native Workflow Engine in production | NOT_STARTED; a custom review table alone is insufficient |
| YouTube | 3 | Product demonstration on YouTube | NOT_STARTED; local video alone is insufficient |
| Online demo | 2 | Cloud-hosted application demo | NOT_STARTED; require live IRIS workflow and accessible URL |
| ZPM/IPM | 2 | Publish installable package | NOT_STARTED; require public install command and test |
| Community Idea | 4 maximum | Implement a Community Opportunity idea | IN_PROGRESS / UNAWARDED: user-authorized DPI-I-689 trace work has started; evidence gate below is not yet satisfied |
| First DC article | 2 | New article explains project/use | NOT_STARTED; require published URL |
| Second DC article | 1 | Second article or translation | NOT_STARTED; require published URL |
| Questionnaire | 1 | Submit feedback questionnaire | NOT_STARTED; require receipt |
| PEX | 3 | Java/.NET PEX in interoperability production | OUT_OF_SCOPE |
| AI Hub bugs | 2–3 | First reproducible report; second adds one point | NOT_STARTED; never invent a bug |
| Embedded Python bugs | 2–3 | First reproducible report; second adds one point | NOT_STARTED |

Local proof is retained in `evidence/native/clean-install-initial.json`, `evidence/native/clean-install.json`, the native run/evaluation records, and `evidence/browser/browser-scenario-delivered.png`. These are private/ignored artifacts, not public proof URLs. Publish reviewed evidence extracts with the source and installation guide; retain the actual OEX bonus decision separately. See [BUILD_STATUS.md](BUILD_STATUS.md) for the current ledger and [CONTEST_COMPLIANCE.md](CONTEST_COMPLIANCE.md) for submission gates.

## DPI-I-689: useful extension, not four points already earned

[DPI-I-689 — Use InterSystems Interoperability as a Traceability tool for GenAI LLM pipelines](https://ideas.intersystems.com/ideas/DPI-I-689) has Community Opportunity status in the November 3 research. Semion Makarov's replies to Aziz Cotrim and MxSalata on the [official bonus page](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows) clarify:

- Vector Search is optional for this idea.
- Multiple entries may implement the same idea.
- The idea bonus is capped at 4 per entry, irrespective of the number of ideas.
- Link the implemented idea in README and OEX's dedicated idea-link section; provide a reproducible LLM-metadata Visual Trace example. A Langfuse comparison is helpful context.

**Current gap / work in progress:** The user has authorized the trace-bonus implementation. At this documentation checkpoint, SilentShift's trace/session/audit data does not yet provide verified prompt-version attribution and explicit spans for each provider call. A case trace ID or a tool-event list alone does not substantiate the implementation. The four points remain unclaimed; later observed trace evidence must replace this checkpoint before claiming satisfaction.

The engineering acceptance gate is to make actual provider calls inspectable in native Visual Trace, correlated with the case/session and model/prompt version, including observed latency, tool/retrieval events, errors, retries and fallback. Usage/cost must stay null where the runtime does not expose them. Retain a successful example and a failure example with reproducible commands, a trace screenshot, a metadata-field map and a short comparison of the supported scope with Langfuse. This is SilentShift's proposed evidence standard, not an assertion that every optional observability feature is required by the organizer. Redact credentials and bound payloads before publication.

The original [DPI-I-439](https://ideas.intersystems.com/ideas/DPI-I-439) AI-test-automation extension stays deferred. Generating test prose is insufficient, and implementing a second idea cannot add another four points. Do not expand scope merely to collect a second idea link.

## Prioritized points roadmap

The totals are **conditional planning arithmetic**, not awarded or guaranteed scores. No feature, publication, questionnaire or external action was completed by writing this document.

| Order | Concrete completion gate | Additional potential points | Conditional total including current 5 |
|---|---|---:|---:|
| 0 | Finish the judge pack, publish reviewed source, complete OEX application and separately verify contest entry | Eligibility first | 5 locally supported, awards unconfirmed |
| 1 | Implement and observe the DPI-I-689 trace gate above; README/OEX links and reproducible evidence | 4 | 9 |
| 2 | Publish a truthful YouTube demonstration of the actual native journey | 3 | 12 |
| 3 | Publish a new DC article explaining the product, setup and evidence | 2 | 14 |
| 4 | Publish a second distinct DC article or translation | 1 | 15 |
| 5 | Submit the official feedback questionnaire and retain its confirmation | 1 | 16 |

This is a possible **16-point route only if every requirement is satisfied and accepted**. Draft materials locally first. Articles, video publication and questionnaire submission need the user's applicable explicit authorization; this roadmap does not grant it. Generated narration, if used, must use Deepgram under the standing agreement. Do not add paid model calls, hosting, purchases or billing changes.

Custom adapter, native Workflow Engine, Vector Search and IPM remain lower-priority options: each must improve the actual product and be executed/verified. The current custom review records do not establish native Workflow Engine usage. A source manifest does not establish a published IPM package. An online-demo bonus needs live IRIS; a static replay site does not qualify. These options are excluded from the conditional 16 above.

## Resolved and remaining external details

- The formerly unanswered IPM question now has an organizer response on the [contest announcement](https://community.intersystems.com/node/590306): publish on IPM, include `<SystemRequirements Version=">=2026.3" Interoperability="enabled"/>`, and verify registry installation on the declared supported runtime. The reply names build154; a subsequent reply permits declared Community109 with corresponding judge setup. SilentShift remains verified only on154.
- AI Hub RAG may count as IRIS Vector Search; this does not mean SilentShift currently implements it.
- The contest page's “0 Bonuses” display for all eight listed entries is not a validated score audit. No competitor's bonus eligibility or final award was independently confirmed.
- Native repairs or crashes are not automatically reproducible vendor bugs or earned bug bonuses. No bug report, article, questionnaire or organizer message was sent by this documentation task.
