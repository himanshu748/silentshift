# Contest compliance

Rechecked against the linked primary sources on **2026-11-03**. This records rules and observed status, not contest acceptance. Runtime evidence belongs in [BUILD_STATUS.md](BUILD_STATUS.md); points in [BONUS_EVIDENCE.md](BONUS_EVIDENCE.md); the earlier public-entry comparison in [COMPETITIVE_REVIEW.md](COMPETITIVE_REVIEW.md). Recheck external status immediately before submission.

## Entry requirements and schedule

[Contest 49](https://openexchange.intersystems.com/contest/49) requires a functional, original IRIS interoperability workflow using an IRIS AI Hub agent for a decision. IRIS and IRIS for Health are supported. Source must be open on GitHub/GitLab, with an English README containing installation and a video or detailed walkthrough. At most three entries per developer are accepted. Judging covers **Complexity, Clarity of Instructions, Developer Experience, Applicability, and Usability**; no numerical weights were published on the inspected page.

| Event | Published time | India time (UTC+05:30) |
|---|---|---|
| Registration closes | 2026-11-08 23:59:59 EST | **2026-11-09 10:29:59 IST** |
| Voting | November 9–15, 2026 | See announcement for exact boundaries |

The conversion uses EST (UTC−05:00), as explicitly written by the organizer. Submit substantially earlier than the cutoff.

## Build, distribution, providers

The [announcement](https://community.intersystems.com/node/590306) originally prescribed **2026.3.0AI.154.0 Community**, replacing 162; IRIS/Health and x64/ARM64 were accepted. **New organizer exception visible November 3:** Tatiana Tikhonova's reply to Mikhail Oskola permits **2027.1.0AI.109.0 Community**, with judges using the corresponding declared build. The question reports that older kits disappeared from the portal. Do not describe 154 as the only currently permitted build.

SilentShift remains on its actually verified **154 ARM64 Community** target. No migration or 109 compatibility is claimed. Recheck kit availability for a new judge installation; do not redistribute an old kit as a workaround. Download through the [EAP portal](https://evaluation.intersystems.com/Eval/early-access/AIHub), load/retag locally and document the exact build, provider, key variable, start command and health check. EAP and derived images must not be published.

Organizer clarifications permit contest development, recorded/public demos, synthetic data, and AI coding assistance; disclosure is optional. No provider credits are supplied. Entrants and judges supply their own keys. Replay without a key is accepted if live mode is available; a static recorded-response website does not earn the live-demo bonus. An Ideas Portal link is optional. Team READMEs must link every member's Developer Community profile.

The [EAP documentation](https://github.com/intersystems-community/ai-hub-eap) warns that APIs can change and the prerelease is unsuitable for production. Older examples are not a version guarantee. The [community template](https://github.com/intersystems-community/ai-hub-dev-template) is a reference, not application execution evidence. SilentShift's actual 154 compilation, native sessions and clean-install results govern its claims.

## Submission workflow and confirmation

[Open Exchange application instructions](https://docs.openexchange.intersystems.com/apps/submit/) require authentication, New Application, metadata and repository details, then **Send for Approval**. Saving produces a draft; sending initiates review, and acceptance publishes it. Prepare the license URL, categories, technologies, descriptions, logo, and applicable demo/documentation/video links. The [contest guide](https://docs.openexchange.intersystems.com/contest/apply/) describes Apply from the contest, app page, or developer portal and generally says the app must be published first.

The contest-specific October 21 [organizer clarification](https://community.intersystems.com/node/590306) says approval need not occur before the deadline: timely submission is sufficient, but the package must work during evaluation. **Observed behavior of registering an Awaiting Review application remains unverified.** Preserve the actual OEX submission receipt and separate contest-registration confirmation; a repository, draft or approval request alone proves neither contest entry nor acceptance.

### Authenticated workflow recheck, 2026-11-02

The published instructions list no separate pre-development participant application. This is an inference from the documented app-based submission process, supported by the authenticated UI: after SSO login, clicking contest49 Apply reported that this account has no published Open Exchange applications. The modal instructed: submit an application, send it for approval, then submit the published application to the contest. No app or contest entry was created by this check. The organizer's pending-approval exception remains relevant near the deadline, but the UI path for a pending application is still unverified. Local screenshot: `evidence/browser/contest-application-prerequisite.png`.

EAP access is separate from contest registration. On November 2 the authenticated portal exposed `iris_arm64-community-2026.3.0AI.154.0-docker.tar.gz`; the user explicitly accepted the [Early Access terms](https://evaluation.intersystems.com/Eval/early-access/tos) before its checkbox/download. That archive was subsequently loaded and the native workflow verified; see the build ledger. This historical observation is **not** proof that 154 remains downloadable today, or acceptance of separate contest terms. Screenshot: `evidence/browser/eap-download-approved.png`.

[Moderation documentation](https://docs.openexchange.intersystems.com/quality/mod/) explains that moderators test apps and may report Works/Doesn't work. The [expert-preparation article](https://community.intersystems.com/post/what-experts-look-contest-entries) recommends clean setup, a complete workflow, clear README evidence and relevant bonuses. It explicitly describes itself as advice, not a formal scoring rubric.

## Eligibility and terms

The [competition terms](https://openexchange.intersystems.com/markdown?url=/assets/doc/contest-terms.md) require an Open Exchange profile, correct English registration details, agreement to applicable terms, and legal eligibility. Entrants must satisfy age-of-majority requirements and be at least 16; location/export restrictions apply. InterSystems can verify eligibility and prize identity. No purchase is necessary. Contest-specific rules take priority over general terms. **The user's personal eligibility, profile, prior entry count and Freshmen status have not been verified.** These are distinct from engineering completion.

## Bonus clarifications visible November 3

Semion Makarov's replies to Aziz Cotrim and MxSalata on the [bonus page](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows) resolve the earlier idea questions: DPI-I-689 can qualify without Vector Search; multiple entries may implement the same idea; all ideas together are capped at **4 points per entry**. Required evidence includes the idea link in README **and** OEX's dedicated idea-link field, plus a reproducible LLM-metadata Visual Trace example. A Langfuse comparison is helpful, not a separately stated mandatory requirement. SilentShift's local provider-call traces, screenshots and field map are now verified in [BONUS_EVIDENCE.md](BONUS_EVIDENCE.md). The earlier OEX draft has the idea link; publishing current source and submitting the application remain manual gates.

Tatiana's newer [announcement reply to Doc](https://community.intersystems.com/node/590306) resolves the earlier IPM question: publish the package; installation is checked on AI Hub 154; include `<SystemRequirements Version=">=2026.3" Interoperability="enabled"/>`. Her subsequent 109 reply permits a declared matching build. If IPM is pursued, retain the actual registry-install result for the declared runtime. A manifest alone is not a published, working package.

The [bonus announcement](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows) describes extra voting points. It does not publish a conversion into Expert Jury criterion scores. The contest still lists five judging dimensions without numerical weights.

## Evidence and external gates

| Gate | Observed position at this update |
|---|---|
| Native execution | LOCALLY_VERIFIED: actual 154 production, native agent tools, five scenario outcomes; synthetic simulator scope |
| Reproducibility | LOCALLY_VERIFIED: fresh-volume zero-record start and successful five-case clean-install run; retained evidence below |
| Browser journey | LOCALLY_VERIFIED: connected desktop/mobile reads and a real approved-amendment Scenario Lab delivery; not a public deployment |
| Public repository | CONFIRMED core at [b836d2d](https://github.com/himanshu748/silentshift/tree/b836d2d); current extensions are committed locally and unpushed |
| OEX application | SAVED_DRAFT earlier, with contest checkbox and idea link; not sent for approval |
| Contest registration | NOT_STARTED externally; no separate registered-entry confirmation |
| Bonuses | Local execution receipts for provider tracing, Workflow, case/amendment vectors and custom inbound adapter; see current bonus ledger for exact gates. Organizer awards remain unconfirmed |
| Questionnaire | Submitted earlier; actual confirmation retained in the bonus ledger |

Local evidence: `evidence/native/clean-install-initial.json` (empty initial state), `evidence/native/clean-install.json` (run `0503b649-ee6f-495e-be37-166db508377c`, passed), and `evidence/browser/browser-scenario-delivered.png` (actual C delivery, trace42). These artifacts are ignored/private; publish only reviewed, redacted extracts. See `BUILD_STATUS.md` for current measurements and limits.

The latest November 3 read-only check of the [contest page](https://openexchange.intersystems.com/contest/49) displayed nine entries. The earlier eight-entry comparison is a historical snapshot. Displayed bonus counts do not establish implementation eligibility or final scoring. The competitive review separates public claims, static inspection and actual execution.

No submission, bonus, production-readiness or prize claim follows from this research document.
