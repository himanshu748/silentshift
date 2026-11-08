# Changelog

## 0.3.0 - prepared for release, not published (2026-11-08)

**Status:** the repository manifest declares `0.3.0`, but **public IPM still serves `0.2.0`** until the owner publishes and verifies a new Open Exchange release. The Open Exchange application was last observed publicly as `0.2.1`. No tag, public registry push, or listing edit accompanies this preparation.

This is the native IPM package update since the publicly verified `0.2.0` snapshot at [`d3637bb`](https://github.com/himanshu748/silentshift/commit/d3637bbe85812035e6258320c81af93305e95560). The exact commit inventory and earlier source-vs-registry proof are in [Submission checklist](docs/SUBMISSION_CHECKLIST.md#published-vs-main).

### Added

- **Bounded CSV order-feed intake** through the native InterSystems IRIS interoperability production, including explicit importer authority, independently approved reference exports, input validation and idempotent per-line investigation. Unsupported unit/quantity changes stay held; an independently authorized matching line can reach the simulator. [Native change `09f71b7`](https://github.com/himanshu748/silentshift/commit/09f71b7c2896e7b27adbd2b539a0fcd1867741b8).
- **Interactive CSV Import workbench** for previewing incoming lines beside their governing references, recording approved sources, displaying native routing/results, opening cases and recovering repeated imports without redispatch. Includes mobile, keyboard, offline/recovery and reduced-motion coverage. [Workbench change `ab00ecc`](https://github.com/himanshu748/silentshift/commit/ab00ecccd931bec1c9aa6f8a9efc9953b9c88560) and [presentation finish `df59142`](https://github.com/himanshu748/silentshift/commit/df591420c06ed081623f6178804359ceb1686964).
- **Interactive product landing/workbench walkthrough** that illustrates the order/reference/case journey. [`770baab`](https://github.com/himanshu748/silentshift/commit/770baabd2c5e317918003dde05986eed476a75ef).

### Improved

- **Image optimization** for repository/web assets. [`fbd3947`](https://github.com/himanshu748/silentshift/commit/fbd39471f93dba94e007e405e8e00f008df224d6).
- **Source bootstrap compile scope:** normal installation compiles the checked-in source directory rather than all existing classes in the namespace, so an unrelated retained diagnostic class no longer blocks reload. [`e61a961`](https://github.com/himanshu748/silentshift/commit/e61a961228cdf3d0f4ebc3a274b46ad1894a43b1). Native execution and policy semantics are unchanged.
- **Release preparation:** native `module.xml` version `0.3.0`; the allowlisted local packaging/test tools now validate and report the candidate version instead of hard-coding `0.2.0`.

### Scope and verification caveats

- `module.xml` packages the native classes and declared Python/fixture assets, **not the independently built TypeScript web frontend**. A judge installing only `zpm "install silentshift"` after the registry update obtains the native CSV backend, but must follow [INSTALL.md](INSTALL.md) to run the web workbench and configure importer permission.
- The earlier [build-154 source and native evidence](docs/JUDGE_VERIFICATION.md) includes 5 native classes / 12 test methods, five live scenarios, two replay checks, 54 review assertions, 32 CSV browser checks, 207 pytest, TypeScript/build, and 38+16 browser checks. These receipts have different scopes (fresh instance versus same-instance upgrade) and predate the version-only candidate. Do not present them as a new `0.3.0` registry install.
- A new isolated Linux release-tooling check is recorded in [the 0.3.0 candidate receipt](docs/evidence/ipm-030-candidate-linux-nov8.json); it is **not** an IRIS native run. Final clean IRIS/source, native replay, and CSV browser validation still require the owner's licensed build-154 environment unless independently re-evidenced.
- Synthetic orders and IRIS simulator receipts only. No hosted demo, real partner delivery, Embedded Python/Java/.NET PEX/online-demo bonus claim, organizer award, or registry publication is implied.

### Owner publication handoff

See [docs/IPM.md](docs/IPM.md#owner-only-030-publication-runbook) for the **not executed** staging/`zpm load`/`zpm package` and optional writable-test-registry `zpm publish` commands. Public Community Registry publication is initiated via **Open Exchange** rather than by direct unauthenticated `zpm publish`. After approval, independently verify public registry version `0.3.0` and a fresh `zpm "install silentshift"` result before changing any published-status statement.

## 0.2.0 - public native IPM package (2026-11-04)

The original verified public native release, snapshot [`d3637bb`](https://github.com/himanshu748/silentshift/commit/d3637bbe85812035e6258320c81af93305e95560), installed and replayed on IRIS Community AI Hub `2026.3.0AI.154.0`. It does not include the later CSV order-feed work.
