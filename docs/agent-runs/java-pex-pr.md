# Prepared PR — do not open without `submit`

**Base:** main
**Head:** feat/java-pex-nov11
**Title:** feat: export committed outcomes through Java PEX

SilentShift currently keeps routing evidence inside IRIS. This adds a Java PEX receipt-export operation called by Destination and Quarantine after their existing route commits. Each exported JSON binds the case, persisted outcome and evidence hashes, with an RSA/SHA-256 signature. Retries reuse the immutable original; later review outcomes append another record. Export failure preserves the original route.

The source candidate is native 0.3.2, unpublished. Public IPM/OEX stay 0.3.1 and do not include this feature. React stays 0.2.1. Compose compiles owned Java source against the preloaded build-154 SDK locally; IPM packages owned source/build assets, not vendor JARs or signing keys.

**Local blocking failure resolved:** pre-inference generation now retains the complete case citation manifest after four scoped reads. Three planned sets passed 15/15, followed by 5/5 on the final message-storage layout. All 20 Java receipts verified independently. Native 8/26, 394 pytest, TS/build and 54 disconnected browser checks passed. The actual regenerated 0.3.2 archive installed in a pristine offline container, left empty/stopped. Hosted branch CI is still unexecuted until the owner approves pushing. [Current evidence](../evidence/citation-fix-nov11/summary.json).

Validation and scope are recorded in docs/evidence/citation-fix-nov11/summary.json and docs/JAVA_PEX.md. The earlier clean source Compose path ran keyless replay without a model. This follow-up used the retained source-upgraded instance for live Ollama and a separate pristine offline instance for archive installation; it did not rerun the full keyless API example. No new build or architecture is claimed. Native gateway testing is local only; hosted CI cannot test the restricted EAP image.

- [x] Real native PEX request/response and signed receipt in a case session.
- [x] Native retry and stopped-exporter tests; no policy/fixture changes.
- [x] Keyless Compose replay and repeat replay.
- [x] Public-dependency JUnit tests; no restricted SDK download in CI.
- [ ] Hosted CI for this branch: requires the separately approved push/PR.
- [ ] Owner review and merge, then separately approved tag/release and OEX/IPM publication.
- [ ] Bonus follow-up only after published evidence links resolve anonymously.

No deployment, listing edit, release, comment or bonus award is part of this PR preparation.
