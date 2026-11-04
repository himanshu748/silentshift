# Install and publish SilentShift with IPM

`silentshift` **0.2.0** packages 44 native classes and ten runtime assets. The verified target is official ARM64 IRIS Community AI Hub **2026.3.0AI.154.0**, reported by `$ZVERSION` as **2026.3.0AI (Build 154U)**. Build 109 has not been tested. The module requires IPM **0.10.10 or newer** and an interoperability-enabled **SILENTSHIFT** namespace.

Installation imports classes and copies the standard-library Python modules, frozen scenarios, recorded-provider fixture and MIT license. It does not create accounts, activate web applications, start the production or call a model. The React workbench remains a separate build. The runtime image and model weights are not in the package.

## Public registry

The public **0.2.0** metadata and manifest returned HTTP 200 on November 4, 2026. A **fresh public-registry install passed**, followed by explicit production startup, all five native test classes / 12 methods and the no-key API replay (12/12, session 24, zero deliveries). All 55 runtime/package files in the registry cache matched the released source. [Public-install receipt](evidence/bonus-020-registry-install.json). Source loading remains a separately identified result.

In a prepared **SILENTSHIFT** namespace with IPM installed:

```objectscript
zpm "install silentshift"
```

For a reproducible version-qualified verification against the public registry:

```objectscript
zpm "repo -r -n PublicCommunity -url https://pm.community.intersystems.com/ -user """" -pass """" -publish 0 -read-only 1"
zpm "install PublicCommunity/silentshift 0.2.0 -synchronous"
```

The inner empty quotes must be doubled if this shell text is passed as an ObjectScript string literal. The automated driver below performs that escaping; in the interactive `zpm` shell, enter the repository command without an outer ObjectScript string. No publisher credentials are needed to install a public package.

## What the manifest owns

`module.xml` declares `<SystemRequirements Version=">=2026.3" Interoperability="enabled" IPMVersion=">=0.10.10"/>`, all 44 classes explicitly, and ten `FileCopy` assets. Explicit resources keep separately loaded `SilentShift.Test` diagnostics out of a release. There are no external module dependencies: interoperability, Embedded Python and AI Hub are supplied by the declared IRIS image; the runtime Python code uses the standard library.

The Compile-after hook calls `IPM.CheckTarget()`: the namespace/build must match and production must be stopped. IPM may already have imported classes before that guard fails, so select the correct namespace before loading. The Activate-after hook configures and validates the installed asset root. The Clean-before hook protects retained application state during uninstall.

Web applications and roles are deliberately created by the **explicit** `SilentShift.Setup.Install()` operation, using private environment configuration. Defining them again as automatic package web-app resources would create a second security owner and hide a consequential setup step. Setup configures the authenticated `/silentshift` API, internal `/silentshift-provider` gateway and native trace portal. It seeds independent references, enables production auto-start and starts `SilentShift.Production`; it invokes no model.

## Reproduce a fresh source load

Prerequisites: the authorized official build-154 ARM64 image already loaded as `silentshift-iris:2026.3.0AI.154.0`, the official Web Gateway image already present, Docker/Compose, Colima profile `silentshift`, and private `.env` configured as in the README. Use unique new container names. Both host and VM Docker free space are checked; existing stacks and volumes are preserved.

Fetch and verify the pinned official IPM installer:

```sh
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
```

