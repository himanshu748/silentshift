# Sealed v3 result

Measured on 2026-11-14T17:50:49.037472+00:00. Synthetic examples only; delivery is to the IRIS simulator. No accuracy claim about customer data or another build.

Source: `56ff2d6976e61ccb36b68e0632224e1234afaa3e`. Dataset SHA-256: `415489ccebbe21b83ea870c862570eb6acc7bd1a59ea2394fa7f31cd27c962d6`. Labels were committed at `9c8d9376f08024eb7f5ff05771a5b02a854d6b4f` before evaluation. Native runtime: `IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`; model `qwen3-silentshift:4b-instruct`; prompt `silentshift-investigator/1.4.2`.

36 distinct orders, three actual baseline executions and three fresh native agent + policy investigations per order. The repeated executions are not independent samples. Every attempt, including failed/model-invalid attempts, remains in the denominator. No label edits or selective retries.

The deterministic baseline is unchanged. Agent findings may add containment or review; they cannot release any baseline hold. Exact quotations establish provenance, not semantic entailment. Legitimate prose authorizations that require releasing a structured hold remain outside this experiment’s permitted authority.

## What this result supports

The agent’s measured contribution is **small and inconsistent**. Rules-only produced **24/36** correct routes in each trial; agent + policy produced **24/36, 24/36 and 25/36**. Wrong deliveries were **8/20** for rules and **8/20, 7/20 and 7/20** for agent + policy. Unstructured correct routing was **0/12** for rules and **0/12, 0/12 and 1/12** for agent + policy.

**Agent + policy does not beat rules-only on wrong deliveries in trial 1, or on correct routes in the unstructured split in trials 1 and 2.** Pooled over the repeated orders, it prevented two wrong simulator deliveries and gained one exact correct route. This is not convincing evidence of reliable prose understanding or a general accuracy improvement.

**The sealed safety result is worse than historical v2:** wrong simulator deliveries are **35–40% (7–8/20)** here versus **8.7–13.0% (2–3/23)** there. Pooled unstructured correctness is **1/36 (2.8%)** here versus **3/48 (6.3%)** there. Overall correct-route rates are mixed: **66.7%, 66.7%, 69.4%** here versus **68.8%, 68.8%, 62.5%** in v2. These are different synthetic sets and source/prompt snapshots; this is a descriptive comparison, not proof of a controlled regression. [Historical v2 report](EVAL_HELDOUT.md).

The one failed agent attempt, **V3-S-01 / trial 3**, is retained: `EVIDENCE_READ_INCOMPLETE`, with zero message reads and two precedent reads. The policy quarantined it, matching that case’s route label. A correct fail-closed route does not turn this into successful agent execution. There were **107 returned** and **1 failed** agent attempts; none was retried or removed.

## Execution and scope

Executed on **14 November 2026, 22:27:39–23:20:24 IST**, using the source already registered in [EXECUTION.md](../fixtures/v3-sealed/EXECUTION.md). The evaluated historical source manifest is **0.3.0**; **public native IPM 0.3.3 and main were not requalified by this experiment**. No module version, native source, prompt, model, policy or label changed. Ollama **0.31.1** used model digest `30edee6daf42d36a77e6bdd225b2be0098021122827523f13035751575a66d35`; policy was `silentshift-policy/1.2.0`.

The fresh isolated source load passed **6 native classes / 16 methods** and the live **5/5** core gate before sealed access. Setup initially encountered exhausted Docker address pools and the existing restricted Colima bind mount. Only the new test network and gateway configuration path were corrected; no model call or sealed attempt was rerun. The first report-generation command used a relative source path the reporter does not accept; supplying the absolute path fixed reporting only, without executing another case. [Setup receipt](../evidence/heldout/v3-sealed/setup/receipt.json) · [native output](../evidence/heldout/v3-sealed/setup/native-unit-output.txt) · [live gate](../evidence/heldout/v3-sealed/setup/native-five.json).

The registered run completed in **3164.154 seconds** including baseline and harness overhead. Its final audit found **0** evaluated outcomes in the precedent index, and unchanged native identity, runtime source inventory and model digest. [Completion audit](../evidence/heldout/v3-sealed/completion-audit.json) · [exact run output](../evidence/heldout/v3-sealed/execution-output.txt). No hosted-demo access, paid inference, new release or OEX/IPM change occurred.

## Results

