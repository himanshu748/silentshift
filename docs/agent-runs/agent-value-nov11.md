# Recorded agent value: presentation review

Prepared on the `feat/agent-value-nov11` branch. The functional presentation snapshot is **855e0143d67540b192072d7c0430d7a061a1ef11**, based on main **7ae03be03ac6721639e83bdd9e3ed07a5350649e**. [Machine-readable checks and exact output links](../evidence/agent-value-nov11/summary.json).

## What a judge can inspect

The README opening, landing hero, recorded tour and OEX **draft** now pair the historical wrong-delivery result with its review cost: **6/23 → 2–3/23**, counterfactual baseline release choices versus actual simulator receipts, across the same **48 synthetic orders**. Review rises **12.5% → 21.5%**, pooled across agent trials. All values come from the unchanged [original result](../EVAL_HELDOUT.md) and [summary](../../evidence/heldout/summary.json).

The requested “overall unchanged 33/48” shorthand would hide the worse third trial. The copy instead says **33/48 → 33/48, 33/48 and 30/48**, with no overall accuracy gain. Unstructured exact routing remains **1/16** in every trial for both arms. The historical evaluation predates current native 0.3.2; it is not a fresh assessment of this release.

[What the agent saw](../AGENT_VALUE.md) and the static page show **HO-045, HO-030 and HO-017** with complete original clauses, exact reference IDs, raw recommendations, deterministic policy reasons and all three recorded trials. They were selected after results were known. In each, the raw agent matches the frozen QUARANTINE label while policy retains the concern in REQUEST_REVIEW, with a pending native task and no simulator delivery. That is reviewer assist, **not** a correct final three-way route or evidence of completed human review. The source links are pinned to the unchanged base commit and the exporter checks their hashes.

The [2:20 re-cut](../launch/video-script.md) is a script/shot list only. Native IPM stays **0.3.2**; separate React stays **0.2.1**. No evaluation, agent, policy, label, native-package or original-run change was made.

## What ran

| Check | Actual result | Evidence |
| --- | --- | --- |
| Python suite | 394 passed, 36.33 seconds | [output](../evidence/agent-value-nov11/pytest.txt) |
| Java receipt core | 7 successful, none failed | [output](../evidence/agent-value-nov11/java.txt) |
| TypeScript / build | Both passed | [types](../evidence/agent-value-nov11/types.txt), [build](../evidence/agent-value-nov11/build.txt) |
| Existing workbench browser suite | 54 passed | [output](../evidence/agent-value-nov11/workbench-browser.txt) |
| Static provenance/crypto tests | 18 passed | [output](../evidence/agent-value-nov11/node-tests.txt) |
| Receipt inspector / tour / new prose page / landing | 33 / 39 / 38 / 47 browser checks passed | [inspector](../evidence/agent-value-nov11/inspector-browser.json), [tour](../evidence/agent-value-nov11/tour-browser.json), [new page](../evidence/agent-value-nov11/cases-browser.json), [landing](../evidence/agent-value-nov11/landing-browser.json) |
| Source extraction | Deterministic offline regeneration matches | [output](../evidence/agent-value-nov11/build-presentation.txt) |
| Links | All checked local targets exist; 17 anonymous public reads returned 200 | [individual targets](../evidence/agent-value-nov11/links.json) |

Browser checks cover keyboard, reduced motion, mobile, no-JavaScript reading and source disclosures. The new page makes static local GET requests only. The actual in-app browser journey was also inspected. No native install or live scenarios were rerun; their existing receipts retain their earlier scope.

Final local Lighthouse performance/accessibility/best-practices/SEO: landing mobile **93/100/100/100**, desktop **100/100/100/100**; tour and new page **100/100/100/100** on both profiles. The final paired runs are not lower than their corresponding baselines. Earlier runs varied, including a new-page desktop performance score of 72 and a noisy final mobile baseline of 56. Do not infer a general speed improvement. [Every series and limitations](../evidence/agent-value-nov11/lighthouse-summary.json), [compressed raw reports](../evidence/agent-value-nov11/lighthouse-reports.tar.gz), [report hashes](../evidence/agent-value-nov11/lighthouse-manifest.json).

Local setup issues were corrected without weakening checks: shared dependency paths caused Vite font allowlist warnings; a task-owned dependency copy removed them and types/build/browser checks were repeated. The first Python landing preview lost a script request; the [failed receipt](../evidence/agent-value-nov11/landing-browser-first.json) is retained alongside the successful Node-preview retry. The temporary performance server's incorrect robots fallback was also corrected. No native runtime change was needed.

## Screenshots

[Desktop opening](../evidence/agent-value-nov11/intro-1440.png) · [Mobile opening](../evidence/agent-value-nov11/intro-375.png) · [Desktop policy and all trials](../evidence/agent-value-nov11/case-1440.png) · [Mobile policy and all trials](../evidence/agent-value-nov11/case-375.png).

## Public actions remain gated

No merge, deployment, OEX edit/release, tag, native publication, post or video upload occurred. The new agent-value URL is a future Pages target; existing tour/inspector URLs already respond publicly. The OEX metadata 0.3.3 copy is a **docs-only proposal**, not a claim that native 0.3.3 exists. Stop if the editor couples it to native/IPM publication.

[Exact owner action list](../launch/gated-actions.md): review/merge prerequisite, then Pages, then the OEX draft with manually typed version (never 1.0.0). Java PEX comment **288628 is already public** according to the anonymous read retained in the link receipt; skip any duplicate. Hosted CI for this local branch has not been run.
