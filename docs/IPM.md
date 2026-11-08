# Native package maintenance and publication

**Installing the application? Use [INSTALL.md](../INSTALL.md).** This is a maintainer-only guide. No commands in this file were run to publish the 0.3.0 candidate.

## Release state, verified November 8, 2026

| Artifact | Version | Status |
| --- | --- | --- |
| Public native IPM package | **0.2.0** | Last anonymous public-registry observation, [verified install](evidence/judge-current-nov8.json); 44 classes and ten assets in that published snapshot |
| Current source `module.xml` | **0.3.0** | Candidate only, **not published or registry-installed**; 45 explicitly declared native classes and eleven `FileCopy` assets |
| Open Exchange app/workbench release | **0.2.1** | Publicly observed listing; this is a **separate** version from the native package |

The [0.3.0 changelog](../CHANGELOG.md) identifies changes since the [0.2.0 published source snapshot](https://github.com/himanshu748/silentshift/commit/d3637bbe85812035e6258320c81af93305e95560). [Candidate checks](evidence/ipm-030-candidate-linux-nov8.json) passed 207 Python tests, allowlisted staging, TypeScript and web build. **These are not native IRIS, live, browser or registry-install evidence.** The previous full native and browser results are preserved with their original execution scopes in [JUDGE_VERIFICATION.md](JUDGE_VERIFICATION.md).

After the owner publishes and anonymous registry metadata plus an actual clean `zpm "install silentshift"` verify **0.3.0**, the *public native* row may be updated to 0.3.0. Do not automatically infer that the separately released web frontend is included or that the OEX app's version is 0.3.0.

## What the manifest owns

The current `module.xml` declares `<SystemRequirements Version=">=2026.3" Interoperability="enabled" IPMVersion=">=0.10.10"/>`, **45** native class resources and **11** assets (including the new CSV native class/parser). These are the 0.3.0 candidate counts. The published 0.2.0 package had 44 classes and ten assets. No Java/.NET PEX, web `dist`, EAP image, credentials, private evidence or hosting resource is packaged.

The explicit resources leave unrelated `SilentShift.Test` diagnostics out of a release. There are no external native package dependencies; interoperability, Embedded Python and AI Hub are supplied by the separately licensed IRIS runtime. Python assets use the standard library.

The Compile-after hook calls `SilentShift.IPM.CheckTarget()` with a stopped-production/namespace/build guard. IPM may already have imported classes before that guard fails. The Activate-after hook validates the package asset root; Clean-before protects retained state during uninstall. Web applications, security roles, and production startup require the **explicit** `SilentShift.Setup.Install()` step. The native IPM package is not the TypeScript workbench, and `zpm "install silentshift"` alone neither configures an importer nor launches the web UI.

## Owner-only 0.3.0 publication runbook

**DO NOT EXECUTE as part of candidate preparation.** This runbook starts with an unreleased candidate and separates native checks, local packaging, optional test-registry publishing, and Open Exchange's public publication/moderation.

### A. Confirm source, version, and local checks

Run after the final candidate commits are present in `main` on the owner's machine:

```sh
git clone https://github.com/himanshu748/silentshift.git silentshift-release-030
cd silentshift-release-030
git rev-parse HEAD
grep '<Version>0.3.0</Version>' module.xml
uv run pytest -q
npm --prefix web ci --no-audit --no-fund
npm --prefix web run check
npm --prefix web run build
uv run python scripts/package_ipm.py --output .local/ipm/030-stage
```

Expected local staging inventory: `version=0.3.0`, **58 files, 45 native classes, 11 assets**. A staged tree alone is not an IRIS install or actual IPM archive. Review the tree, `package-inventory.json`, and `git diff` before any release action.

### B. Finish the owner's official 154U ARM64 native gate

In the owner's licensed, isolated environment, follow [INSTALL.md](../INSTALL.md). Use **new names**; do not reuse, overwrite or delete existing containers. For the two native modes, the repo's verification driver accepts the explicit candidate version:

```sh
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
uv run python scripts/verify_bonus_release.py \
  --source load --version 0.3.0 \
  --container silentshift-bonus-load-030-replay \
  --execution-mode recorded-replay --api-port 52863 --execute

# Only on the owner's machine with local Ollama running; performs fresh local inference:
uv run python scripts/verify_bonus_release.py \
  --source load --version 0.3.0 \
  --container silentshift-bonus-load-030-live \
  --execution-mode live --allow-model-calls --api-port 52873 --execute
```

Run the separate **second** keyless trace replay and the [CSV browser verifier](CSV_IMPORT.md#reproduce-the-browser-verification) plus browser suites in a configured source installation, preserving the output as dated `docs/evidence/` receipts. Confirm: clean IRIS with no application source mounts; 5 native classes / 12 methods; 5/5 live routes; both replays; 54 review assertions; 32 CSV browser checks; 207 Python; TypeScript/build; 38+16 browser checks. Inspect the generated IPM archive with `uv run python scripts/inspect_ipm.py <path-to-actual-ipm-0.3.0.tgz>`; do not present the stage as an actual package archive. Never publish credentials, runtime images, or private case data.

**Candidate-only caveat:** this fresh 0.3.0 native/browser gate **has not been executed** in the temporary Linux sandbox. The prior [clean source instance](evidence/source-isolated-nov8.json) and [same-instance upgrade](evidence/final-pass-nov8.json) are valid historical evidence, not new 0.3.0 receipts.

### C. Exact local IPM commands; `zpm publish` is NOT the public step

In a clean isolated IRIS `SILENTSHIFT` namespace, with the 0.3.0 stage copied into the container at `/home/irisowner/silentshift-release/stage`, these are the intended **local** IPM shell commands. They are shown here, **not executed**:

```objectscript
zpm "load /home/irisowner/silentshift-release/stage"
zpm "package silentshift -path /home/irisowner/silentshift-release/export/"
```

IPM's `publish` action, when used, targets a **configured writable registry**. Only if the owner specifically sets up a separate private/test registry may the owner optionally execute:

```objectscript
zpm "repo -r -n LocalTest -url <OWNER_CONTROLLED_WRITABLE_TEST_REGISTRY_URL>"
zpm "publish silentshift"
```

**Do not run `zpm "publish silentshift"` against the public community registry or assume it publishes there.** The [official Open Exchange publication workflow](https://docs.openexchange.intersystems.com/apps/ipm/) is the route for the public community registry. Exact test-repo setup depends on its authentication/configuration and must be verified separately; the URL above is a placeholder, not a runnable public endpoint.

### D. Owner submits the new version through Open Exchange

1. Sign in to [Open Exchange](https://openexchange.intersystems.com/) → Developer Portal → My Applications → **SilentShift**. Open the **existing** application and create a **new 0.3.0 package release** as the portal allows. Do not overwrite or unpublish the existing 0.2.0 package or remove the historical OEX app 0.2.1 release.
2. Add release notes from [CHANGELOG.md](../CHANGELOG.md) and select the verified GitHub source. Keep **Publish in Package Manager** and **Submit to Contest**, the dedicated `https://ideas.intersystems.com/ideas/DPI-I-689` association, video, both articles, existing approved description, and other current fields. Do not add a demo URL or re-submit the questionnaire. The portal's options are subject to its actual UI.
3. **Send for approval** if required. OEX editing/release approval may enter moderation, so do not report publication on submission alone. Keep an owner receipt and note any rejection/duplicate-version response.
4. Once anonymous public metadata confirms the registry serves **0.3.0**, repeat a fresh no-source-mount clean `zpm "install silentshift"` with `--version 0.3.0 --install-latest` as in [INSTALL.md](../INSTALL.md#optional-check-without-a-model). Confirm the installed native module's version; record a new receipt. Update published-versus-main claims only after the check succeeds.
5. Confirm the [Contest 49 listing](https://openexchange.intersystems.com/contest/49) remains visible. Organizer acceptance of the two-point IPM bonus and of DPI-I-689 is **independent** of submission, registry visibility, and native execution.

## Historical 0.1.0 and existing-namespace evidence

The November 3 clean local 0.1.0 archive installed 43 classes and nine assets, with 53 files / 75,003 bytes and SHA-256 `0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6`. Explicit setup then passed five final native routes, four of five expected model proposals and all four tool reads. [Historical receipt](evidence/ipm-clean-install.json). That local archive hash is not the public registry artifact hash.

For an existing namespace, `verify_ipm_native.py` remains a bounded **stopped-production** load/package check comparing all ten application/workflow table row counts. It leaves production stopped; it is **not** clean installation or registry verification. Never run it during active intake or investigations.
