# Manual submission checklist

Deadline: **November 9, 2026 at 10:29:59 IST** — November 8 at 23:59:59 EST on the [official contest page](https://openexchange.intersystems.com/contest/49). Publication and bonus sources were rechecked on **2026-11-04**. These are the user's manual steps. No upload, approval request, article publication, registry publication or contest submission was performed by this documentation update.

## Prepared materials and verified state

| Item | Evidence / boundary |
|---|---|
| Source | [Public GitHub main](https://github.com/himanshu748/silentshift), verified features through `c68d10c`; MIT license and root `module.xml` |
| Native product | Official ARM64 AI Hub build 154U; four-tool agent, policy/routing, native review, vector precedents and file adapter verified locally |
| Clean IPM install | Real offline install of the inspected 43-class/nine-asset package; manager origins and installed native 5/5 passed. [Receipt](evidence/ipm-clean-install.json). Public registry unverified |
| Quality gate | 172 Python checks; TypeScript/build, 32 disconnected/landing and 16 native browser checks. [Final gate](evidence/step5-gate.json) |
| Judge materials | [Walkthrough](JUDGE_GUIDE.md), [application copy](OPEN_EXCHANGE_COPY.md), [demo plan](DEMO_SCRIPT.md), [YouTube copy](YOUTUBE_UPLOAD.md), [overview](articles/overview.md), [engineering article](articles/engineering.md) |
| Open Exchange | Earlier [saved draft](https://openexchange.intersystems.com/portal/products/SilentShift/edit); no approval-request or contest-entry confirmation observed |
| Video | READY: [silentshift-demo.mp4](../evidence/video/silentshift-demo.mp4), 150 seconds, 1080p H.264/30fps, AAC silence, burned-in/embedded captions and SRT; 3,561,558 bytes. Full decode, caption readback and sampled-frame inspection passed. No upload performed |
| Questionnaire | Already submitted with the user's answers; [confirmation](assets/questionnaire-submitted.png). No repeat submission needed |

Keep `<YOUTUBE_VIDEO_URL>` and `<OPEN_EXCHANGE_APP_URL>` as preparation placeholders until the real destinations exist. Replace them in the application copy and both articles before publication. The repository URL is already real: `https://github.com/himanshu748/silentshift`.

## 1. Upload the video to YouTube

- [ ] After local video verification, open **YouTube Studio → Create → Upload videos** and select `evidence/video/silentshift-demo.mp4`. Use the finished [title, description and tags](YOUTUBE_UPLOAD.md).
- [ ] Add the reviewed thumbnail and `evidence/video/silentshift-demo.srt`; complete audience/disclosure fields truthfully. Preserve the synthetic-data and IRIS destination-simulator disclosures.
- [ ] Finish **Checks**, choose visibility judges can access, and complete the upload. Open the watch URL while signed out; verify full playback, captions, readable interface text and working source link.
- [ ] Record the working watch URL as `<YOUTUBE_VIDEO_URL>`. A local file, upload progress screen or private video does not establish judge access.

[Official upload instructions](https://support.google.com/youtube/answer/57407?hl=en). Potential bonus: **3 points**, subject to organizer acceptance. The walkthrough is silent; no generated narration is needed.

## 2. Complete the saved Open Exchange application

- [ ] Sign in and open the [SilentShift draft](https://openexchange.intersystems.com/portal/products/SilentShift/edit). Check personal eligibility/profile details and any team Community profile links; these are separate from technical completion.
- [ ] Paste [the finished application copy](OPEN_EXCHANGE_COPY.md). Check repository, MIT license, documentation, logo and category/technology fields.
- [ ] Check **Submit to Contest** for **InterSystems Programming Contest: AI Agents in Interoperability Workflows**.
- [ ] Put the real `<YOUTUBE_VIDEO_URL>` in **YouTube URL**. Leave an online-demo URL empty unless a separately authorized live deployment exists.
- [ ] Put `https://ideas.intersystems.com/ideas/DPI-I-689` in the dedicated **Ideas Portal link** field. Confirm the README links the same idea and its reproducible LLM-metadata Visual Trace example.
- [ ] Select **Publish in Package Manager** for step 5. Verify module **silentshift 0.1.0** and declared **2026.3.0AI.154.0 ARM64 Community** target; no build-109 compatibility is claimed.
- [ ] **Save → Preview**, inspect rendered copy/links/video, then manually click **Send for Approval**. Keep the actual saved review state and, after approval, `<OPEN_EXCHANGE_APP_URL>`.

The [OEX guide](https://docs.openexchange.intersystems.com/apps/submit/) separates draft saving, review request and publication. None alone confirms contest entry.

## 3. Apply to contest 49 and retain confirmation

- [ ] Open [contest 49](https://openexchange.intersystems.com/contest/49), click **Apply**, select SilentShift, and complete the entry. The app's **Contest** tab and developer-portal app menu are documented alternatives.
- [ ] Retain the separate contest confirmation and verify the registered-app list. Recheck declared runtime, team and repository. Keep OEX-review and contest-entry receipts separately.
- [ ] If an **Awaiting Review** app is not selectable, follow up manually in the official organizer channel before the deadline. The organizer permits timely submission before OEX approval; the exact pending-review UI path is unverified. Do not mark the entry registered without confirmation.

Sources: [Apply routes](https://docs.openexchange.intersystems.com/contest/apply/) and [contest-specific clarification](https://community.intersystems.com/node/590306). The app must work during evaluation. Build 154 is verified; the separately permitted 109 has not been tested for SilentShift. EAP kits and derived images must not be redistributed.

## 4. Publish both Developer Community articles

- [ ] In [the overview](articles/overview.md), replace both URL placeholders with the working video and public OEX app URLs. Preserve the real repository link `https://github.com/himanshu748/silentshift`.
- [ ] Sign in to [Developer Community](https://community.intersystems.com/), choose **New post → Article**, paste the finished overview, choose the relevant Group/tags, upload its reviewed images, preview and publish. Verify the public URL while signed out. This is the **2-point potential first-article** gate.
- [ ] Repeat for [the distinct engineering article](articles/engineering.md), keeping its implementation evidence and limitations. The second public article adds **1 potential point**; subsequent articles add no stated bonus.
- [ ] Put the actual OEX app and repository links in **each** article, and set its **Open Exchange application link** field. Add the published article URLs to OEX's **Community Article URL** field/resources and verify the saved association. The OEX guide also describes automatic app association when an article links its app.

Local Markdown is finished preparation; publication gates require actual public articles. [Official posting guidance](https://community.intersystems.com/post/how-get-most-out-posting-dev-community).

## 5. Publish IPM, then verify a fresh public-registry install

- [ ] Follow [the exact public publication steps](IPM.md#publish-and-verify-the-public-package): public root `module.xml`, OEX Package Manager setting, reviewed application approval request and observed public registry availability. A private/test CLI publish does not replace the Open Exchange route.
- [ ] Provision a **new official build-154 instance** and empty **SILENTSHIFT** interoperability namespace. Omit source mounts, source stages, local app archives and preinstalled SilentShift classes. Install pinned IPM 0.10.10 and capture pristine-state evidence.
- [ ] Run [the anonymous repository and verification commands](IPM.md#3-verify-installation-from-the-public-registry-in-a-fresh-instance). The source-qualified command is `install PublicCommunity/silentshift 0.1.0`, with that name bound to `https://pm.community.intersystems.com/` and publishing disabled.
- [ ] Retain registry/version, history, build/client, available artifact identity, manager-only Python origins, ten path rejections, five deterministic cases and ten empty-table checks. Separately authorize any later explicit setup, local embedding/warmup and native-five rerun. Exclude the diagnostic from the evaluation.
- [ ] Change public-IPM status only after success. Existing local proof: **43 classes, nine assets, 53 files, 75,003 bytes**, native **5/5**; archive SHA-256 `0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6`. This filesystem-registry result does not prove public installation.

Potential IPM bonus: **2 points**, unconfirmed. Commands were checked against official **v0.10.10** source; no registry publication/install or credentials test was executed during this preparation.

## Potential bonus points

The [official announcement](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows) sets voting bonuses. **All points below are potential and unconfirmed.** The [execution ledger](BONUS_EVIDENCE.md) supplies technical receipts; organizers decide whether each criterion qualifies.

| Criterion | Potential points | Evidence / remaining action |
|---|---:|---|
| Embedded Python | 3 | Native assessment/policy and installed module origins verified |
| IRIS in Docker | 2 | Official 154U runtime and fresh local package instance verified |
| Native Workflow | 2 | Real tasks, reviewer actions and native queues verified |
| Custom adapter | 2 | Actual file intake and delivered/quarantined cases verified |
| IRIS vector retrieval | 2 | Real embeddings, IRIS vectors/cosine and fourth agent tool verified |
| Community Opportunity idea | 4 maximum | DPI-I-689 trace implementation verified; retain README and dedicated OEX idea links |
| Feedback questionnaire | 1 | Already submitted; confirmation retained. Do not repeat merely to seek another point |
| YouTube demonstration | 3 | Complete step 1 and link the accessible video |
| First Community article | 2 | Publish/verify the overview in step 4 |
| Second Community article | 1 | Publish/verify the distinct engineering article in step 4 |
| Public IPM package | 2 | Complete publication and fresh registry-install proof in step 5 |

These rows total **24 potential points** if accepted: 16 supported by executed technology/questionnaire evidence, plus 8 dependent on remaining publication gates. This is not an awarded score or ranking prediction; no conversion to Expert Jury scores is published. The idea allowance is capped at four per entry.

| Other announced criterion | Published points | Why no claim is prepared |
|---|---:|---|
| Online live demo | 2 | Not hosted; outside scope. Recorded/static replay does not meet the organizer's live-demo clarification |
| Java/.NET PEX | 3 | No Java/.NET production extension implemented |
| Reproducible AI Hub bugs | 2 first, +1 second; max 3 | No verified vendor defect/report claimed; local application/driver repairs are not vendor bug evidence |
| Reproducible Embedded Python bugs | 2 first, +1 second; max 3 | No verified vendor defect/report claimed |

## Final manual readback

- [ ] Open the video, OEX app, repository and articles while signed out. Remove URL placeholders from published copy and resolve broken links.
- [ ] Retain actual OEX-review state, contest receipt, article URLs and public registry-install receipt; update the ledger from observed states.
- [ ] Preserve the feedback confirmation. Personal eligibility, Freshmen status and organizer awards remain unverified until actual confirmation exists.
