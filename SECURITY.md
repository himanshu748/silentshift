# Security model

SilentShift is a single-tenant contest demonstrator using synthetic business data. The EAP runtime is not approved here for production. Native compilation, permission and restart testing are release gates, not inferred guarantees.

## Authority boundaries

- A partner supplies a message, never reference authority, scenario clocks, model output or reviewer identity.
- The server retrieves reference records from a separately seeded catalog, scopes synthetic scenarios server-side and retains a case snapshot. Effective dates and amendment lineage matter.
- A native AI Hub agent reads only its server-bound case through three bounded tools. No shell, arbitrary SQL, remote URL fetch, mutation or model-selected case ID is exposed. Notes and retrieved text cannot grant authority.
- Strict parsing rejects extra recommendation fields, duplicate JSON keys, unsupported actions, nonfinite values and unknown evidence. Policy independently checks critical findings, active approved evidence, citation coverage, uncertainty and duplicate effects.
- Quarantine and destination operations check saved policy. The model cannot call either. The included destination is an IRIS-persisted simulator; no external atomic-delivery guarantee is made.
- Viewer and reviewer IRIS resources are separate. Reviews require server identity, a reason, expected version and idempotency key. Critical contradictions cannot be bypassed by manual approval.

## Credentials and exposure

Use external `.env`/secret files with restrictive permissions; `.env.example` contains placeholders only. Never put provider keys into screenshots, fixtures, URLs, source, CI output or browser local storage. The frontend holds login credentials only in memory and clears them on sign-out. Basic authentication requires TLS outside loopback. Loopback bindings are deliberate; do not expose IRIS administration or Vite to the Internet.

No paid calls are authorized merely because credentials exist. Native verification requires an explicit model-call flag and runs five investigations. Keep model iterations/tokens and operation waits bounded. A business timeout does not prove provider-side cancellation; late responses have no routing authority and need runtime verification.

## Data and retention

Store synthetic payloads, reference snapshots, native response, decision and audit history for reproducibility. Do not import customer/financial/personal data for this contest build. Provider errors are reduced to stable stages/codes. Audit events must not contain credentials. Database access is sensitive even when the model tools are read-only. No general delete API is provided; retention/backup lifecycle is not production-ready.

## Reporting

Do not disclose live keys or restricted EAP binaries in an issue. Until a public security contact exists, report privately to the repository owner using the hosting platform's private vulnerability channel if enabled. Publication of source does not license proprietary IRIS runtime redistribution.
