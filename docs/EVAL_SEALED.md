# Sealed v3: blocked before execution

Status recorded November 9, 2026 UTC. **No sealed result is available. The case file was not opened after generation, and no sealed arm was run.**

The 36 synthetic orders and their labels were committed first at `9c8d9376f08024eb7f5ff05771a5b02a854d6b4f`. Their scenarios.json SHA-256 is `415489ccebbe21b83ea870c862570eb6acc7bd1a59ea2394fa7f31cd27c962d6`. See [the frozen protocol](../fixtures/v3-sealed/FROZEN.md). No label or input was changed.

## Why execution stopped

The repaired candidate at `34c45a96c7493135aa0b9dfb7e91340ddfda2ee9` failed its live core gate after an earlier failed gate. Under the owner's two-failure rule, repair/model attempts stopped. Running the sealed comparison through a known failed provider path would measure that infrastructure failure rather than a meaningful prose-reading comparison. The sealed set is preserved for a corrected, verified source snapshot.

| Check | Observed result | Evidence |
| --- | --- | --- |
| Full Python suite | 317 passed in 21.54 seconds | [Exact output](evidence/prose-repair-pytest-output.txt) |
| Native %UnitTest suite | 6 classes / 15 methods passed, including the original suite | [Exact output](evidence/prose-repair-native-unit-output.txt) |
| Keyless replay, twice | 12/12 and 12/12 | [Receipts](evidence/prose-repair-keyless-replays.json) |
| Live core, prompt 1.4.1 | Failed: 4/5 routes; the approved amendment was held after malformed JSON | [Failed gate](evidence/prose-repair-live-gate-v141.json) |
| Live core, prompt 1.4.2 | Failed: 4/5 routes; 0/5 successful native agent/tool executions | [Failed gate](evidence/prose-repair-live-gate-v142.json) |
| Sealed rules-only, three repetitions | Not run | [Blocked status](evidence/prose-repair-status.json) |
| Sealed agent + policy, three repetitions | Not run | [Blocked status](evidence/prose-repair-status.json) |
| Full v2 dev rerun, after tuning | Not run | [Dev status](EVAL_DEV_AFTER_TUNING.md) |

There are no per-category accuracy numbers, wrong-delivery comparisons or case-time medians for v3. Do not substitute the selected development probes or historical v2 result for a sealed result.

## Next gate

Repair the invocation-scoped final-format integration under the real provider application's least-privilege role, then re-establish the live core gate before freezing an execution source. No broader permission was granted in this pass. Only after that gate is green should the committed runner open the case file:

```sh
# Replace VERIFIED_SOURCE_SHA only after the native live gate passes.
uv run python scripts/run_sealed.py --dataset sealed --execute --open-sealed \
  --source-commit VERIFIED_SOURCE_SHA --container VERIFIED_LIVE_CONTAINER \
  --output evidence/heldout/v3-sealed
```

The runner pins the original label commit, unchanged baseline, prompt, local model digest and source inventory; it performs three actual baseline runs and three fresh native agent + policy runs per order. It suppresses indexing evaluated outcomes without changing native retrieval or routing. Once sealed execution begins, do not tune against it or relabel cases.

Runtime actually used for the failed live gate: ARM64 IRIS 2026.3.0AI.154.0 / Build 154U. No other build, hosted demo, new publication or measured improvement is claimed.
