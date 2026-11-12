# Bug hunt findings, 12 Nov 2026

Runtime: `IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`, image `sha256:8fa0ae85777d…` (arm64), Embedded Python 3.12.3. Each probe ran in a fresh container that was removed afterwards.

## Where to file

- Embedded Python: https://github.com/intersystems-community/python-bugreports (template `bug_report.md`). Entrants in the bonus thread link issues there (Knos #30/#31, OcuTalon #32, Shutter #26/#27).
- AI Hub: https://github.com/intersystems-community/ai-hub-eap-bugreports (our #17). Earlier reports also went to `intersystems-community/ai-hub-eap`; I checked both for duplicates.

## Embedded Python

| Probe | Result | Verdict |
| --- | --- | --- |
| Skipped argument `Py(,"Z")` / `Py("X",)` | Python receives `None`; ObjectScript receives the default | **Bug. Draft in `ep-bug-1/`, reproduced 3/3** |
| `ByRef`/`Output` on a Python method | `ERROR #2607 … qualifier is not allowed` at compile | Documented error, but the rejected class stays installed and runnable (my first runtime TypeError came from calling it). **Bug 2. Draft in `ep-bug-2/`, reproduced 3/3** |
| Finite `Decimal` returned as `%Numeric` | `%SYS.Python` oref | Same family as #22 (NaN/Infinity). Unsupported types come back as orefs. Not filed: would pad #22 |
| `True`/`None` via `%DynamicObject._Set` / `_Push` | Stored as oref, so `%ToJSON()` throws `<METHOD NOT SUPPORTED>` | Same root cause as #28 (Python bools to ObjectScript args) and #17 (None). Not filed |
| Emoji / non-BMP round trip | Valid UTF-16 pair; Python `len` 3, back to Python intact | Correct |
| NUL in strings | Preserved both ways | Correct |
| 3,641,144-char return / 4,000,000-char return | Returns OK / `<MAXSTRING>` raised | Correct, documented string limit |
| `None` as `%String` / `%Integer` | `""` | Documented |
| `-0.0`, `0.1+0.2`, `1e100`, `-(2**62)` as numbers | Printed as expected for ObjectScript | Correct |
| dict / list / tuple / date / datetime returns | `%SYS.Python` oref | Documented (no auto-conversion) |
| `bytes` as `%String` | 3-character string | Documented ("Bytes and Strings") |
| Python `raise` | `<PYTHON EXCEPTION> 246 <class 'ValueError'>: boom` | Correct |
| `iris.system.Status.Error` returned as `%Status` | Proper error status | Correct |
| ObjectScript `$$$ThrowStatus` caught in Python | `RuntimeError: ERROR #5001: …` | Correct |
| `%SYS.Python.Import` + `args...` keyword call (docs example) | Matches docs | Correct |
| `iris.cls(...).OsMethod(b="Z")` | `takes no keyword arguments` | Documented: IRIS has no keyword arguments |
| `irispython` standalone without Callin | `IRIS_ACCESSDENIED` | Documented (enable `%Service_CallIn`) |

**Second EP bug: found (ep-bug-2), lower impact than bug 1.** Nothing else I could honestly file without duplicating #17, #22 or #28.

## AI Hub (keyless; local mock OpenAI-compatible server inside the container)

| Probe | Result | Verdict |
| --- | --- | --- |
| `%AI.Tool` schema: defaults, %Integer, %Numeric, %Double, %Boolean | Correct types; only args without defaults are `required` | Correct |
| `%DynamicArray` arg advertised as `items: {type: string}` | Narrower than the method accepts | This is the fix ai-hub-eap #20 (closed) asked for. Not a bug |
| Private / Internal / `%` members as tools | `ToolNotFound` | Correct |
| ClassMethod exposed as a tool | Advertised and runnable | Consistent with design |
| `"false"` (string) to `%Boolean` | Accepted, evaluates FALSE | Covered by #20 (schema not enforced) |
| Non-ASCII user prompt and reply (ASCII-escaped and raw UTF-8 JSON) | Exact code points both ways | Correct |
| Non-ASCII, quotes and backslashes in tool-call arguments | Exact | Correct |
| Malformed arguments JSON, unknown tool, tool raising `<DIVIDE>` | Error returned to the model as a tool message; loop ends cleanly | Correct (the error text includes the source line; a design choice, not a defect) |
| `"arguments": ""` for a no-argument tool | JSON parse error to the model | `""` is not valid JSON; OpenAI sends `"{}"`. Leniency request, not a bug |
| Assistant tool-call turn re-sent without `content` | Present | Already #16 |

**Second AI Hub bug: not found.**