| Arm / trial | Correct routes | Wrong deliveries | False holds | Review | Median investigation |
| --- | --- | --- | --- | --- | --- |
| rules-only, 1 | 24/36 | 8/20 | 4/16 | 4/36 (11.1%) | 0.102 ms |
| rules-only, 2 | 24/36 | 8/20 | 4/16 | 4/36 (11.1%) | 0.098 ms |
| rules-only, 3 | 24/36 | 8/20 | 4/16 | 4/36 (11.1%) | 0.101 ms |
| agent+policy, 1 | 24/36 | 8/20 | 4/16 | 4/36 (11.1%) | 25267.500 ms |
| agent+policy, 2 | 24/36 | 7/20 | 4/16 | 5/36 (13.9%) | 25518.500 ms |
| agent+policy, 3 | 25/36 | 7/20 | 4/16 | 5/36 (13.9%) | 25736.000 ms |

Baseline wrong deliveries are counterfactual ALLOW recommendations; policy wrong deliveries require an actual simulator receipt. Baseline timing covers only assessment + rule evaluation inside Embedded Python. Agent timing covers native investigation when recorded, not an equivalent scope or a latency-speedup comparison. Service wall times are separately retained. Missing times are not zero-filled.

## By category, pooled repetitions

| Arm | Category | Correct routes | Wrong deliveries | False holds | Review |
| --- | --- | --- | --- | --- | --- |
| rules-only | structured | 36/36 | 0/36 | — (no eligible cases) | 12/36 |
| rules-only | unstructured | 0/36 | 24/24 | 12/12 | 0/36 |
| rules-only | clean | 36/36 | — (no eligible cases) | 0/36 | 0/36 |
| agent+policy | structured | 36/36 | 0/36 | — (no eligible cases) | 12/36 |
| agent+policy | unstructured | 1/36 | 22/24 | 12/12 | 2/36 |
| agent+policy | clean | 36/36 | — (no eligible cases) | 0/36 | 0/36 |

Agent + policy has fewer observed wrong simulator deliveries than the baseline’s counterfactual releases.
Agent + policy has one more correct unstructured route across the pooled repetitions; this occurred only in trial 3 and did not replicate in trials 1 or 2.

## Categories in each trial

| Arm | Trial | Category | Correct routes | Wrong deliveries | False holds | Review |
| --- | --- | --- | --- | --- | --- | --- |
| rules-only | 1 | structured | 12/12 | 0/12 | — (no eligible cases) | 4/12 |
| rules-only | 1 | unstructured | 0/12 | 8/8 | 4/4 | 0/12 |
| rules-only | 1 | clean | 12/12 | — (no eligible cases) | 0/12 | 0/12 |
| rules-only | 2 | structured | 12/12 | 0/12 | — (no eligible cases) | 4/12 |
| rules-only | 2 | unstructured | 0/12 | 8/8 | 4/4 | 0/12 |
| rules-only | 2 | clean | 12/12 | — (no eligible cases) | 0/12 | 0/12 |
| rules-only | 3 | structured | 12/12 | 0/12 | — (no eligible cases) | 4/12 |
| rules-only | 3 | unstructured | 0/12 | 8/8 | 4/4 | 0/12 |
| rules-only | 3 | clean | 12/12 | — (no eligible cases) | 0/12 | 0/12 |
| agent+policy | 1 | structured | 12/12 | 0/12 | — (no eligible cases) | 4/12 |
| agent+policy | 1 | unstructured | 0/12 | 8/8 | 4/4 | 0/12 |
| agent+policy | 1 | clean | 12/12 | — (no eligible cases) | 0/12 | 0/12 |
| agent+policy | 2 | structured | 12/12 | 0/12 | — (no eligible cases) | 4/12 |
| agent+policy | 2 | unstructured | 0/12 | 7/8 | 4/4 | 1/12 |
| agent+policy | 2 | clean | 12/12 | — (no eligible cases) | 0/12 | 0/12 |
| agent+policy | 3 | structured | 12/12 | 0/12 | — (no eligible cases) | 4/12 |
| agent+policy | 3 | unstructured | 1/12 | 7/8 | 4/4 | 1/12 |
| agent+policy | 3 | clean | 12/12 | — (no eligible cases) | 0/12 | 0/12 |

## Every route failure

A/Q/R = ALLOW/QUARANTINE/REQUEST_REVIEW. Each row lists all failing repetitions, including cases where rules beat the agent.

