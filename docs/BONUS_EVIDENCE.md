# Bonus evidence

Checked **2026-11-02** against the [official bonus announcement](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). The list may change. Scores below are available points, **not earned points**. Prioritize the mandatory native production and submission gates. No bonus is claimed yet.

| Bonus | Points | Published requirement | SilentShift evidence/status |
|---|---:|---|---|
| Embedded Python | 3 | Use Embedded Python | SOURCE_IMPLEMENTED / RUNTIME_BLOCKED: `src/SilentShift/Bridge.cls`, `python/silentshift/engine.py`; host tests pass, actual Embedded Python execution not observed |
| Docker | 2 | IRIS runs in Docker | SOURCE_IMPLEMENTED / RUNTIME_BLOCKED: `compose.yaml`, local-only `Dockerfile`, `scripts/bootstrap.py`; no running EAP or clean-start transcript |
| Custom adapter | 2 | Custom inbound/outbound adapter used in production | NOT_STARTED; ordinary Business Service alone is insufficient |
| Vector Search | 2 | Use IRIS vector search | NOT_STARTED; require actual retrieval and evidence |
| Workflow Engine | 2 | Use native Workflow Engine in production | NOT_STARTED; a custom review table alone is insufficient |
| YouTube | 3 | Product demonstration on YouTube | NOT_STARTED; local video alone is insufficient |
| Online demo | 2 | Cloud-hosted application demo | NOT_STARTED; require live IRIS workflow and accessible URL |
| ZPM/IPM | 2 | Publish installable package | NOT_STARTED; require public install command and test |
| Community Idea | 4 | Implement an idea marked Community Opportunity | NOT_STARTED; see scope below |
| First DC article | 2 | New article explains project/use | NOT_STARTED; require published URL |
| Second DC article | 1 | Second article or translation | NOT_STARTED; require published URL |
| Questionnaire | 1 | Submit feedback questionnaire | NOT_STARTED; require receipt |
| PEX | 3 | Java/.NET PEX in interoperability production | OUT_OF_SCOPE |
| AI Hub bugs | 2–3 | First reproducible report; second adds one point | NOT_STARTED; never invent a bug |
| Embedded Python bugs | 2–3 | First reproducible report; second adds one point | NOT_STARTED |

For any implemented row, add exact source paths, commands, observed output, screenshot/URL, date and remaining uncertainty before changing its status to VERIFIED. Organizer-awarded status is separate from local evidence.

## Community Opportunity scope

[DPI-I-439](https://ideas.intersystems.com/ideas/DPI-I-439), “Add support for AI-powered test automation,” displays Community Opportunity status. The requested idea concerns AI-supported testing within the IRIS testing framework. A possible extension proposes regression cases from reviewed semantic incidents, validates their schema, and executes them through deterministic IRIS tests. Merely generating test text does not demonstrate that capability. It is optional and unimplemented; defer it until P0 works. Recheck the live idea status before claiming eligibility.

## Unresolved organizer details

The bonus discussion has unanswered questions about multiple entries implementing one idea. The [contest discussion](https://community.intersystems.com/node/590306) still shows an unanswered build-154 public-IPM eligibility question at this check. AI Hub RAG retrieval can count for Vector Search according to the October 21 organizer clarification; static recorded REST responses cannot count for online demo. Seek clarification only if these features are actually pursued. No organizer message was sent by this research task.
