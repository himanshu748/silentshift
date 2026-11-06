# Native package maintenance and publication

**Installing the application? Use [INSTALL.md](../INSTALL.md).** This file is for package maintainers. It is not part of the installation path.

Public native package **0.2.0** contains 44 classes and ten assets. It requires the verified **154U ARM64** runtime, IPM 0.10.10 or newer and an interoperability-enabled `SILENTSHIFT` namespace. App/workbench **0.2.1** has a separate version. Package installation alone does not configure accounts or start the production; the single installation guide covers those steps.

## What the manifest owns

`module.xml` declares `<SystemRequirements Version=">=2026.3" Interoperability="enabled" IPMVersion=">=0.10.10"/>`, all 44 classes explicitly, and ten `FileCopy` assets. Explicit resources keep separately loaded `SilentShift.Test` diagnostics out of a release. There are no external module dependencies: interoperability, Embedded Python and AI Hub are supplied by the declared IRIS image; the runtime Python code uses the standard library.

The Compile-after hook calls `IPM.CheckTarget()`: the namespace/build must match and production must be stopped. IPM may already have imported classes before that guard fails, so select the correct namespace before loading. The Activate-after hook configures and validates the installed asset root. The Clean-before hook protects retained application state during uninstall.

Web applications and roles are deliberately created by the **explicit** `SilentShift.Setup.Install()` operation, using private environment configuration. Defining them again as automatic package web-app resources would create a second security owner and hide a consequential setup step. Setup configures the authenticated `/silentshift` API, internal `/silentshift-provider` gateway and native trace portal. It seeds independent references, enables production auto-start and starts `SilentShift.Production`; it invokes no model.

## Publish through Open Exchange

Native package **0.2.0** was published successfully on November 4 and remains the verified registry version. OEX frontend/product release **0.2.1** was subsequently submitted and read back under Published releases; listing edits still show Awaiting Review. Its download archive still points to native backend 0.2.0. The dedicated idea field and IPM/contest choices are retained in the owner view; SilentShift remains in contest 49. [Release confirmation](assets/oex-020-release-published.jpg) · [description approval request](assets/oex-020-description-sent.jpg).

The [official publication workflow](https://docs.openexchange.intersystems.com/apps/ipm/) uses Open Exchange to publish to the community registry. There is no separate direct-registry publishing step to invent.

1. Commit and push the verified source to `https://github.com/himanshu748/silentshift`, with root `module.xml` at 0.2.0. Do not publish EAP runtime images, secrets or private evidence.
2. Sign in to Open Exchange → Developer Portal → My Applications → **SilentShift**. Create a **new release** with version 0.2.0 and factual release notes. Preserve the existing app and approval request; never choose Unpublish or Cancel approval.
3. Preserve **Publish in Package Manager**, **Submit to Contest**, the dedicated `https://ideas.intersystems.com/ideas/DPI-I-689` field and the existing demo URL. Refresh the description from the verified README and save/send the new release for approval as the portal permits.
4. Read back the saved release and moderation status. Wait for the anonymous registry metadata/manifest to list 0.2.0; then follow the optional public-package check in [INSTALL.md](../INSTALL.md#optional-check-without-a-model). If approval is pending, record that blocker and do not claim a registry install passed.
5. Confirm SilentShift remains on [contest 49](https://openexchange.intersystems.com/contest/49). Organizer acceptance of the potential two-point IPM bonus is separate from package publication.

## Historical 0.1.0 evidence

The November 3 clean local archive installed 43 classes and nine assets, with 53 files / 75,003 bytes and SHA-256 `0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6`. Explicit setup then passed five final native routes, four of five expected model proposals and all four tool reads. [Historical receipt](evidence/ipm-clean-install.json). That local archive hash is not the public registry artifact hash.

For an existing namespace, `verify_ipm_native.py` remains a bounded **stopped-production** load/package check and compares all ten application/workflow table row counts. It leaves production stopped; its receipt is not a clean install or registry-install result. Never run it while intake or investigations are active.
