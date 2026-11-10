# Native package maintenance and publication

**Installing the application? Use [INSTALL.md](../INSTALL.md).** This file is for package maintainers. It is not part of the installation path.

Public native package and OEX release **0.3.0** are published. The published 0.3.0 manifest and archive contain **45 classes and 11 assets**; every native source file/asset and the manifest matched the verified source. [Archive comparison](evidence/ship-030-public-artifact.json). A [fresh registry installation](evidence/ship-030-registry.json) passed native tests and both recorded replays. React workbench **0.2.1** has a separate version. The target remains **154U ARM64**, IPM 0.10.10 or newer and an interoperability-enabled `SILENTSHIFT` namespace. Package installation alone does not configure accounts or start the production.

## Local backend-polish branch — not a new published package

The public registry remains **0.3.0**. `backend-polish-nov10` now declares an **unpublished 0.3.1 candidate** in `module.xml`, `pyproject.toml` and the lockfile. A [fresh source load](evidence/voting-finish-nov10/candidate-031-load.json) passed explicit startup, all native tests and recorded replay; the [repeat replay](evidence/voting-finish-nov10/candidate-031-replay-2.json) also passed. Its real exported archive then passed an [actual local-filesystem repository install in a second fresh container](evidence/voting-finish-nov10/candidate-031-install.json), where the application stayed empty and stopped. This is clean local package verification, not a public-registry 0.3.1 install. [Candidate summary](evidence/voting-finish-nov10/candidate-031-summary.json).

For installation, use the interoperability-enabled **SILENTSHIFT** namespace and the legally obtained **2026.3.0AI.154.0 Community / 154U ARM64** image. No other build or architecture is qualified here. Setup enrolls exactly one configured reviewer in the native `ReviewWorklist`; it refuses another member rather than silently widening that role. CSV imports are capped at **20 rows**, and importing independent references requires explicit `SSImporter` authorization. The verified live configuration uses only local Ollama **qwen3-silentshift:4b-instruct** and local **all-minilm:22m** embeddings; replay performs no fresh inference. This source branch already contains optional provider adapters, so it would be inaccurate to describe every possible configured source route as pinned by `Lease.LocalHost`. No remote-provider execution is qualified by these checks.

### Manual cleanup: administrator review, never automatic deletion

Back up the namespace, native messages, Workflow tasks, original account/service settings and required evidence first. Stop the production and disable its automatic restart before cleanup. Package uninstall refuses a populated namespace; it is not an application-data purge. No new `Setup.Uninstall()` is provided or claimed tested.

- Remove only the application-owned web applications `/silentshift`, `/silentshift-provider` and `/csp/silentshift`, after removing gateway routes to them.
- Remove application role memberships, then the owned roles `SSViewer`, `SSReviewer`, `SSImporter`, `SSApplication`, `SSProviderTransport` and `SSNativeTrace`. Remove resources `SSView`, `SSReview` and `SSImport` only after checking that no other application uses them. The installer-created `%DB_SILENTSHIFT` database resource is separate; retain it while any database or mapping uses it.
- Retire the two configured viewer/reviewer users only if this installation created them and no other application uses them. Setup preserves existing users. Remove only this application's Workflow `ReviewWorklist` membership and reviewer definition after its tasks are archived/resolved; never delete other applications' worklist rows.
- Preserve or deliberately archive SQL data in `SilentShift.Data.*`, `SilentShift.Workflow.ReviewTask`, native message headers/bodies, audit events and delivery/review receipts. The generated storage definitions show their locations. Do not bulk-kill `^Ens*`, `^EnsLib*` or shared Workflow globals.
- In the dedicated namespace, review application-owned `^SilentShift.Config`, `^SilentShift.Diagnostics`, `^SilentShift.PartnerFiles`, `^SilentShift.CSVImports`, `^SilentShift.CSVSources`, `^SilentShift.Lock` and `^SilentShiftPilotImport`. Some are runtime/import state, not created by Setup alone. `^CacheTemp.SilentShift.Provider` lives in IRISTEMP: discard only expired owned transport state after hosts stop. Preserve the partner inbox and its `.done`, `.hold`, `.work` and acknowledgement evidence until retention is decided.
- Restore prior `%Service_CallIn`, `%Service_WebGateway` and `CSPSystem` settings from the administrator's backup; these are existing system objects, not objects to delete. Remove the namespace/database only when it is dedicated to SilentShift, all mappings are checked, required data is archived and no other application depends on it.

This is an ownership checklist, not an executed cleanup or rollback guarantee. No data, role, user, resource or web application was deleted in this pass.

## What the manifest owns

