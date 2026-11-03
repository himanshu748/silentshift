# Submission status and remaining steps

Stopped at the user's request on **November 4, 2026**. Deadline: **November 9 at 10:29:59 IST / November 8 at 23:59:59 EST**, per [contest 49](https://openexchange.intersystems.com/contest/49). Feature freeze is retained. No organizer score or bonus award is claimed.

## Completed and observed

| Item | Current evidence |
|---|---|
| Native product | Official ARM64 AI Hub 154U; native agent, deterministic policy, Workflow, vector precedents and custom file adapter verified. [Technical ledger](BONUS_EVIDENCE.md) |
| Quality gate | Retained 172 Python checks, TypeScript/build, 32 disconnected/landing and 16 native browser checks. No application features changed in this submission work |
| Video | [Public YouTube demo](https://youtu.be/a4dOcqu89EA), 2:30. Anonymous oEmbed HTTP 200; 1080p HD and English captions observed in the actual player. Local MP4 and SRT remain in `evidence/video/` |
| Open Exchange | [SilentShift 0.1.0](https://openexchange.intersystems.com/package/SilentShift): **Sent for approval / Awaiting Review**. Contest option, Package Manager option, DPI-I-689 link and video saved |
| First article | [Catching semantic failures in an IRIS interoperability production](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production): submitted, rewritten in place and saved; **On moderation** |
| Second article | [Recoverable human review in IRIS: from approval to one delivery](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery): submitted, rewritten in place and saved; **On moderation** |
| Questionnaire | Submitted earlier with the user's answers; [receipt](assets/questionnaire-submitted.png). Do not submit again |
| Local IPM install | Real clean local install: 43 classes, nine assets, 53 files / 75,003 bytes; native 5/5 final routes and 4/5 model proposals. [Receipt](evidence/ipm-clean-install.json). Public-registry installation is a separate gate |

## Remaining actions, in order

1. **Check application moderation.** Open [My Applications → SilentShift](https://openexchange.intersystems.com/portal/products/SilentShift/edit). Preserve the existing request; do not cancel it or create a duplicate. It currently offers **Cancel approval** and says **Sent for approval**.
2. **Register the published app for contest 49.** Open [contest 49](https://openexchange.intersystems.com/contest/49) → **Apply → SilentShift → complete entry**, then retain the actual contest confirmation. The current Apply dialog says no application on this account is published and requires publication before entry. The saved contest checkbox is not a registration receipt. If moderation still blocks entry near the deadline, use the official organizer channel; no organizer message has been sent.
3. **Check both article moderation results and canonical links.** The technical rewrites are saved under the new titles above. Renaming changed their slugs. OEX's saved article fields and the posts' cross-links still contain the original routes; confirm redirects or replace those fields with the canonical links above. The repository copies already use canonical links. Verify both posts without editor privileges after approval. Potential article bonuses: **2 points + 1 point**.
4. **Verify public IPM availability, then install from that registry.** The saved OEX request asks for Package Manager publication. Anonymous `silentshift/0.1.0` listing and manifest reads returned **404**. Follow [IPM.md](IPM.md#publish-and-verify-the-public-package) after the listing appears; use a fresh official build-154 namespace with no source/app archive mounts and `install PublicCommunity/silentshift 0.1.0`. Keep the registry artifact and clean-install receipt. Potential bonus: **2 points**. An OEX IPM badge alone proves no registry install.
5. **Finish public readback.** Open the video, app, repository and approved articles without editor privileges. Check caption playback, setup/source links, article associations, idea field and separate contest receipt. Optionally add the approved OEX link to the live YouTube description. Recheck personal eligibility/team/profile details; these have not been established by technical tests.

## Bonus coverage

All points below are **potential and unconfirmed**. Sources: [official bonus announcement](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows), [DPI-I-689](https://ideas.intersystems.com/ideas/DPI-I-689). Organizers determine qualification.

| Criterion | Points | Status |
|---|---:|---|
| Embedded Python | 3 | Native policy and installed module origins verified |
| Docker | 2 | Official 154U runtime and clean local instance verified |
| Native Workflow | 2 | Real tasks, reviewer actions, concurrency and recovery verified |
| Custom adapter | 2 | Real file intake, held/delivered cases and replay verified |
| IRIS vector retrieval | 2 | Native vectors/cosine, fourth tool and critical-case veto verified |
| Community Opportunity idea | Up to 4 | Provider-call traces executed; README and OEX dedicated idea links saved |
| Feedback questionnaire | 1 | Submitted; receipt retained |
| YouTube demonstration | 3 | Public video with captions and actual 1080p playback observed |
| First Community article | 2 | Submitted and revised; moderation pending |
| Second Community article | 1 | Submitted and revised; moderation pending |
| Public IPM package | 2 | Publication requested; registry availability/install unverified |

The rows total **24 potential points**, with no claimed awarded score or ranking. The online live-demo bonus (2) is not pursued because no hosted app exists. Java/.NET PEX (3) is not implemented. AI Hub and Embedded Python vendor-bug bonuses (up to 3 each) have no verified vendor defect/report. Recorded UI footage is not a hosted live demo.

The [submission receipt](evidence/submission-status.json) records the external states separately from [native engineering evidence](BONUS_EVIDENCE.md). Resume from the remaining actions above; no further publication work is running.