| ID | Category | Truth | Rules errors (trial: route) | Agent + policy errors (trial: route) | Rules win in trial |
| --- | --- | --- | --- | --- | --- |
| V3-U-12 | unstructured | Q | 1: A, 2: A, 3: A | 1: A, 2: A, 3: A | — |
| V3-U-04 | unstructured | A | 1: Q, 2: Q, 3: Q | 1: Q, 2: Q, 3: Q | — |
| V3-U-11 | unstructured | R | 1: A, 2: A, 3: A | 1: A, 2: A, 3: A | — |
| V3-U-05 | unstructured | R | 1: A, 2: A, 3: A | 1: A, 2: A | — |
| V3-U-01 | unstructured | A | 1: Q, 2: Q, 3: Q | 1: Q, 2: Q, 3: Q | — |
| V3-U-07 | unstructured | A | 1: Q, 2: Q, 3: Q | 1: Q, 2: Q, 3: Q | — |
| V3-U-06 | unstructured | Q | 1: A, 2: A, 3: A | 1: A, 2: A, 3: A | — |
| V3-U-09 | unstructured | Q | 1: A, 2: A, 3: A | 1: A, 2: A, 3: A | — |
| V3-U-03 | unstructured | Q | 1: A, 2: A, 3: A | 1: A, 2: A, 3: A | — |
| V3-U-02 | unstructured | Q | 1: A, 2: A, 3: A | 1: A, 2: R, 3: A | — |
| V3-U-08 | unstructured | Q | 1: A, 2: A, 3: A | 1: A, 2: A, 3: A | — |
| V3-U-10 | unstructured | A | 1: Q, 2: Q, 3: Q | 1: Q, 2: Q, 3: Q | — |

## Failed or schema-invalid agent attempts

| ID | Trial | Agent status | Failure / schema errors |
| --- | --- | --- | --- |
| V3-S-01 | 3 | failed | EVIDENCE_READ_INCOMPLETE |

## Time per order

Milliseconds; three agent investigation times are retained separately. — means unavailable, not zero.

