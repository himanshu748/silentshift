# Bug-report drafts

Nothing in this directory was filed. Vendor acceptance and contest points remain unconfirmed.

Ready to file: [exact issue title, body and fresh compiler log](ai-hub-quoted-tool-name.md), reproduced again on **2026.3.0AI.154.0 / 154U**. Submit it to the [contest's dedicated AI Hub bug tracker](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/new). The other candidate remains unisolated.

| Candidate | Evidence | Filing readiness |
| --- | --- | --- |
| [AI Hub generated dispatch for a quoted underscore method](ai-hub-quoted-tool-name.md) | Valid UDL parses; native generator emits an invalid unquoted call; camel-case control compiles. Reproduced locally on 154U without an LLM call | Reproducible draft for the user to review and file |
| [Historical callback signal 11](callback-signal11-candidate.md) | Five retained log entries and an application workaround in git history | Needs standalone reproduction and stack attribution; not a confirmed Embedded Python defect |

Excluded from bug claims: incorrect `%GetTypeOf` usage in application code, skipping the final iterator row, the documented HTTP stream setter behavior, provider-specific options requiring `extra_params`, short local model deadlines, and treating the `%UnitTest.Manager` return status as an assertion-pass result. These were application/API usage mistakes or unproven limitations. Ordinary HTTP 400 diagnostics are intentional failure tests, not vendor defects.
