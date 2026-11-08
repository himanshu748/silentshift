# Native package maintenance and publication

**Installing the application? Use [INSTALL.md](../INSTALL.md).** This file is for package maintainers. It is not part of the installation path.

Public native package and OEX release **0.3.0** are published. The manifest and public archive contain **45 classes and 11 assets**; every native source file/asset and the manifest matched the verified source. [Archive comparison](evidence/ship-030-public-artifact.json). A [fresh registry installation](evidence/ship-030-registry.json) passed native tests and both recorded replays. React workbench **0.2.1** has a separate version. The target remains **154U ARM64**, IPM 0.10.10 or newer and an interoperability-enabled `SILENTSHIFT` namespace. Package installation alone does not configure accounts or start the production.

## What the manifest owns

`module.xml` declares `<SystemRequirements Version=">=2026.3" Interoperability="enabled" IPMVersion=">=0.10.10"/>`, every application class explicitly, and bounded `FileCopy` assets. Explicit resources keep separately loaded `SilentShift.Test` diagnostics out of a release. There are no external module dependencies: interoperability, Embedded Python and AI Hub are supplied by the declared IRIS image; the runtime Python code uses the standard library. The React workbench is run separately from matching source; IPM does not install its web bundle.

The Compile-after hook calls `IPM.CheckTarget()`: the namespace/build must match and production must be stopped. IPM may already have imported classes before that guard fails, so select the correct namespace before loading. The Activate-after hook configures and validates the installed asset root. The Clean-before hook protects retained application state during uninstall.

Web applications and roles are deliberately created by the **explicit** `SilentShift.Setup.Install()` operation, using private environment configuration. Defining them again as automatic package web-app resources would create a second security owner and hide a consequential setup step. Setup configures the authenticated `/silentshift` API, internal `/silentshift-provider` gateway and native trace portal. It seeds independent references, enables production auto-start and starts `SilentShift.Production`; it invokes no model.

## Owner-only 0.3.0 publication runbook

**Completed under the owner's subsequent authorization. Do not republish 0.3.0.** The [fresh-source candidate gate](evidence/candidate-030.json), OEX publication and [fresh public-registry gate](evidence/ship-030-registry.json) all passed. The commands below retain the preparation/publication procedure for maintainers; they are not installation steps or a request to create another release. No Git tag was created. The updated description is separately awaiting moderation. [External-state receipt](evidence/ship-030-publication.json).

For a prepared namespace in a disposable build-154U container, load the allowlisted candidate and generate a local archive. Substitute the actual verified container and staging path printed by the candidate receipt; do not use the active production instance:

```sh
SS_CANDIDATE_CONTAINER=silentshift-bonus-load-030-nov8
docker --context colima-silentshift start "$SS_CANDIDATE_CONTAINER"
uv run python scripts/package_ipm.py --output .local/ipm/owner-030-stage
docker --context colima-silentshift cp .local/ipm/owner-030-stage "$SS_CANDIDATE_CONTAINER":/home/irisowner/silentshift-030-stage
docker --context colima-silentshift exec -it "$SS_CANDIDATE_CONTAINER" iris session IRIS -U SILENTSHIFT
```

In that namespace, with production stopped:

```objectscript
set sc=##class(Ens.Director).StopProduction()
if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt
zpm "load /home/irisowner/silentshift-030-stage"
zpm "package silentshift -path /home/irisowner/silentshift-030-export/"
set module=##class(%IPM.Storage.Module).NameOpen("silentshift")
write module.VersionString,!
```

The expected identity is `0.3.0`. Staging and packaging are local operations, not publication. A stopped-production load is not a clean-install result.

### Public community registry: use OEX

[Official OEX instructions](https://docs.openexchange.intersystems.com/apps/ipm/) state that Open Exchange is the publication route for `pm.community.intersystems.com`. Do not configure a direct public publishing credential or run `zpm "publish silentshift"` against that registry. The command exists for an explicitly configured writable private/testing registry; it is not an extra required public-publication step. **Only** after configuring and selecting a private writable test registry, the optional local test command is `zpm "publish silentshift"`. Never use it to try to publish to the public community registry. [Official CLI reference](https://github.com/intersystems/ipm/wiki/02.-CLI-commands#publish).

The publication used the following owner-authorized sequence; it is retained as reference:

1. Confirm the verified candidate is pushed to `himanshu748/silentshift` and root `module.xml` declares `0.3.0`.
2. Sign in to OEX → **My Applications → SilentShift → Add new release**. Enter release **0.3.0** and the changelog above, including the separate-workbench boundary. The portal first saved a Draft; publishing that draft completed the release. The live signed-out listing then showed 0.3.0.
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

The first command executes the literal `zpm "install silentshift"`, checks that **0.3.0** was installed, starts the production, runs the native suite and runs the first replay. The second repeats the API example. The executed equivalents used container `silentshift-bonus-registry-public-030-nov8`; [exact commands and output](JUDGE_VERIFICATION.md#public-030-install--november-8-2026-utc) record the results. The explicit version-qualified alternative inside a prepared namespace is `zpm "install silentshift 0.3.0"`.

These checks succeeded on November 8: native **0.3.0**, production started, **5 classes / 12 methods passed**, two **12/12** replays. [Registry receipt](evidence/ship-030-registry.json) · [second replay](evidence/ship-030-repeat.json). The installed CSV preview returned HTTP **200** for two synthetic lines and HTTP **422** for a 21-row bounded rejection; no import/inference occurred in that preview check. [Receipt](evidence/ship-030-public-csv-preview.json). SilentShift remains listed on [contest 49](https://openexchange.intersystems.com/contest/49). Old 0.2.0 receipts remain historical; source-only verification never substitutes for public installation.

## Historical 0.1.0 evidence

The November 3 clean local archive installed 43 classes and nine assets, with 53 files / 75,003 bytes and SHA-256 `0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6`. Explicit setup then passed five final native routes, four of five expected model proposals and all four tool reads. [Historical receipt](evidence/ipm-clean-install.json). That local archive hash is not the public registry artifact hash.

For an existing namespace, `verify_ipm_native.py` remains a bounded **stopped-production** load/package check and compares all ten application/workflow table row counts. It leaves production stopped; its receipt is not a clean install or registry-install result. Never run it while intake or investigations are active.
