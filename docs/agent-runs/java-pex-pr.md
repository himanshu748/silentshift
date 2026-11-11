# Prepared PR — do not open without `submit`

**Base:** main
**Head:** feat/java-pex-nov11
**Title:** feat: export committed outcomes through Java PEX

SilentShift currently keeps routing evidence inside IRIS. This adds a Java PEX receipt-export operation called by Destination and Quarantine after their existing route commits. Each exported JSON binds the case, persisted outcome and evidence hashes, with an RSA/SHA-256 signature. Retries reuse the immutable original; later review outcomes append another record. Export failure preserves the original route.

The source candidate is native 0.3.2, unpublished. Public IPM/OEX stay 0.3.1 and do not include this feature. React stays 0.2.1. Compose compiles owned Java source against the preloaded build-154 SDK locally; IPM packages owned source/build assets, not vendor JARs or signing keys.

**Blocked:** the API verifier passed 5/5, but the explicit ObjectScript repeat passed 4/5 because the approved-amendment proposal omitted a required citation. Policy correctly held it; the assertion remains unchanged. Do not merge or publish this candidate as fully verified. Fresh archive install has not run.

Validation and scope are recorded in docs/evidence/bonus-claims-nov11/java-pex.json and docs/JAVA_PEX.md. The clean source Compose path runs keyless replay without a model; the separate clean source-loaded IPM instance runs live Ollama. No new build or architecture is claimed. Native gateway testing is local only; hosted CI cannot test the restricted EAP image.

- [x] Real native PEX request/response and signed receipt in a case session.
- [x] Native retry and stopped-exporter tests; no policy/fixture changes.
- [x] Keyless Compose replay and repeat replay.
- [x] Public-dependency JUnit tests; no restricted SDK download in CI.
- [ ] Hosted CI for this branch: requires the separately approved push/PR.
- [ ] Owner review and merge, then separately approved tag/release and OEX/IPM publication.
- [ ] Bonus follow-up only after published evidence links resolve anonymously.

No deployment, listing edit, release, comment or bonus award is part of this PR preparation.