`module.xml` declares `<SystemRequirements Version=">=2026.3" Interoperability="enabled" IPMVersion=">=0.10.10"/>`, every application class explicitly, and bounded `FileCopy` assets. Explicit resources keep separately loaded `SilentShift.Test` diagnostics out of a release. There are no external module dependencies: interoperability, Embedded Python and AI Hub are supplied by the declared IRIS image; the runtime Python code uses the standard library. The React workbench is run separately from matching source; IPM does not install its web bundle.

The Compile-after hook calls `IPM.CheckTarget()`: the namespace/build must match and production must be stopped. IPM may already have imported classes before that guard fails, so select the correct namespace before loading. The Activate-after hook configures and validates the installed asset root. The Clean-before hook protects retained application state during uninstall.

Web applications and roles are deliberately created by the **explicit** `SilentShift.Setup.Install()` operation, using private environment configuration. Defining them again as automatic package web-app resources would create a second security owner and hide a consequential setup step. Setup configures the authenticated `/silentshift` API, internal `/silentshift-provider` gateway and native trace portal. It seeds independent references, enables production auto-start and starts `SilentShift.Production`; it invokes no model.

## Owner-only 0.3.1 publication runbook

**Prepared only; do not execute without the owner's separate approvals.** The tested candidate commit is `7b3d5efafb07fd54530c912f6b9cdbb710462020`. The [exported package](evidence/voting-finish-nov10/candidate-031-archive.json) is a local artifact under the fresh clone's ignored `.local/ipm/bonus-runs/silentshift-bonus-load-candidate-031-nov10/`; no EAP image or credential belongs in a release.

To reproduce staging from the reviewed candidate checkout, in a **new** destination:

```sh
uv run python scripts/package_ipm.py --output .local/ipm/owner-031-stage
```

For a disposable 154U ARM64 interoperability namespace with production stopped, copy that stage into the container and run:

```objectscript
zpm "load /home/irisowner/silentshift-031-stage"
zpm "package silentshift -path /home/irisowner/silentshift-031-export/"
set module=##class(%IPM.Storage.Module).NameOpen("silentshift")
write module.VersionString,!
```

The expected version is `0.3.1`. The [executed clean-load command](evidence/voting-finish-nov10/candidate-031-command.txt) and [actual archive-install command](evidence/voting-finish-nov10/candidate-031-install-command.txt) are complete reproducibility references; they do not authorize reusing an active production container or overwriting an existing verification directory.

Owner action order:

1. Approve opening the draft backend PR; review its precise scope. This approval covers opening only.
2. Only after acceptance, approve merging the reviewed backend head to main **with a merge commit, no squash or force-push**. Inspect the merge SHA; do not assume it is identical to a tested commit without comparing native package and workbench files. Then close superseded PRs and prepare safe branch deletion through their separate gates. Submit the existing **public-0.3.0 description correction** separately, preserving contest/IPM/idea/video/articles and any pending approval. The requested source-version exception applies because Phase 3H has already passed; that does not publish 0.3.1.
3. Approve the **v0.3.1 tag** at that reviewed merge SHA, then separately approve its GitHub release. Use the changelog's 0.3.1 section and state native 0.3.1 / React 0.2.1. Never point an existing version tag at different source.
4. Approve **public IPM publication** through Open Exchange's existing SilentShift application → Add new release → 0.3.1. Use the approved GitHub version archive as source; keep IPM and Submit to Contest selected, preserve the DPI-I-689 field, video, MP4 and both articles. Review/save/send/publish only for that exact approved action; never cancel a pending approval. If the portal couples release and IPM publication, record that coupling before confirmation rather than inventing a separate direct registry action.
5. Approve any later **OEX version/description update** separately if the publication flow did not already apply it. Do not claim 0.3.1 public until anonymous readback and a new clean registry install prove it.

Public community publication uses OEX, as the official instructions linked below explain. **Do not run `zpm "publish silentshift"` against the public community registry.** That command is for an explicitly configured writable private/test registry, not a required public step.

After publication is actually confirmed, verify the new public version in a fresh container with the candidate's own tests and private local `.env`:

```sh
SS_CANDIDATE_SUBNET=$(uv run python -c 'import sys; sys.path.insert(0, "scripts"); from judge_replay import unused_network_subnet; print(unused_network_subnet(["docker", "--context", "colima-silentshift"]))')
uv run python scripts/verify_bonus_release.py \
  --source public-registry --version 0.3.1 --install-latest \
  --execution-mode recorded-replay \
  --container silentshift-bonus-registry-031-owner \
  --api-port 53063 --network-subnet "$SS_CANDIDATE_SUBNET" \
  --env-file .env --execute
```

Choose a genuinely unused subnet and new container name. `--install-latest` executes literal `zpm "install silentshift"` and then requires the installed version to be 0.3.1. The existing `judge-replay.sh` deliberately remains pinned to **public 0.3.0** until a separately reviewed publication follow-up updates its version and release-matched assertion source. Candidate proof must not silently change that public-package command.

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
