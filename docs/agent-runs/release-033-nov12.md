# Matching 0.3.3 candidate — November 12, 2026 (IST)

[Draft PR #15](https://github.com/himanshu748/silentshift/pull/15), source `56c21c0`, prepares a real **0.3.3** manifest/project/lockfile and release description. **No native code changes:** all **75** tracked native/runtime/fixture files match v0.3.2 byte for byte. React remains **0.2.1**. Public native/IPM/OEX and the latest tag remain **0.3.2**. [Scoped evidence](../evidence/release-033-nov12/summary.json).

## What passed

- Offline lock validation and **55** focused package/verifier tests.
- [Push CI](https://github.com/himanshu748/silentshift/actions/runs/43084921250) and [PR CI](https://github.com/himanshu748/silentshift/actions/runs/43085392049): SUCCESS on `56c21c0`. Hosted output shows **395 pytest**, **7 Java tests**, **54 workbench browser tests**, TypeScript/build and **33/39/38** inspector/tour/prose browser checks. Later evidence-only commits need their own check readback.
- A real IPM source load/export produced **silentshift 0.3.3**. The builder needed one namespace activation retry after IRIS ERROR #453, before SilentShift was loaded; the original error and successful retry are retained. This resumed builder is not presented as an uninterrupted fresh-source gate. [Build receipt](../evidence/release-033-nov12/archive-build.json).
- An **independent pristine 154U ARM64 container** installed that archive using literal IPM `install silentshift`, with **no source mounts and no network during install**. The installed identity was explicitly checked as **0.3.3**. Installed checks passed **5 deterministic cases**, **10 path rejections**, **4 Python module origins**, and **10 empty application tables**, with production stopped immediately after package activation. [Install receipt](../evidence/release-033-nov12/clean-install.json) · [actual command/output](../evidence/release-033-nov12/clean-install-output.txt) · [installed version and checks](../evidence/release-033-nov12/installed-checks.txt).

## What remains blocked

The optional explicit setup was then invoked and returned its success marker, but the unchanged **1.8 GiB macOS disk floor** stopped the gateway phase. **No API startup health check, full native %UnitTest suite or recorded API replays ran on this candidate.** The earlier 0.3.2 results retain their own version and scope; they are not relabeled 0.3.3. [Guard output](../evidence/release-033-nov12/clean-activation-output.txt).

Safe cache cleanup and the owner-approved deletion of only the stopped builder freed Docker space, but trimming did not materially return the latter to macOS. The independent archive-install container `silentshift-ipm-clean-033-nov12` is stopped and retained, including its installed package and private runtime configuration. Source, unique evidence, models, official images, user credentials and the other containers/volumes were preserved. Continue only when the disk floor is satisfied. Do not reinstall over the retained state, silently reuse it as a new pristine container, lower a guard or run provider/benchmark work.

## Publication and support

PR #14 was merged as `921b37d`, and [Pages run 43080719000](https://github.com/himanshu748/silentshift/actions/runs/43080719000) published its recorded evidence views. Anonymous browser checks passed before this candidate; the new [agent-value page](https://himanshu748.github.io/silentshift/agent-value.html#HO-045), [tour](https://himanshu748.github.io/silentshift/evidence-tour.html) and [receipt inspector](https://himanshu748.github.io/silentshift/receipts.html) are live.

An updated support follow-up is an **unsent Gmail draft** in the existing OEX thread. It reports the missing description-only editor choice, acknowledges the intended matching 0.3.3 package and makes clear that a reply is not a release prerequisite. The obsolete draft forbidding all IPM 0.3.3 publication must not be sent.

No merge, v0.3.3 tag/release, IPM/OEX publication/edit, support email send, new inference or new evaluation occurred. Finish the remaining native/replay gate before asking to merge; tag/GitHub release and OEX/IPM publish each retain separate exact-submit approvals. **Type 0.3.3 manually, never 1.0.0.** The public-registry 0.3.3 install remains a future post-publication check, distinct from the successful local-filesystem install.

## Protect the existing judge path before publishing

The launcher previously combined install-latest with expected version 0.3.2. A new 0.3.3 publication would therefore break its version check. The follow-up removes moving-latest selection while retaining the exact 0.3.2 version and release-matched assertion source. Its command-contract regression failed on the preceding launcher (**1 failed, 28 passed**) and passed after the fix (**29 passed**). Native resources and the tested 0.3.3 archive are unchanged. [Before](../evidence/release-033-nov12/launcher-regression-before.txt) · [after](../evidence/release-033-nov12/launcher-regression-after.txt). This is a harness repair, not another native or model evaluation.
