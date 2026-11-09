# Sealed v3 evaluation

Label-first commit: `9c8d9376f08024eb7f5ff05771a5b02a854d6b4f`. No case file has been opened after generation.

Generated once from seed `8172406782145921268` by `scripts/generate_sealed.py`.
Exact scenarios.json SHA-256: `415489ccebbe21b83ea870c862570eb6acc7bd1a59ea2394fa7f31cd27c962d6`.
Generator SHA-256: `17eead910dcc3e61b28196b62a1c5c7c3e8da7ab809bfe34eff61a8e8da9379c`.

36 synthetic orders: 12 structured, 12 unstructured, 12 clean, with new vendors and wording. Labels and one-line reasons derive from the stipulated contractual records, without importing or running any evaluated engine, baseline or model. The generator author knows its template families; this is not independent human blinding or customer validation.

## Access and freeze

After committing this directory, do not open the case file until the sealed execution phase. Do not use it for diagnosis, prompt selection or policy tuning. v2-heldout is now the dev set; preserve its original historical run and labels. Never edit a v3 input, category, label, reason, clock or order after generation. Disputed labels must be reported without relabelling.

## Preregistered scoring

Freeze the tuned source commit, prompt version and model identity before opening/running this set. Native target: 2026.3.0AI.154.0 / 154U ARM64, local Ollama qwen3-silentshift:4b-instruct only. Three executions of the unchanged deterministic baseline and three fresh native agent + policy investigations per case, in frozen order, trial-major. No selective model retries or output repair. Agent evidence may add a hold, but must never release a baseline rule hold. Do not copy labels, category or reasons into native/model inputs. Distinct case/trial namespaces isolate precedent history. No manual approvals or indexing of these outcomes as precedents.

Score exact ALLOW / QUARANTINE / REQUEST_REVIEW routes. Invalid, failed and timed-out attempts remain in denominators. Wrong deliveries mean a non-ALLOW truth released by a baseline counterfactual, or actually delivered to the simulator by the policy arm. False holds mean any non-ALLOW outcome on ALLOW truth. Report review rate, per-category and per-trial results, all failures with IDs, and measured per-case time. Separate baseline assessment time from agent/service time. Repeated orders are not independent samples. Run this set once as three preregistered repetitions, then report regardless of outcome; no further tuning against these results.
