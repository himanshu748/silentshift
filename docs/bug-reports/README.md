# Bug reports

The reproduced AI Hub generator defect was filed on November 5 as [issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17), under `himanshu748`. The published body was read back and matched the prepared report. Vendor acceptance and contest points remain unconfirmed. [Filing receipt](../evidence/ai-hub-bug-filed.json).

[Exact issue title, reproduction and compiler log](ai-hub-quoted-tool-name.md), verified on **2026.3.0AI.154.0 / 154U**. Do not file a duplicate. The other candidate remains unisolated and unfiled.

| Candidate | Evidence | Filing readiness |
| --- | --- | --- |
| [AI Hub generated dispatch for a quoted underscore method](ai-hub-quoted-tool-name.md) | Valid UDL parses; native generator emits an invalid unquoted call; camel-case control compiles. Reproduced locally on 154U without an LLM call | Filed as #17; vendor and organizer confirmation pending |
| [Historical callback signal 11](callback-signal11-candidate.md) | Five retained log entries and an application workaround in git history | Needs standalone reproduction and stack attribution; not a confirmed Embedded Python defect |

Excluded from bug claims: incorrect `%GetTypeOf` usage in application code, skipping the final iterator row, the documented HTTP stream setter behavior, provider-specific options requiring `extra_params`, short local model deadlines, and treating the `%UnitTest.Manager` return status as an assertion-pass result. These were application/API usage mistakes or unproven limitations. Ordinary HTTP 400 diagnostics are intentional failure tests, not vendor defects.
