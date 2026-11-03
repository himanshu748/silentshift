# Open Exchange application copy

Prepared locally for the user to paste. Source is public; the Open Exchange application remains an earlier saved draft. This document does not submit, publish or register anything.

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

Demo video: `<YOUTUBE_VIDEO_URL>`

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
| YouTube URL | `<YOUTUBE_VIDEO_URL>` |
| Ideas Portal link | `https://ideas.intersystems.com/ideas/DPI-I-689` |
| Call to Action label | `Run SilentShift` |
| AI / ML selections | Select both; the application uses native agent inference and neural embeddings. |
| Submit to Contest | Check for **InterSystems Programming Contest: AI Agents in Interoperability Workflows**. |
| Publish in Package manager | Check when the user requests public IPM publication; a clean local installation is verified, but public registry publication/install remain unverified. |
| Demo URL | Leave empty: there is no hosted application. Put the published video in YouTube URL. |
| Community Article URL | Leave empty until an article is actually published. |

## Preparation notes — do not paste into the description

- Replace `<YOUTUBE_VIDEO_URL>` only after the uploaded video's playback and access are checked. Remove its description line if submitting without a published video; never paste a placeholder into a live URL field.
- The future public application URL is `<OPEN_EXCHANGE_APP_URL>`. Obtain it from the accepted public application page. The portal's private edit URL is not the application link for an article or README.
- Use only offered technology/category choices that match the implementation. Tags can be selected or created. All five extension receipts are linked from [the bonus evidence](BONUS_EVIDENCE.md); they are engineering evidence, not awarded points.
- The short description is a separate catalog field. Paste only its sentence, not the section heading. Copy the Full Description from its first paragraph through its demo line; the later tables and manual steps are preparation material.

## Manual approval and contest clicks

These are instructions for the user, verified read-only against official documentation on **November 4, 2026**. No click below has been performed by this preparation work.

1. Sign in to [Open Exchange](https://openexchange.intersystems.com/), open the avatar menu and enter **Developer portal**. Open the applications list: the submission guide calls it **All applications**; the editing guide calls it **Your Applications**. Select the existing **SilentShift** draft or its edit action. Create **New Application** only if that draft is absent. [Official editing route](https://docs.openexchange.intersystems.com/apps/update/), [submission route](https://docs.openexchange.intersystems.com/apps/submit/).
2. Paste the fields above. Recheck any content populated from GitHub, then set the contest checkbox and dedicated Ideas Portal link. Add only real published resource URLs. Request package-manager publication only if choosing to proceed with that separate external step. [Official field and package-manager guidance](https://docs.openexchange.intersystems.com/apps/submit/), [IPM publication guide](https://docs.openexchange.intersystems.com/apps/ipm/).
3. Click **Save**, then **Preview**. Inspect the rendered description, source/setup links, technology selections, idea link and any video. Saving retains a draft; previewing does not publish it. [Official draft/preview behavior](https://docs.openexchange.intersystems.com/apps/submit/).
4. When ready to request moderation, click **Send for Approval**. Retain the confirmation and status shown by the portal. This requests review; publication occurs after acceptance. For later edits to an already public app, the documented choices are **Send edits** for information changes or **Release app** when deliberately creating a release. [Initial approval](https://docs.openexchange.intersystems.com/apps/submit/), [later edits](https://docs.openexchange.intersystems.com/apps/update/).
5. Treat contest registration as a separate gate. The standard documented path is [contest 49](https://openexchange.intersystems.com/contest/49) → **Apply** → select the application. The public application's **Contest** tab or the developer-portal application dropdown are documented alternatives. Read back and retain an actual contest-entry confirmation; the saved checkbox or application approval request alone does not prove registration. [Official contest paths](https://docs.openexchange.intersystems.com/contest/apply/).
6. The standard contest guide assumes a published app. For this event, the organizer permits submission before Open Exchange approval, provided the package works during evaluation. The actual pending-approval registration path remains unverified; if the portal blocks selection, preserve that state and use the official contest channel for clarification. Do not assume the approval request registered the entry. [Contest-specific organizer clarification](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-interoperability-workflows).

After acceptance, replace `<OPEN_EXCHANGE_APP_URL>` in the README and both article drafts with the real public URL, verify it without editor privileges, and record application publication and contest registration separately.