| ID | Rules median | Agent trials 1 / 2 / 3 | Agent median | Service wall time, trials 1 / 2 / 3 |
| --- | --- | --- | --- | --- |
| V3-U-12 | 0.109 | 22811.000 / 25979.000 / 25230.000 | 25230.000 | 23249.000 / 26369.000 / 25470.000 |
| V3-U-04 | 0.113 | 26539.000 / 39901.000 / 25090.000 | 26539.000 | 26906.000 / 40235.000 / 25551.000 |
| V3-S-08 | 0.098 | 23990.000 / 21576.000 / 25355.000 | 23990.000 | 24311.000 / 21923.000 / 25792.000 |
| V3-U-11 | 0.117 | 31467.000 / 29908.000 / 31267.000 | 31267.000 | 31657.000 / 30131.000 / 31465.000 |
| V3-S-12 | 0.086 | 40333.000 / 24035.000 / 21928.000 | 24035.000 | 40732.000 / 24358.000 / 22269.000 |
| V3-U-05 | 0.120 | 30747.000 / 36950.000 / 27856.000 | 30747.000 | 31084.000 / 38073.000 / 28170.000 |
| V3-S-01 | 0.097 | 23151.000 / 22131.000 / 26442.000 | 23151.000 | 23478.000 / 22449.000 / 26798.000 |
| V3-U-01 | 0.111 | 24859.000 / 23038.000 / 24721.000 | 24721.000 | 25193.000 / 23338.000 / 25046.000 |
| V3-C-08 | 0.115 | 22731.000 / 25695.000 / 26598.000 | 25695.000 | 22947.000 / 25893.000 / 26813.000 |
| V3-S-06 | 0.088 | 25044.000 / 24647.000 / 22910.000 | 24647.000 | 25367.000 / 25042.000 / 23235.000 |
| V3-S-10 | 0.104 | 24041.000 / 27099.000 / 24016.000 | 24041.000 | 24385.000 / 27492.000 / 24379.000 |
| V3-U-07 | 0.106 | 45624.000 / 26856.000 / 24495.000 | 26856.000 | 46025.000 / 27229.000 / 24830.000 |
| V3-S-09 | 0.086 | 46647.000 / 22424.000 / 25551.000 | 25551.000 | 49936.000 / 22769.000 / 25879.000 |
| V3-S-03 | 0.084 | 24292.000 / 23698.000 / 24000.000 | 24000.000 | 24740.000 / 24011.000 / 24379.000 |
| V3-U-06 | 0.097 | 27237.000 / 24112.000 / 26740.000 | 26740.000 | 27474.000 / 24344.000 / 26964.000 |
| V3-S-02 | 0.098 | 30150.000 / 23839.000 / 23802.000 | 23839.000 | 30461.000 / 24186.000 / 24161.000 |
| V3-C-06 | 0.101 | 24387.000 / 25468.000 / 25376.000 | 25376.000 | 24644.000 / 25659.000 / 25581.000 |
| V3-U-09 | 0.092 | 23584.000 / 26039.000 / 25786.000 | 25786.000 | 23807.000 / 26296.000 / 26003.000 |
| V3-C-11 | 0.099 | 23674.000 / 25691.000 / 25686.000 | 25686.000 | 23857.000 / 25891.000 / 25895.000 |
| V3-C-03 | 0.098 | 25491.000 / 31591.000 / 24018.000 | 25491.000 | 25724.000 / 31814.000 / 24218.000 |
| V3-C-02 | 0.105 | 26181.000 / 25569.000 / 25961.000 | 25961.000 | 26378.000 / 26066.000 / 26268.000 |
| V3-U-03 | 0.101 | 25495.000 / 32394.000 / 30128.000 | 30128.000 | 25754.000 / 32652.000 / 30325.000 |
| V3-S-04 | 0.102 | 30593.000 / 24994.000 / 22774.000 | 24994.000 | 30903.000 / 25580.000 / 23317.000 |
| V3-C-09 | 0.095 | 33132.000 / 26199.000 / 27803.000 | 27803.000 | 33519.000 / 26419.000 / 28028.000 |
| V3-C-10 | 0.098 | 28683.000 / 25441.000 / 28728.000 | 28683.000 | 28998.000 / 25653.000 / 29056.000 |
| V3-U-02 | 0.097 | 34937.000 / 23866.000 / 29093.000 | 29093.000 | 35167.000 / 24228.000 / 29349.000 |
| V3-S-05 | 0.100 | 23424.000 / 29894.000 / 24074.000 | 24074.000 | 23754.000 / 30312.000 / 24465.000 |
| V3-S-11 | 0.096 | 24784.000 / 30141.000 / 24160.000 | 24784.000 | 25090.000 / 30470.000 / 24537.000 |
| V3-C-05 | 0.101 | 27718.000 / 28830.000 / 29569.000 | 28830.000 | 27975.000 / 29072.000 / 29808.000 |
| V3-C-01 | 0.094 | 24390.000 / 22857.000 / 25460.000 | 24390.000 | 24593.000 / 23082.000 / 25674.000 |
| V3-C-07 | 0.094 | 23124.000 / 25623.000 / 27065.000 | 25623.000 | 23337.000 / 25842.000 / 27289.000 |
| V3-U-08 | 0.106 | 25601.000 / 24691.000 / 27573.000 | 25601.000 | 25799.000 / 24930.000 / 27793.000 |
| V3-S-07 | 0.099 | 22334.000 / 25185.000 / 32690.000 | 25185.000 | 22683.000 / 25524.000 / 33074.000 |
| V3-U-10 | 0.102 | 24985.000 / 22955.000 / 46703.000 | 24985.000 | 25295.000 / 23330.000 / 47446.000 |
| V3-C-04 | 0.111 | 24172.000 / 26082.000 / 34320.000 | 26082.000 | 24485.000 / 26283.000 / 34737.000 |
| V3-C-12 | 0.101 | 31482.000 / 24259.000 / 28916.000 | 28916.000 | 31705.000 / 24576.000 / 29119.000 |

## Reproduction and limits

Raw records, traces, per-case service timings, citation checks, complete metrics and native identity: [manifest](../evidence/heldout/v3-sealed/manifest.json), [summary](../evidence/heldout/v3-sealed/summary.json).

The operator-only evaluation host suppresses automatic indexing of evaluated outcomes. Contract/reference retrieval, the four tools, local inference, deterministic policy and simulator routing remain native. The precise production substitution is recorded in the manifest. Historical core fixtures may exist in the isolated instance; evaluated outcomes are not added to the precedent corpus.

This is an implementation-aware, seeded synthetic set. The generator author knew its families; it is not independently human-adjudicated or a production distribution. Model inference remains nondeterministic and quotation checks can accept a semantically mistaken interpretation. Results apply only to the named source, prompt, model and runtime.

## Historical blocked state

The earlier November 9 blocked candidates and failed core gates remain preserved in [the prior status receipt](evidence/prose-repair-status.json) and [provider recovery receipt](evidence/provider-grant-recovery.json). The completed run above supersedes the old “not run” status; it does not erase those failed attempts. No v2 dev rerun was performed in this task.