IPM 0.10.10 is pinned to 1,593,780 bytes and SHA-256 `daa2adabd66b488f57187d29712e54b0c25bbe000794fbf2a35a882c458b788a`. It comes from the [official IPM release](https://github.com/intersystems/ipm/releases/tag/v0.10.10).

```sh
uv run python scripts/verify_bonus_release.py --source load \
  --container silentshift-bonus-load-example --api-port 52793 --execute
```

The driver begins with an official container without mounts or SILENTSHIFT. It creates the isolated namespace, enables authenticated CallIn for Embedded Python, imports the pinned client, disables IPM analytics, copies a bounded source stage and executes real `load /home/irisowner/silentshift-bonus/stage`. It verifies installed version 0.2.0 and exports IPM's actual archive. After separate explicit setup it runs every native `%UnitTest` class, checks assertion results rather than the manager's return value alone, and runs the real API replay.

The provider mode is `recorded-replay`. The native SDK and four tools execute, but no fresh inference, embedding call or external API key is needed. The source is copied into the container; it is never bind mounted. Logs, configuration and receipts remain private below `.local/ipm/bonus-runs/`. Containers are retained for inspection.

Repeat the replay through the installed production:

```sh
uv run python scripts/trace_example.py \
  --api http://127.0.0.1:52793/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-load-example
```

The result must be QUARANTINED, zero deliveries, five native provider pairs, four real tool reads and `checks=12/12; passed=true`. Its printed Visual Trace URL is specific to that run. Inspecting message bodies needs an existing portal account with native message-content read permission; the standard reviewer role grants graph access only.

## Verify a public install in a second clean container

The following path was verified with container `silentshift-bonus-registry-20261104` on port 52813. To repeat, use a new name and port:

```sh
uv run python scripts/verify_bonus_release.py --source public-registry \
  --version 0.2.0 --container silentshift-bonus-registry-example \
  --api-port 52803 --execute
```

This executes **`install PublicCommunity/silentshift 0.2.0 -synchronous`** against `https://pm.community.intersystems.com/` with empty credentials. No application source stage or local application archive supplies that installation. The test classes are copied separately only after package installation. Production startup, the full native test suite and the replay must pass against the installed package. A badge, public manifest or successful download alone is not this proof.

For live local inference, leave `SILENTSHIFT_PROVIDER_MODE=live` (the default), configure the local Ollama model/embedding endpoint and use the README bootstrap. `verify_native.py --allow-model-calls` exercises five actual local investigations. Replay is never counted as live model evidence.

## Publish through Open Exchange

Release **0.2.0** was published successfully on November 4. The public app displays version 0.2.0, `zpm install silentshift`, and its linked DPI-I-689 idea. The description refresh was separately sent for approval; SilentShift remains listed in contest 49. [Release confirmation](assets/oex-020-release-published.jpg) · [description approval request](assets/oex-020-description-sent.jpg).

The [official publication workflow](https://docs.openexchange.intersystems.com/apps/ipm/) uses Open Exchange to publish to the community registry. There is no separate direct-registry publishing step to invent.

1. Commit and push the verified source to `https://github.com/himanshu748/silentshift`, with root `module.xml` at 0.2.0. Do not publish EAP runtime images, secrets or private evidence.
2. Sign in to Open Exchange → Developer Portal → My Applications → **SilentShift**. Create a **new release** with version 0.2.0 and factual release notes. Preserve the existing app and approval request; never choose Unpublish or Cancel approval.
3. Preserve **Publish in Package Manager**, **Submit to Contest**, the dedicated `https://ideas.intersystems.com/ideas/DPI-I-689` field and the existing demo URL. Refresh the description from the verified README and save/send the new release for approval as the portal permits.
4. Read back the saved release and moderation status. Wait for the anonymous registry metadata/manifest to list 0.2.0; then run the second clean-container command above. If approval is pending, record that blocker and do not claim a registry install passed.
5. Confirm SilentShift remains on [contest 49](https://openexchange.intersystems.com/contest/49). Organizer acceptance of the potential two-point IPM bonus is separate from package publication.

## Historical 0.1.0 evidence

The November 3 clean local archive installed 43 classes and nine assets, with 53 files / 75,003 bytes and SHA-256 `0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6`. Explicit setup then passed five final native routes, four of five expected model proposals and all four tool reads. [Historical receipt](evidence/ipm-clean-install.json). That local archive hash is not the public registry artifact hash.

For an existing namespace, `verify_ipm_native.py` remains a bounded **stopped-production** load/package check and compares all ten application/workflow table row counts. It leaves production stopped; its receipt is not a clean install or registry-install result. Never run it while intake or investigations are active.
