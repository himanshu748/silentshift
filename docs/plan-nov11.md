# Voting-week plan — November 11, 2026 (IST)

## Outcome and boundaries

Help an integration engineer or judge understand the semantic mismatch, run the released native package without keys, and inspect the evidence behind a routing decision. Preserve deterministic routing, the 154U ARM64 qualification, synthetic-data labels and immutable evidence. No new model benchmark, unsupported build, award or ranking claim. No paid infrastructure or provider calls.

Main observed: `2a5cc4e577f60e6bd34375f81780a5d1a267e3b4`, not the supplied older `cfc4c27`. Native IPM/OEX/GitHub release are 0.3.2; React is separately built 0.2.1. The saved OEX body still has 0.3.0 wording. A new listing edit remains gated; this task supersedes the earlier paused edit attempt.

## Rules checked before implementation

- [Official announcement](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-interoperability-workflows) permits improvements during submission and voting. [Contest 49](https://openexchange.intersystems.com/contest/49) ends November 15 at 23:59:59 EST, November 16 at 10:29:59 IST. Keep the owner's earlier public-change freeze at November 16, 07:00 IST.
- [Voting announcement](https://community.intersystems.com/post/time-vote-intersystems-programming-contest-ai-agents-interoperability-workflows) says votes are hidden; listing order is submission order. Its published Community Top 5 names LabTriage Agent, Medical Insurance Audit Evidence Assistant, MyOwn Portal, OcuTalon and iris-agentic-production. This is a dated Community snapshot, not an Experts ranking or a prediction.
- [Official bonuses and staff comments](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows): questionnaire 1; Java OR .NET PEX 3; Workflow 2; custom adapter 2; AI Hub bug 2 plus 1 for a second; Embedded Python usage 3; Vector Search 2; Docker 2; IPM 2; online demo 2; Community Idea 4 maximum; Embedded Python bug 2 plus 1 for a second; first article 2, second article 1; downloadable video 3. More ideas, a second PEX language and further articles do not multiply those caps. No separate FHIR or unit-test bonus is listed. Reviewers are assessing eligibility; implementation or a public association is not an award.
- Staff require the idea URL in README and the dedicated OEX field, a reproducible Visual Trace metadata example, and a Langfuse comparison for DPI-I-689. Multiple entrants may use the same idea. All are already evidenced; qualification remains unconfirmed.
- Freshmen eligibility depends on the owner's contest history and prior placements. A newcomer label is not sufficient independent proof of eligibility.

## Competitive scan and decisions

The comparisons below concern advertised reader experience, not independent execution of rivals' software. No rival credentials or model calls were used. Direct OEX fetching was intermittently blocked (timeouts/403); after repeated failures, read indexed primary project material and mark limits instead of retrying indefinitely.

| Published Community leader | Primary evidence inspected | Useful pattern | SilentShift opportunity |
| --- | --- | --- | --- |
| LabTriage Agent | [Listing](https://openexchange.intersystems.com/package/LabTriage-Agent), [repository](https://github.com/AzizCotrim/iris-lab-triage-agent) | Default keyless replay with a short Compose start | Make our advertised replay verify the current package rather than fail a stale version assertion |
| Medical Insurance Audit Evidence Assistant | [Listing](https://openexchange.intersystems.com/package/Medical-Insurance-Audit-Evidence-Assistant), [repository](https://github.com/boanerges1227/MedicalInsuranceAudit) | Explicit distinction between no-key evidence/review and optional live AI; separate package startup | Keep our replay/live boundary explicit and offer a concrete evidence-reading journey |
| MyOwn Portal | [Author article](https://community.intersystems.com/post/myown-portal-ai-knows-paths-human-chooses-destination), [repository](https://github.com/muriloprzy-code/Portal-Iris) | One-click installation and clearly named viewer role | Reduce setup ambiguity; prepare a no-install evidence experience without pretending it runs IRIS |
| OcuTalon | [Listing](https://openexchange.intersystems.com/package/OcuTalon), [author teaser](https://community.intersystems.com/post/ocutalon-teaser-my-ai-agents-contest-entry) | Understandable explanation and human approval in the product pitch | Make evidence and routing visible in a short interaction. Detailed implementation/demo operation not independently verified |
| iris-agentic-production | [Listing](https://openexchange.intersystems.com/package/iris-agentic-production) | Three-minute replay, visible evaluation, direct message stories and a demo link | Put the concrete case journey before implementation history; link inspection to real receipts and trace IDs |

[Expert guidance](https://community.intersystems.com/post/what-experts-look-contest-entries) favors first-run success, a working demo, strong work at the top, complete task coverage and explained engineering decisions. No placement estimate is supportable from these observations.

## Three small feature PRs, in order

1. **Current-package judge launcher.** Correct the mismatch where the driver requests the latest IPM package but expects 0.3.0. Pin the matching 0.3.2 assertion source, retain literal keyless public installation, preserve image/credential/disk safeguards, and capture a fresh public install, native suite and two replays. Highest impact: Clarity and Developer Experience. Regression tests must catch the stale version and keep failure propagation intact.
2. **Local receipt-integrity inspector.** A static browser utility to inspect a real exported synthetic receipt, independently recompute its payload hash and verify its RSA signature. Explain embedded-key trust and business-correctness limits; untrusted upload stays local. A tampered-copy check demonstrates integrity failure without modifying any case or receipt. Highest impact: Usability and technical mechanism visibility; no bonus claimed merely for the utility.
3. **Guided recorded evidence tour.** A keyboard/mobile/reduced-motion browser journey through the existing held and approved-amendment evidence, with immutable source links and a clear recorded/synthetic banner. No fake native calls, counts or live-demo label. Highest impact: Applicability and first-click understanding. Preparation only until Pages publication is approved; not the online-demo bonus.

Each feature gets a branch/PR, focused tests, full local checks, hosted CI and a clean-container package gate before merging. Do not merge a candidate with an unverified clean-install gate. No weakened test, secret, EAP image, policy change or package-version bump. Preserve failures in the run log; after two genuine failures, record the blocker and move on.

## Hosting decision and release preparation

A genuine native online demo remains potentially claimable (2), not earned. Written contest permission exists; deployment is not verified. The prior Crashcart-host preflight found x86_64 versus our ARM64-only qualified image, with limited memory. Do not expose the operator Compose stack or substitute a static page for a running app. Prepare an honest deploy/resource/rollback proposal only if the architecture and read-only boundary can be satisfied; deployment and spending require owner approval. No model image will be pushed to a registry.

Prepare `docs/launch/` with next-version notes (no invented release number), OEX description, PEX/other genuine claim drafts, an engineering article, a 2:30–3:00 video script/shot list and three social drafts. Every external action remains separately gated. Existing bonuses are in [the checklist](SUBMISSION_CHECKLIST.md#every-bonus); do not resubmit the questionnaire or duplicate bug #17.
