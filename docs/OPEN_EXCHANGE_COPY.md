# Open Exchange application copy

Release 0.2.0 copy, aligned with the current README. On November 4 the developer portal showed Published, the dedicated idea field and contest/IPM checkboxes were saved, public registry 0.1.0 metadata/manifest returned 200, and SilentShift appeared on contest 49. Current 0.2.0 moderation/install results are tracked in SUBMISSION_CHECKLIST.md.

## Fields to paste

### Application Name

SilentShift

### Short description

Catch wrong business meaning before delivery: native IRIS AI Hub investigation, deterministic policy and recoverable human review.

### Full Description

An order arrives as `20 CASE`. Its approved contract says `240 EA`. The transport succeeds and the JSON is valid, but there is no approved conversion explaining the change. SilentShift holds the order before delivery and gives the integration operator the original message, reference records and reason in one investigation.

The same incoming value can be legitimate. An effective approved amendment can authorize `20 CASE`; SilentShift checks that authority at event time rather than guessing a conversion. The payment example makes the same distinction for interface contracts: `12550` minor EUR units and `125.50` major units may be numerically equivalent, but that does not authorize a representation change.

### Investigate inside the native production

SilentShift runs its decision inside an InterSystems IRIS interoperability production:

```text
Partner Business Service → Semantic Business Process
  → reference, precedent and native AI Hub Operations
  → Embedded Python policy → destination or quarantine Operation
```

The native AI Hub agent reads four case-scoped, read-only tools: the current message, approved contracts, related records and similar precedents. It proposes a recommendation with evidence IDs and uncertainty. Deterministic Embedded Python policy authorizes the final route. A previous delivery, a helpful runbook or an agent's explanation cannot override a critical contradiction in current approved evidence.

### Give the operator a clear next action

The React evidence workbench keeps the original payload, immutable reference snapshot, actual tool reads, policy checks and delivery receipt together. Similar precedents expose real source IDs, outcomes and cosine scores from native IRIS Vector Search. They supply context without borrowing authority from an earlier decision.

Held cases become native IRIS Workflow tasks. Authorized reviewers can approve eligible cases or reject them with a reason, current version and idempotency key. Critical contradictions cannot be approved. If native completion fails after a decision is saved, **Resume recorded review** carries the original request forward. Each verified concurrent-approval and recovery journey produced one simulator delivery.

Partners can submit raw message JSON through the authenticated API or a custom native ready-file adapter. The adapter retains exact input bytes, records the native case and trace, and writes an acknowledgement from the persisted outcome. Replays reuse the original case and receipt. Each actual local provider HTTP exchange also appears as a typed request/response pair in its case's native Visual Trace, including a verified failure path. Version 0.2.0 also supplies an explicitly labeled recorded-provider example: the same native agent and four tools execute without a fresh LLM call or external API key. The critical order remains held. The README links DPI-I-689 and compares this transaction-centered trace with Langfuse's observability, evaluations, dashboards and prompt management.

### Run and inspect the demonstration

The verified runtime is official ARM64 Community AI Hub **2026.3.0AI.154.0 (154U)**, with local Ollama `qwen3-silentshift:4b-instruct` and local `all-minilm:22m` embeddings in 384-dimensional IRIS vectors. The backend also passed a clean local IPM installation without a source mount. After explicit setup, that installed production returned **5/5 expected final outcomes** and **4/5 expected agent proposals**, with all four native tools read.

All supplied orders, payments and references are synthetic. Delivery means a receipt in the included IRIS simulator. The five frozen scenarios are a coverage demonstration: the deterministic baseline also solves all five, so they establish no AI accuracy uplift or general production-readiness claim. No public hosted application is provided. Public IPM installation and the no-key recorded-provider recipe are documented separately, with their actual verification status in the README.

Start with [the operator walkthrough](https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_GUIDE.md): hold the unsupported unit change, allow the effective amendment, then inspect a review task and native Visual Trace. The [README](https://github.com/himanshu748/silentshift#native-build-154-setup) provides exact runtime, model, installation and verification commands. The licensed EAP runtime and model weights are obtained separately.

Source: [github.com/himanshu748/silentshift](https://github.com/himanshu748/silentshift)

Demo video: `https://youtu.be/a4dOcqu89EA`

### Tags

```text
AI Hub, Interoperability, Embedded Python, Workflow Engine, Vector Search, ObjectScript, Python, Docker, IPM
```

### URLs and selections

| Field | Value |
|---|---|
| GitHub/GitLab URL | `https://github.com/himanshu748/silentshift` |
| About URL | `https://github.com/himanshu748/silentshift` |
| Documentation URL | `https://github.com/himanshu748/silentshift/blob/main/docs/JUDGE_GUIDE.md` |
| License URL | `https://github.com/himanshu748/silentshift/blob/main/LICENSE` |
| YouTube URL | `https://youtu.be/a4dOcqu89EA` |
| Ideas Portal link | `https://ideas.intersystems.com/ideas/DPI-I-689` |
| Call to Action label | `Run SilentShift` |
| AI / ML selections | Select both; the application uses native agent inference and neural embeddings. |
| Submit to Contest | Check for **InterSystems Programming Contest: AI Agents in Interoperability Workflows**. |
| Publish in Package manager | Keep checked. Public 0.1.0 metadata exists; current 0.2.0 installation results are in the release ledger. |
| Demo URL | Leave empty: there is no hosted application. Put the published video in YouTube URL. |
| Community Article URL | [Semantic validation](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [Workflow recovery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery); both submitted for moderation; verify the canonical associations after approval. |

## 0.2.0 release notes

Expose each local AI Hub provider exchange in the business-case Visual Trace, with explicit provider/model/prompt version, operation timing, available response tokens, safe HTTP errors and retry/fallback boundaries. Add a no-key recorded-provider example through the same queued operation, native agent and four read-only tools; replay is labeled and cannot release the critical synthetic case. Package 44 classes and ten assets with IPM 0.10.10 requirements. Verified target remains official ARM64 2026.3.0AI.154.0 (154U); five live final routes and the corrected native suite/replay passed. The README provides exact commands and a fair comparison with Langfuse.

## Release actions

1. Push the fully checked 0.2.0 source to main.
2. Developer Portal → My Applications → SilentShift → ellipsis → Add new release → Add new release. Enter 0.2.0, November 4, 2026 and the notes above. Publish the new release; preserve the existing app and any moderation request.
3. Edit SilentShift, refresh the full description from the pushed README, preserve checked Submit to Contest and Publish in Package Manager, preserve the dedicated DPI-I-689 field and current video, then Save.
4. Read back release status. Verify public 0.2.0 metadata, perform the clean public registry install in IPM.md and confirm SilentShift remains listed in contest 49. Pending approval is a separate state from a published registry package.

The [official submission guide](https://docs.openexchange.intersystems.com/apps/submit/), [contest paths](https://docs.openexchange.intersystems.com/contest/apply/) and [IPM publication guide](https://docs.openexchange.intersystems.com/apps/ipm/) describe the portal workflow. No direct registry password or publishing API is invented.
