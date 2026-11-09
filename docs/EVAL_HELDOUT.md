# Held-out comparison — incomplete, not a final result

**November 9, 2026 UTC: paused for host storage.** No claim of an agent advantage is made. The report generator refuses to score an incomplete run as the final comparison.

The 48 synthetic orders and their contractual labels were committed before any rule or model execution. They remain unchanged at SHA-256 `e02747e587495dd2587a3813277a15451c7715638d9ff9962186a09e8986ef55`. [Frozen protocol](../fixtures/v2-heldout/FROZEN.md) · [inputs and labels](../fixtures/v2-heldout/scenarios.json).

| Execution coverage | Retained observations | Status |
| --- | ---: | --- |
| Rules-only baseline | 48 / 48 | Complete inside native Embedded Python |
| Paired agent-only and shipped-policy trial 1 | 48 / 48 | Complete |
| Paired agent-only and shipped-policy trial 2 | 48 / 48 | Complete |
| Paired agent-only and shipped-policy trial 3 | 18 / 48 | Incomplete |

There are **114 / 144** persisted native investigations. [Coverage receipt](../evidence/heldout/coverage.json). Agent-only and agent + policy are paired views of each investigation, not independent model runs. All completed records remain available; no completed case was rerun. The missing 30 observations prevent the preregistered full three-trial comparison, per-category results, variance and final failure list from being reported here. Successful original demo checks and setup warmups are outside these denominators.

The retained instance uses **IRIS 2026.3.0AI.154.0 Community / 154U ARM64**, native source 0.3.0, local `qwen3-silentshift:4b-instruct`, and prompt `silentshift-investigator/1.3.1`. The benchmark's native investigator and provider code are the frozen release implementation. The later configurable-provider branch was not loaded into that instance. Native source staging hashes, model identity and infrastructure interruptions are recorded in the manifest.

The first infrastructure interruption combined a disk guard and out-of-memory kills when another IRIS verification instance was started inside the same 2 GiB VM. Other instances were stopped before resuming the same evaluation container. Subsequent disk guards retained progress at 109 and then 114 investigations. The two failed provider-test containers were removed only after exact owner approval and log preservation. macOS swap subsequently occupied 6 GiB, leaving approximately 1.4 GiB free at the final stop. The 1.8 GiB safety floor was never lowered. No label, inference budget, prompt or routing policy was changed to obtain a pass.

This run needs more host disk space before it can finish. Retain the existing container and output directory. Once the host has sufficient headroom, restore the same native instance and resume:

```sh
docker --context colima-silentshift start silentshift-bonus-load-heldout-nov9
docker --context colima-silentshift start silentshift-bonus-load-heldout-nov9-gateway
uv run python scripts/run_heldout.py --execute
uv run python scripts/report_heldout.py
```

The runner validates the frozen dataset and runtime identity and skips already-persisted cases. Do not create a new run over the same files or change the benchmark container's source. The generator replaces this incomplete note only after all 144 observations exist. A fresh replication must use a separate instance/output directory and the frozen release implementation, not silently substitute the unpublished provider branch.

[Manifest and interruption log](../evidence/heldout/manifest.json) · [native rule outputs](../evidence/heldout/rules-only.json) · [setup receipt](../evidence/heldout/setup.json) · [trial 1](../evidence/heldout/trial-1/) · [trial 2](../evidence/heldout/trial-2/) · [partial trial 3](../evidence/heldout/trial-3/).

README and listing wording remain unchanged pending the owner's review of the completed comparison. No accuracy, ranking, award or production-data claim follows from this partial synthetic run.
