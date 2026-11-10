# Backend polish and voting-week preparation

Checked **2026-11-10 17:07:54 IST**. Work is local on `backend-polish-nov10`; main, registry, OEX, tags and releases were not changed. This is a verification report with explicit incomplete gates, not a release-ready claim.

The [official contest rules](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-interoperability-workflows) state: “You can continue improving your application throughout both the submission and voting periods.” Checked November 10. That permits continued work; it does not grant a bonus or remove the owner's publication gates.

## Backend addendum

| Item | State and limit | Evidence / commit |
| --- | --- | --- |
| 1. Host Event Log | Implemented; held routing INFO and investigation WARNING observed in native UI. Delivered-case screenshot remains missing. Stage TRACE calls exist; no claim that disabled trace events were persisted. | `a6fda34`; [UI capture](../evidence/backend-polish-nov10/11-native-ui.json) |
| 2. Setup/IPM diagnostics | Implemented and native-tested; friendly error plus redacted bounded original status and last_setup_error global. | `c578e8a`; [native suite](../evidence/backend-polish-nov10/fresh-source-native.txt) |
| 3. Formatting / prompt | Implemented; native compile passed after fixing accidental ObjectScript pattern spacing. Runtime prompt bytes match original hash. | `adb47a5`, `cec2330`; [prompt check](../evidence/backend-polish-nov10/03b-pytest.txt) |
| 4. Shared helpers/catalog | Implemented; allowlist, tool preamble, model default, Bridge import and policy catalog. Policy function/class ASTs remain unchanged. | `25a1ef2`; [invariants](../evidence/backend-polish-nov10/07-policy-invariants.json) |
| 5. Compact replies | Implemented; native summary-shape test passed; actual References reply inspected. Destination/Quarantine bodies were not separately captured. Full Partner reply retained. | `718f3c2`; [UI receipt](../evidence/backend-polish-nov10/11-native-ui.json) |
| 6. Stages / settings | Implemented; exact fault-injection comparison retained; native production defaults tested. | `1b5701d`, `5af52c9`; [fault invariant](../evidence/backend-polish-nov10/06-fault-invariant.json) |
| 7. Small fixes / Ruff | Implemented safe changes. Whole-tree findings: 154 before, 79 at item 7, **83** at final tree (including 3 in the copied raw command artifact). No clean Ruff claim or CI gate. Existing configurable source providers prevent a truthful universal local-only claim; only local Qwen is qualified. | `611eca4`; [Ruff receipt](../evidence/backend-polish-nov10/final-ruff-summary.json) |
| 8. Generated Storage | Done; nine compiler-exported blocks, diff-only commit. | `c3302c3`; [export hashes](../evidence/backend-polish-nov10/08-storage.json) |
| 9. IPM operator docs | Done; namespace/build, reviewer, CSV bound, model limits and ownership-aware manual cleanup. No uninstall or cleanup ran. | `2f25ee1`; [IPM guide](../IPM.md) |

Each implementation step has its own pytest output under [backend evidence](../evidence/backend-polish-nov10/). Original failures remain visible. Native code was not modified to make a fixture or replay pass.

## Gates actually run

