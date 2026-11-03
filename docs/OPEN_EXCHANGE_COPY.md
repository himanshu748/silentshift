# Open Exchange application copy

The fields below were saved to [SilentShift 0.1.0](https://openexchange.intersystems.com/package/SilentShift) on November 4, 2026. The portal confirmed **Your application was sent for approval successfully** and **Sent for approval**. The application page shows **Awaiting Review**. Contest entry and public registry availability remain unconfirmed.

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

Partners can submit raw message JSON through the authenticated API or a custom native ready-file adapter. The adapter retains exact input bytes, records the native case and trace, and writes an acknowledgement from the persisted outcome. Replays reuse the original case and receipt. Each actual local provider HTTP exchange also appears as a typed request/response pair in its case's native Visual Trace, including a verified failure path.

### Run and inspect the demonstration

The verified runtime is official ARM64 Community AI Hub **2026.3.0AI.154.0 (154U)**, with local Ollama `qwen3-silentshift:4b-instruct` and local `all-minilm:22m` embeddings in 384-dimensional IRIS vectors. The backend also passed a clean local IPM installation without a source mount. After explicit setup, that installed production returned **5/5 expected final outcomes** and **4/5 expected agent proposals**, with all four native tools read.

All supplied orders, payments and references are synthetic. Delivery means a receipt in the included IRIS simulator. The five frozen scenarios are a coverage demonstration: the deterministic baseline also solves all five, so they establish no AI accuracy uplift or general production-readiness claim. A public hosted application and public IPM registry installation are not provided.

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
| Publish in Package manager | Checked in the saved approval request. Clean local installation verified; public registry publication/install unverified. |
| Demo URL | Leave empty: there is no hosted application. Put the published video in YouTube URL. |
| Community Article URL | [Semantic validation](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [Workflow recovery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery); both submitted for moderation and associated with the app. |

## Saved submission and remaining clicks

1. Completed: **My Applications → SilentShift → Edit → Save**, with the video URL, dedicated DPI-I-689 field, contest selection and Package Manager option. Both original article URLs are saved in **Community Article URL**. The technical rewrites changed their slugs; canonical links are in the table above and need a final association/redirect check.
2. Completed: **Send for approval → New version 0.1.0 → Release date November 4, 2026 → release notes → Send**. The portal returned **Your application was sent for approval successfully** and now offers **Cancel approval**. Do not cancel or create a duplicate application.
3. Pending: after moderation publishes the app, open [contest 49](https://openexchange.intersystems.com/contest/49) → **Apply → SilentShift → complete entry**. Keep the separate contest confirmation. The actual current Apply dialog says this account has no published app and requires publication before selection.
4. Pending: verify both article moderation results and the public IPM listing/install. The saved Package Manager checkbox and displayed IPM badge alone do not prove registry availability.

The [official submission guide](https://docs.openexchange.intersystems.com/apps/submit/), [contest paths](https://docs.openexchange.intersystems.com/contest/apply/) and [IPM publication guide](https://docs.openexchange.intersystems.com/apps/ipm/) describe separate gates. See [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) for points and the remaining order of work.
