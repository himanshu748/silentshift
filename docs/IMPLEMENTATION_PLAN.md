# Implementation gates

| Milestone | Dependencies | Acceptance / verification | Evidence / state |
|---|---|---|---|
| 0 Research | Official sources, local audit | Pin154 APIs/rules; inspect Docker, credentials, disk | Rules/native research complete; EAP login and runtime blocked |
| 1 Native foundation | Official image, runnable Docker | Compile classes; ingest through service/process/operation; SQL receipt and Visual Trace | Source implemented; native compilation/execution blocked |
| 2 Native AI Hub | M1, supported tool-capable model | Native evidence tools + structured proposal from a production case | Adapter/tools implemented; native run blocked |
| 3 Semantic safety | M1–2, pure engine | Five scenarios + adversarial/duplicate/stale tests; no unsafe deliveries | 111 local tests passed; actual native scenarios blocked |
| 4 Workbench | Real API contract | Functional seven routes, actual cases, scenario injection, reviews; browser desktop/mobile/keyboard/reduced motion | Seven views implemented; 20 disconnected browser checks passed; connected journey blocked |
| 5 Evaluation | Frozen fixtures, M3 | Actual rule-only/native/final metrics, denominators and nullable usage | Local 5/5 observed; native metrics null/denominator 0; capture API implemented/uncompiled |
| 6 Reliability | M3–4 | Auth, duplicate/restart, timeout/late result, malicious data, malformed proposal | Native failure paths gate release |
| 7 Polish | M4 | Inspect real browser, correct overflow, focus/contrast and empty/error states | Desktop/mobile screenshots inspected; keyboard/reduced motion pass in disconnected mode |
| 8 Release | Mandatory runtime gates passed | Clean setup; secret scan; public source; OEX and contest actual confirmations | Separate publication/submission status; no restricted images |

Commands: `uv run pytest`; `npm --prefix web run check`; `npm --prefix web run build`; `npm --prefix web run test:e2e`; `python scripts/verify_native.py`. Exact installation commands are maintained in README as they are implemented. A gate stays blocked until its observable result is captured.

Next priority is the native vertical slice. Source, the shared pure policy functions, setup and the real API client are ready for runtime integration. Acquire the official image and runnable Docker/Compose, compile and repair runtime-specific issues before making native claims. Optional bonuses follow all P0 gates.
