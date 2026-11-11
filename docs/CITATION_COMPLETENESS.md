# Keeping the required citation manifest intact

The approved-amendment failure was an output-format error: the agent received both contract versions, proposed ALLOW, but cited only the amendment. The unchanged `EVIDENCE_COMPLETE` policy check required both records and correctly returned REVIEW. The [failed run remains preserved](evidence/bonus-claims-nov11/java-pex-objectscript-repeat.json).

## What changed

The local Ollama relay now builds the final answer's JSON schema from the **persisted assessment for the bound case**. Its `evidence_ids` property is an exact-array `const`, so generation cannot drop the predecessor, substitute a historical case's ID or add an unknown ID. This happens only after the current invocation has completed all four evidence reads. Tool-selection rounds, keyless recorded replay and other providers retain their existing behavior.

This is constrained generation, **not a repaired answer**. The relay does not append IDs to a returned recommendation, force ALLOW, change uncertainty or manufacture a quote. The model still chooses its proposal and findings, and deterministic policy still checks completeness, contradictions, authority, uncertainty and exact-quote grounding. Unit tests explicitly prove that incomplete/foreign citations still deny release and complete citations never release a critical contradiction.

The required ID list is a manifest of supplied records, not a relevance ranking or proof that the model reasoned correctly about every record. Four observed tool reads also do not establish that reasoning. This fix addresses the omitted-manifest false hold; it does not establish improved held-out accuracy or change the earlier benchmark conclusions.

[Ollama structured-output API](https://github.com/ollama/ollama/blob/main/docs/api.md) describes schema-constrained generation; compatibility with the installed local model was separately observed in the saved probe.

## Version and traceability

- System prompt bytes and version remain `silentshift-investigator/1.4.2`.
- Applied local format is separately versioned as `silentshift-local-final/2`, recorded in agent metadata and each shaped native provider request.
- The new persistent metadata field is appended after every released message slot. `StructuredFinal` stays in slot 19; format version uses slot 20. A regression test checks the released layout, and a native round trip checks both fields after saving/reopening a message.
- No Embedded Python callback, extra database privilege, retry or response repair was added. Local Ollama is the qualified provider; this does not qualify new providers or builds.

[Format and schema](../src/SilentShift/AI/Investigator.cls) · [case/invocation binding](../src/SilentShift/Provider/Lease.cls) · [native regressions](../tests/iris/CitedFindingsChecks.cls) · [message storage](../src/SilentShift/Provider/CallRequest.cls).

## Observed verification

On the retained source-upgraded **154U ARM64** instance, the three predeclared complete sets passed **5/5 + 5/5 + 5/5** through API / ObjectScript / API, without resetting history. A final serialization-layout run passed another **5/5**. All **20** persisted Java receipts passed independent OpenSSL verification. The **15** API records retain raw, unrepaired recommendation arrays matching their assessments; the ObjectScript set has its separate native assertions.

The full native suite passed **8 classes / 26 methods**, Python **394**, TypeScript/build and **54** disconnected browser checks. Earlier connected/CSV/review/JUnit receipts keep their earlier scope; they are not relabeled as new runs. Hosted branch CI still requires the separately approved push.

The regenerated **0.3.2** archive installed in a second pristine, offline container with **no source mounts**. Its checks passed **5** deterministic cases, **10** invalid-path rejections and **4** Python origin checks; all **10** application tables remained empty and production stayed stopped. This is a real local-filesystem archive install, not a fresh archive live-model run or a public registry installation.

[Summary](evidence/citation-fix-nov11/summary.json) · [all repeat results](evidence/citation-fix-nov11/repeat-gate.json) · [final source run](evidence/citation-fix-nov11/final-native-five.json) · [archive install](evidence/citation-fix-nov11/archive-install.json) · [unchanged policy/fixtures](evidence/citation-fix-nov11/policy-identity.json) · [commands/output](evidence/citation-fix-nov11/outputs.txt).

**Historical state at this citation checkpoint:** 0.3.2 was unpublished and public 0.3.1 lacked these changes. The later receipt-mode fix was merged and [0.3.2 published](evidence/ipm-032-publication-nov11/publication.json); [its final tagged archive](evidence/ipm-032-final-nov11/summary.json) passed a separate fresh offline install. Those later steps do not renew this checkpoint’s live model results or imply organizer qualification.
