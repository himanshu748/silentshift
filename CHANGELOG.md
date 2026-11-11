# Changelog

## 0.3.2 — prepared Java PEX candidate, not published

- Add a Java PEX `ReceiptExporter` Business Operation invoked by Destination and Quarantine after their existing routing commits. Native request/response bodies keep the export in the case's Visual Trace session.
- Sign bounded outcome/evidence receipts with a per-instance RSA-2048 key. Atomic publication refuses replacement; repeated outcomes reuse the original receipt, and later review decisions append another record.
- Bind the local final-generation citation manifest to the current case assessment after all four evidence reads. This prevents omitted predecessor IDs without editing responses or weakening policy. Keep the system prompt unchanged and record a separate format version in append-compatible message storage.
- Preserve routing when export fails or times out. Signing establishes receipt integrity under an operator-held key, not correctness of the business decision or a tamper-proof host.
- Build the owned Java JAR locally against build 154's shipped Java 11/PEX SDK. IPM includes the owned Java sources/build script, never vendor JARs, EAP images or signing keys. Explicit native setup compiles those assets; package activation still starts no production or model.
- Retain the keyless Compose launcher, separate React 0.2.1 workbench and unchanged policy/fixture bytes. Add JUnit and real native gateway, retry and outage checks. See [scoped Java verification](docs/JAVA_PEX.md).

Public IPM/OEX remain **0.3.1** until separately approved publication. This source manifest and Python project declare **0.3.2**; no v0.3.2 tag, registry package or OEX release was created by this preparation.

## 0.3.1 — published; original preparation notes retained

- **Provider configuration:** inherits the unpublished `push/top3` provider selection and internal gateway. Only local Ollama is live-qualified; OpenAI, Gemini, OpenRouter and compatible endpoints retain configuration/protocol-test scope. Keyless replay remains separate from inference.
- **Cited prose evidence:** inherits case-scoped prose projection, required invocation-scoped evidence reads and validated exact-quote findings. A cited finding can add containment; it cannot release an existing rule hold. The held-out results retain their limitations; the sealed benchmark is unfinished and no accuracy gain is asserted.
- **Native diagnostics:** privacy-safe host Event Log codes/stage traces, bounded redacted setup errors and compact internal acknowledgments. The full Partner response remains available. XData preserves the branch's prompt bytes; shared evidence/model/import/catalog helpers and compiler-exported build-154 Storage improve maintainability without rewriting the frozen routing engine.
- **Operator configuration:** bounded host settings and a single CSV parse retain original authority data. The native CSV backend was already included in public 0.3.0.
- **Source workbench and installation:** the multi-page frontend, source-only demo gateway and one-command isolated Compose judge path are repository deliverables. The frontend remains version 0.2.1 and is not installed by IPM. Compose keeps source read-only and writes frontend dependencies into a dedicated volume; no model or hosted demo is needed for its recorded replay.
- **Verification:** full-history CI checkout preserves the historical policy assertion; exact prompt-version and connected-setup fixes retain every check. Safe lint fixes and an explicit remaining-finding inventory replace a blanket clean-lint claim. Frozen fixtures and replay records are unchanged.

**At that preparation checkpoint**, `module.xml` and the Python project declared **0.3.1**. Public native IPM and OEX remain **0.3.0**. Candidate preparation is not publication: clean IPM load, published-registry installation, merge, tag/release and OEX moderation are distinct gates. See [current scoped verification](docs/JUDGE_VERIFICATION.md) before publishing. No package, tag or release was published in this pass.

## 0.3.0 — published November 8, 2026

Compared with the public 0.2.0 source snapshot `d3637bbe85812035e6258320c81af93305e95560`:

- **Bounded CSV intake** (`09f71b7`): accept order lines and an independently approved reference export through the native production, with explicit importer permission, bounded input validation and retained source evidence.
- **CSV workbench** (`ab00ecc`, `df59142`): preview the comparison, approve the source explicitly, investigate each line, recover interrupted imports and reopen persisted results without redispatch.
- **Interactive landing/workbench** (`770baab`): demonstrate the unsupported-unit hold and approved-amendment release, with case navigation, keyboard access and reduced-motion behavior.
- **Image optimization** (`fbd3947`): reduce repository image payloads.
- **Source bootstrap repair** (`e61a961`): compile the checked-in source directory instead of unrelated diagnostic classes retained in an existing namespace.
- **Release harness**: read the candidate manifest version when staging, packaging and checking receipts instead of reporting the old published identity.
- **Documentation**: consolidate installation in `INSTALL.md`, retain historical failures and verification boundaries, and distinguish recorded replay from fresh local inference.

The native IPM archive owns the backend classes and runtime assets. The React UI, optimized documentation images and source-bootstrap script are repository deliverables; they are not web assets installed by IPM. Pair the native package with the matching repository workbench. The [exact post-package commit inventory](docs/SUBMISSION_CHECKLIST.md#published-vs-main) includes documentation and evidence changes as well as runtime changes.

No routing policy, agent behavior or native execution semantics changed during candidate preparation. All examples remain synthetic; delivery remains per line to an IRIS simulator. There is no hosted demo or verified external ERP/X12 integration. Organizer qualification and awards remain unconfirmed.

**Publication verified:** the [fresh public 0.3.0 install](docs/evidence/ship-030-registry.json) passed startup, all native tests and two recorded replays. The [source archive](docs/evidence/ship-030-source-archive.json) matches published source snapshot `a7aa217f1fc8d96f56bac6fd3110618eec21c353`. Full live/browser candidate results retain their separate scope in [judge verification](docs/JUDGE_VERIFICATION.md). Description moderation and organizer qualification remain separate external gates; no Git tag was created.
