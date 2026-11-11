# SilentShift 0.3.2 — prepared release text

**Not published.** The citation failure is resolved by separately recorded local checks and a clean offline archive install. Hosted CI and all publication approvals remain pending. Target the separately reviewed merge commit, never an assumed SHA or an existing version tag.

SilentShift now exports committed routing outcomes through a Java PEX Business Operation in the native IRIS production. Each receipt binds the case, outcome and evidence hashes, with an RSA/SHA-256 signature and immutable publication. Retries reuse the original receipt; a later review outcome appends another record. Export failure leaves the deterministic routing result unchanged.

The local Compose path builds the Java operation against the operator's build-154 SDK. The native IPM package includes owned Java source and its build script; explicit setup compiles it. Vendor SDKs, EAP images and signing keys are not distributed. Public 0.3.1 does not include this integration. React remains a separate 0.2.1 source build.

Qualified only on IRIS Community AI Hub 2026.3.0AI.154.0 / 154U ARM64. Synthetic cases and simulator-only delivery remain the evaluation boundary. See docs/JAVA_PEX.md and its execution receipts for verification and limits; no bonus award or hosted demo is asserted.
