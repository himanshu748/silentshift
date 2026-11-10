# Frozen held-out protocol

- Label-first commit: `a50a551a92b5f52ba5212a91dca3de0d21f57da5`.
- Exact `scenarios.json` SHA-256: `e02747e587495dd2587a3813277a15451c7715638d9ff9962186a09e8986ef55`.
- Baseline/policy source SHA-256: `63f4d212793e4c6b6ad65374c5302cc863561e4d01607f566f580e2984f151de` (`python/silentshift/engine.py`, unchanged from public 0.3.0 source).
- Investigator source SHA-256: `322fba9f86b555243334951276f1be858ff687922fa1cf5db30d1073d80f0d73`.
- Native target only: IRIS 2026.3.0AI.154.0 Community / 154U ARM64.
- Released local model: `qwen3-silentshift:4b-instruct`; prompt `silentshift-investigator/1.3.1`. No prompt, rules, model, inference-budget or policy tuning is allowed after labels freeze.

## Preregistered execution and scoring

All 48 cases are retained: 16 structured, 16 unstructured, 16 clean. Run the unchanged deterministic `assess` + `rule_only` inside IRIS Embedded Python once per case. Run three fresh native investigations per case. Both agent arms use the same three paired model draws: agent-only is the raw final AI Hub recommendation, and agent + policy is that investigation's actually persisted shipped route. This gives three trials per agent arm without inventing six independent model runs or dispatching an agent-only delivery. The agent sees the released candidate assessment and four released evidence tools; agent-only is not an assessment-free LLM. The runner must never pass category, ground truth or reasons to IRIS/model input.

Use a fresh evaluation instance without application source mounts. Copy frozen message/reference payloads and test-only evaluation code as operator input; do not change any shipped application class. Assign a distinct synthetic scenario scope per case/trial to isolate retrieved same-contract history. Keep reference IDs, message semantics, fixed clock and approved texts identical across arms; vary only event/correlation identity for fresh native investigations. Process in the committed shuffled order, trial-major. Do not seed these outcomes as precedent vectors or apply manual review.

Correct routes use exact three-way labels: ALLOW, QUARANTINE, REQUEST_REVIEW. Missing/unparseable agent decisions count as INVALID and incorrect, with all cases kept in denominators. A valid decision token in otherwise schema-invalid JSON remains the raw agent-only choice; malformed-output counts are also reported. Agent-only ALLOW on non-ALLOW truth is a **counterfactual wrong-delivery recommendation**, not an executed delivery. Agent + policy wrong deliveries require an actual simulator receipt on a non-ALLOW truth. Also disclose any final ALLOW without a receipt as a route/effect discrepancy.

False holds: any non-ALLOW prediction on ALLOW truth. Review rate: REQUEST_REVIEW / all cases; invalids are not silently counted as review. Report correct/N, wrong deliveries, false holds and review rate overall and by category for each trial, plus pooled counts/rates and per-case variation. List every failed case with frozen scenario ID and actual native case/session ID, including cases where rules win. Use median measured native agent investigation duration for both paired agent arms; also report native service end-to-end elapsed time. The rule-only timer includes assessment + baseline function execution inside Embedded Python, excluding shell/session overhead. These are different timing scopes and not a production latency benchmark.

Timeouts or failed inference remain observed failures; never retry selectively to improve scores. On transport/runtime failure, preserve the incomplete attempt, inspect persisted state and stop for a harness repair if needed; do not drop unsuccessful cases. Resume without rerunning an already persisted investigation. Do not rewrite any fixture, label or reason. Disputed labels, supported-schema limitations, prompt/assessment anchoring and synthetic provenance assumptions are reported explicitly.

If agent + policy does not beat rules-only on wrong deliveries or on correct routes in the unstructured split, state that explicitly. No README, main push, IPM publication or OEX change is authorized in this task. Files over 50 MB stay outside Git.
