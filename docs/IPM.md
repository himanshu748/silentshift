# Native package maintenance and publication

**Installing the application? Use [INSTALL.md](../INSTALL.md).** This file is for package maintainers. It is not part of the installation path.

Public native package **0.2.0** remains the last published version. The source manifest now declares **0.3.0 candidate**, with **45 classes and 11 assets**. These counts come from the candidate manifest, not the historical public archive. App/workbench **0.2.1** and OEX **0.2.1** have separate versions. The target remains **154U ARM64**, IPM 0.10.10 or newer and an interoperability-enabled `SILENTSHIFT` namespace. Package installation alone does not configure accounts or start the production.

## What the manifest owns

`module.xml` declares `<SystemRequirements Version=">=2026.3" Interoperability="enabled" IPMVersion=">=0.10.10"/>`, every application class explicitly, and bounded `FileCopy` assets. Explicit resources keep separately loaded `SilentShift.Test` diagnostics out of a release. There are no external module dependencies: interoperability, Embedded Python and AI Hub are supplied by the declared IRIS image; the runtime Python code uses the standard library. The React workbench is run separately from matching source; IPM does not install its web bundle.

The Compile-after hook calls `IPM.CheckTarget()`: the namespace/build must match and production must be stopped. IPM may already have imported classes before that guard fails, so select the correct namespace before loading. The Activate-after hook configures and validates the installed asset root. The Clean-before hook protects retained application state during uninstall.

Web applications and roles are deliberately created by the **explicit** `SilentShift.Setup.Install()` operation, using private environment configuration. Defining them again as automatic package web-app resources would create a second security owner and hide a consequential setup step. Setup configures the authenticated `/silentshift` API, internal `/silentshift-provider` gateway and native trace portal. It seeds independent references, enables production auto-start and starts `SilentShift.Production`; it invokes no model.

## Owner publication commands — not executed

The [candidate changelog](../CHANGELOG.md) is release-ready copy; the [judge gate](JUDGE_VERIFICATION.md) determines whether it is safe to publish. **Do not publish while that gate is incomplete or failing.** No package, registry release, Git tag or OEX edit is part of candidate preparation.

For a prepared namespace in a disposable build-154U container, load the allowlisted candidate and generate a local archive. Substitute the actual verified container and staging path printed by the candidate receipt; do not use the active production instance:

```sh
uv run python scripts/package_ipm.py --output .local/ipm/owner-030-stage
docker --context colima-silentshift cp .local/ipm/owner-030-stage "$SS_CANDIDATE_CONTAINER":/home/irisowner/silentshift-030-stage
docker --context colima-silentshift exec -it "$SS_CANDIDATE_CONTAINER" iris session IRIS -U SILENTSHIFT
```

In that namespace, with production stopped:

```objectscript
zpm "load /home/irisowner/silentshift-030-stage"
zpm "package silentshift -path /home/irisowner/silentshift-030-export/"
set module=##class(%IPM.Storage.Module).NameOpen("silentshift")
write module.VersionString,!
```

The expected identity is `0.3.0`. Staging and packaging are local operations, not publication. A stopped-production load is not a clean-install result.

### Public community registry: use OEX

[Official OEX instructions](https://docs.openexchange.intersystems.com/apps/ipm/) state that Open Exchange is the publication route for `pm.community.intersystems.com`. Do not configure a direct public publishing credential or run `zpm "publish silentshift"` against that registry. The command exists for an explicitly configured writable private/testing registry; it is not an extra required public-publication step. [Official CLI reference](https://github.com/intersystems/ipm/wiki/02.-CLI-commands#publish).

After the candidate gate passes, the owner can:

1. Confirm the verified candidate is pushed to `himanshu748/silentshift` and root `module.xml` declares `0.3.0`.
2. Sign in to OEX → **My Applications → SilentShift → Add new release**. Enter release **0.3.0** and the changelog above, including the separate-workbench boundary. This is a new owner decision; the current OEX release stays 0.2.1 until then.
3. Keep **Publish in Package Manager** and **Submit to Contest** checked. Retain DPI-I-689, both articles and YouTube. Leave Demo URL empty. Never choose **Unpublish** or **Cancel approval**.
4. Submit the release as the portal permits and record the confirmation and moderation state. Do not count public visibility as technology-bonus qualification.
5. Wait for registry version 0.3.0, then run the fresh public-registry replay gate below. Verify the installed version from actual output before calling it public. A duplicate-0.2.0 email is not proof of a 0.3.0 publication.

### After publication: verify the registry

From a clean clone prepared with the local image, pinned IPM client and private recorded-replay configuration in [INSTALL.md](../INSTALL.md#optional-check-without-a-model):

```sh
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest --version 0.3.0 \
  --execution-mode recorded-replay --container silentshift-bonus-registry-owner-030 \
  --api-port 52943 --execute
uv run python scripts/trace_example.py --api http://127.0.0.1:52943/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-registry-owner-030 \
  --output .local/ipm/owner-030-second-replay.json
```

The first command executes the literal `zpm "install silentshift"`, checks that **0.3.0** was installed, starts the production, runs the native suite and runs the first replay. The second repeats the API example. These commands are prepared, not results. The explicit version-qualified alternative inside a prepared namespace is `zpm "install silentshift 0.3.0"`.

Until those checks succeed, public IPM remains **0.2.0 verified**, while **0.3.0 is a source candidate**. After they succeed, retain the old dated receipts and add the new registry receipt/date; update the published-version sentence and OEX state from readback. Source-only verification never substitutes for this post-publication check. Confirm SilentShift still appears on [contest 49](https://openexchange.intersystems.com/contest/49).

## Historical 0.1.0 evidence

The November 3 clean local archive installed 43 classes and nine assets, with 53 files / 75,003 bytes and SHA-256 `0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6`. Explicit setup then passed five final native routes, four of five expected model proposals and all four tool reads. [Historical receipt](evidence/ipm-clean-install.json). That local archive hash is not the public registry artifact hash.

For an existing namespace, `verify_ipm_native.py` remains a bounded **stopped-production** load/package check and compares all ten application/workflow table row counts. It leaves production stopped; its receipt is not a clean install or registry-install result. Never run it while intake or investigations are active.