- Fresh local source clone `76d9ef17f660d3d9ca9aa428257563055111fb51`: compiled source load, started production, **7 classes / 22 methods**, two **12/12** recorded replays; **339 pytest**, TypeScript/build and **54** disconnected/responsive browser checks. Activation resumed after default Docker network pool exhaustion; not a first-try uninterrupted install. [Current verification](../JUDGE_VERIFICATION.md#current-local-branch-repeat).
- Connected suite: **12 passed / 4 failed in 44.7s**, due missing delivered-amendment and retrieved-precedent cases in this clean replay setup. No fixture injection, weakening or retry. [Failures](../evidence/backend-polish-nov10/fresh-connected.json).
- Same-instance earlier review: **26/26 reject + 26/26 approve**, including concurrency and one receipt; not fresh-instance proof. The final-instance review preparation stopped after two environment errors. [Passed scope](../evidence/backend-polish-nov10/upgrade-review.json), [blocked scope](../evidence/backend-polish-nov10/fresh-review-blocked.json).
- Updated harness: **373 pytest in 36.54s**. Fresh local clone `f9fc970b197e8c2830a784ede062a4485a18b7a2` then ran the actual shell entry against public native **0.3.0**, pinned compatible release tests, **5 classes / 12 methods** and two **12/12** replays. [Public launcher](../evidence/backend-polish-nov10/public-shell-summary.json). It uses Docker, not Compose; the requested Compose launcher remains unfulfilled.
- Native compact References body, provider response metadata and Event Log were read under the owner's exact temporary permission approval. Both table grants were removed and role resources restored exactly. [Restoration](../evidence/backend-polish-nov10/11-permissions-restored.json).

**0.3.1 is not prepared:** required delivered-case native screenshots and the complete connected setup gate remain open. Manifest/project stay 0.3.0; do not publish this changed branch under that existing public identity. No fresh live-five-case, full CSV-browser or sealed benchmark run was made in this pass.

## Visuals and presentation

- [README](../../README.md): product pitch, no-install judge path, five fresh recorded-source captures, one install front door and honest bonus table. Existing UI edits and sealed results are preserved outside these commits.
- [Static judge page](../site/README.md): responsive local candidate, video, example, diagram, gallery, replay and articles. [Browser receipt](../evidence/voting-week-nov10/site-final-browser.json). Not published, no backend, no online-demo claim.
- [Logo](../assets/brand/silentshift-logo-v1.png): prepared locally, not uploaded to OEX.
- [One OEX bundle](../OPEN_EXCHANGE_COPY.md): native 0.3.0 / React 0.2.1 correction plus five source captures. Capture URLs require an approved push before the form is prepared. Do not send the old description-only draft separately.
- [v0.3.0 release draft](github-release-v030-draft.md): targets the published snapshot, not backend HEAD. No tag or release created.
- [CSV supplementary clip](csv-supplement.md): local captioned edit from historical captures, not a fresh screen recording; not uploaded.

## External status and owner-visible issue

Anonymous OEX still shows release 0.3.0 and dedicated DPI-I-689, but body text still says native 0.2.0 / CSV source-only. [Readback](../evidence/voting-week-nov10/oex-public-final.json). The browser also observes one failed OEX image whose source is `/assets/img/` followed by a null character; Categories text links render. This is an OEX page asset, not a repository file, and no email about it was sent. The November 10 queue-check email has no reply. No four-point qualification or award is confirmed.

## Exact gated actions, in order

1. **Push only `backend-polish-nov10` to `himanshu748/silentshift`.** A new exact `submit` authorizes only this action; never push main. Protected uncommitted UI/sealed files stay uncommitted.
2. After a separate approval, open one draft backend PR with the incomplete native/browser gates listed. Do not merge or call 0.3.1 ready while they remain open.
3. After source assets are public and each URL reads anonymously, prepare the one OEX form bundle, screenshot it, then stop for a separate exact `submit` for Send for approval. Preserve idea, contest, IPM, video and articles; never cancel approval.
4. GitHub **v0.3.0 tag/release** at the actual public snapshot is a separate optional approval. Do not tag backend HEAD as v0.3.0.
5. Publishing the static Pages candidate is a separate approval, after the advertised shell entry and guide exist on the chosen public branch. It remains a static product page, not a hosted native demo.
6. **Merge, v0.3.1 tag/release, IPM publication and its OEX update are blocked**, not queued actions: finish the missing acceptance evidence and prepare/clean-install a correctly versioned candidate first, then request separate approval for each.

Phase 4 community publication is owner-handled and was skipped. Existing social/article/comment drafts remain unsent. No spending, votes, new entry, questionnaire resubmission, duplicate bug, EAP redistribution, CI/billing changes or bonus-status inflation occurred. Daily monitoring remains read-only through the November 16 freeze.
