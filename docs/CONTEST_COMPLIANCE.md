# Contest compliance

Verified against the linked primary sources on **2026-11-02**. This records requirements, not proof that SilentShift satisfies them. Runtime evidence belongs in `BUILD_STATUS.md`; bonus claims belong in `BONUS_EVIDENCE.md`. Recheck external deadlines and registration immediately before submission.

## Entry requirements and schedule

[Contest 49](https://openexchange.intersystems.com/contest/49) requires a functional, original IRIS interoperability workflow using an IRIS AI Hub agent for a decision. IRIS and IRIS for Health are supported. Source must be open on GitHub/GitLab, with an English README containing installation and a video or detailed walkthrough. At most three entries per developer are accepted. Judging covers **Complexity, Clarity of Instructions, Developer Experience, Applicability, and Usability**; no numerical weights were published on the inspected page.

| Event | Published time | India time (UTC+05:30) |
|---|---|---|
| Registration closes | 2026-11-08 23:59:59 EST | **2026-11-09 10:29:59 IST** |
| Voting | November 9–15, 2026 | See announcement for exact boundaries |

The conversion uses EST (UTC−05:00), as explicitly written by the organizer. Submit substantially earlier than the cutoff.

## Build, distribution, providers

The [announcement and organizer comments](https://community.intersystems.com/node/590306) prescribe **2026.3.0AI.154.0 Community**, replacing build 162. IRIS/Health and x64/ARM64 images are accepted. Download from the [AI Hub EAP portal](https://evaluation.intersystems.com/Eval/early-access/AIHub), load locally, inspect the loaded name, and retag for Compose. The README must identify the build, load/retag commands, provider, key environment variable, start command and health check. Do **not** redistribute EAP images or derived images through registries.

Organizer clarifications permit contest development, recorded/public demos, synthetic data, and AI coding assistance; disclosure is optional. No provider credits are supplied. Entrants and judges supply their own keys. Replay without a key is accepted if live mode is available; a static recorded-response website does not earn the live-demo bonus. An Ideas Portal link is optional. Team READMEs must link every member's Developer Community profile.

The [EAP documentation](https://github.com/intersystems-community/ai-hub-eap) warns that its APIs can change and the prerelease software is unsuitable for production. Its general README still includes build-162 examples; contest-specific build-154 instructions take precedence. The [community development template](https://github.com/intersystems-community/ai-hub-dev-template) currently documents build 154 and native agent usage; it is a reference, not proof that this application runs. Confirm exact classes and methods inside the loaded 154 runtime.

## Submission workflow and confirmation

[Open Exchange application instructions](https://docs.openexchange.intersystems.com/apps/submit/) require authentication, New Application, metadata and repository details, then **Send for Approval**. Saving produces a draft; sending initiates review, and acceptance publishes it. Prepare the license URL, categories, technologies, descriptions, logo, and applicable demo/documentation/video links. The [contest guide](https://docs.openexchange.intersystems.com/contest/apply/) describes Apply from the contest, app page, or developer portal and generally says the app must be published first.

The contest-specific October 21 [organizer clarification](https://community.intersystems.com/node/590306) says approval need not occur before the deadline: timely submission is sufficient, but the package must work during evaluation. **Observed behavior of registering an Awaiting Review application remains unverified.** Preserve the actual OEX submission receipt and separate contest-registration confirmation; a repository, draft or approval request alone proves neither contest entry nor acceptance.

[Moderation documentation](https://docs.openexchange.intersystems.com/quality/mod/) explains that moderators test apps and may report Works/Doesn't work. The [expert-preparation article](https://community.intersystems.com/post/what-experts-look-contest-entries) recommends clean setup, a complete workflow, clear README evidence and relevant bonuses. It explicitly describes itself as advice, not a formal scoring rubric.

## Eligibility and terms

The [competition terms](https://openexchange.intersystems.com/markdown?url=/assets/doc/contest-terms.md) require an Open Exchange profile, correct English registration details, agreement to applicable terms, and legal eligibility. Entrants must satisfy age-of-majority requirements and be at least 16; location/export restrictions apply. InterSystems can verify eligibility and prize identity. No purchase is necessary. Contest-specific rules take priority over general terms. **The user's personal eligibility, profile, prior entry count and Freshmen status have not been verified.** These are distinct from engineering completion.

## Existing entries and product implication

The [contest page](https://openexchange.intersystems.com/contest/49) displayed **eight registered applications** at this check. [PaymentGuard AI](https://openexchange.intersystems.com/package/PaymentGuard-AI) describes payment/claim risk decisions with evidence tools and guardrails. [RouteGuard IRIS](https://openexchange.intersystems.com/package/RouteGuard-IRIS) describes auditable shipment-exception triage. Their published descriptions are competitor claims, not independently tested results. AI Hub plus a safety queue is therefore insufficient differentiation on its own.

SilentShift's chosen focus remains semantic contradictions inside technically successful messages, corroborating contracts, legitimate amendments, conflicting references, and reproducible policy outcomes. This is positioning, not a verified novelty claim.

## Open gates

| Gate | Evidence needed before claiming satisfaction |
|---|---|
| Native execution | Actual 154 production trace, native session and persisted decision |
| Reproducibility | Clean installation transcript from README commands |
| Public source | Accessible repository URL; license and secret/image audit |
| OEX application | Authenticated final status, timestamp, application URL/receipt |
| Contest registration | Separate receipt or visible registered entry on contest 49 |
| Bonuses | Requirement-specific evidence in `BONUS_EVIDENCE.md`; organizer validation where ambiguous |

No submission, bonus, production-readiness or prize claim follows from this research document.
