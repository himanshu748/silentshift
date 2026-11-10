# Held-out synthetic comparison

Generated **2026-11-09T10:54:50.213354+00:00** from the completed [run manifest](../evidence/heldout/manifest.json).

## Result

Agent + policy has fewer wrong deliveries on this synthetic set: rules-only recommends release for 6 bad orders; shipped policy has 2.66667 actual wrong simulator deliveries per trial on average. The baseline effect is counterfactual; only the shipped arm executes simulator delivery.

**Agent + policy does not beat rules-only on correct routes in the unstructured split:** baseline 1/16; shipped policy averages 1/16 across three trials.

## Frozen inputs and execution

Labels were committed first at `a50a551a92b5f52ba5212a91dca3de0d21f57da5`; exact input SHA-256: `e02747e587495dd2587a3813277a15451c7715638d9ff9962186a09e8986ef55`. No label, reason, category, clock or input was edited after execution. [Frozen protocol](../fixtures/v2-heldout/FROZEN.md) · [dataset](../fixtures/v2-heldout/scenarios.json).

There are **48 synthetic orders**: **16 structured, 16 unstructured, 16 clean**. Unstructured examples include signed prose amendments, buyer PO notes, verified superseding emails, text-only conversion clauses and conflicting references. Synthetic approved-source provenance is stipulated; the application did not authenticate an email sender.

The native target is **2026.3.0AI.154.0 Community / 154U ARM64**, source-loaded native **0.3.0**, local `qwen3-silentshift:4b-instruct`, prompt `silentshift-investigator/1.3.1`. Rules, policy and the investigator/provider implementation in this evaluation container are unchanged. Configurable-provider work was subsequently committed on `push/top3`, but was not loaded into this retained evaluation instance. No paid provider, other build, README change, IPM publication or OEX edit occurred. The operator-only evaluation harness is excluded from module.xml.

The unchanged baseline executed once per case **inside IRIS Embedded Python**. The **144 native investigations** are three fresh trials of every case, in the frozen shuffled order. Agent-only and agent + policy are **paired projections of the same three model draws**, not six independent runs. Agent-only reads the raw final response, including attempted output retained when tool verification fails; it sees the released candidate assessment and tools. The shipped arm uses persisted routing and simulator receipt counts. Distinct synthetic scenario scopes isolate same-contract history; held-out results were not indexed as precedent vectors.

Correct routes require the exact three-way label. A non-ALLOW truth released by the baseline/raw agent is a **counterfactual wrong-delivery choice**; the shipped arm requires an **actual local simulator receipt**. False holds include quarantine, review or invalid decisions on ALLOW truth. Invalids stay in all denominators and are not silently counted as review. A valid decision token in otherwise schema-invalid JSON remains the raw agent choice; policy may reject its schema independently.

## Overall results

Pooled agent denominators repeat the same 48 cases three times; they are **not 144 independent orders**. Wrong-delivery and false-hold denominators are respectively non-ALLOW and ALLOW truth counts.

| Arm | Correct routes | Wrong deliveries / bad orders | False holds / eligible | Review rate | Invalid | Median time (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rules-only | 33/48 | 6/23 | 9/25 | 6/48 (12.5%) | 0 | 0.108 |
| agent-only | 100/144 | 20/69 | 23/75 | 0/144 (0.0%) | 5 | 22416.000 |
| agent+policy | 96/144 | 8/69 | 30/75 | 31/144 (21.5%) | 0 | 22416.000 |

Baseline timing covers only assessment + rule selection inside Embedded Python. Agent timing covers the native investigator operation and is shared by both paired arms; it excludes other service stages. These timing scopes differ and do not establish an end-to-end speedup.
Agent investigation timing is available for **141 / 144** attempts. Missing durations remain null and are excluded from that median, never filled with zero. Failed attempts remain in routing-result denominators; the service timing below includes every available service duration.

## Three-trial variance

| Arm / trial | Correct routes | Wrong deliveries / bad orders | False holds / eligible | Review rate | Invalid | Median investigation (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| agent-only / 1 | 35/48 | 6/23 | 7/25 | 0/48 (0.0%) | 0 | 19245.500 |
| agent-only / 2 | 34/48 | 7/23 | 7/25 | 0/48 (0.0%) | 0 | 22304.500 |
| agent-only / 3 | 31/48 | 7/23 | 9/25 | 0/48 (0.0%) | 5 | 33892.000 |
| agent+policy / 1 | 33/48 | 2/23 | 9/25 | 10/48 (20.8%) | 0 | 19245.500 |
| agent+policy / 2 | 33/48 | 3/23 | 9/25 | 9/48 (18.8%) | 0 | 22304.500 |
| agent+policy / 3 | 30/48 | 3/23 | 12/25 | 12/48 (25.0%) | 0 | 33892.000 |

agent-only: correct-count population SD **1.700** across three trials; **10 / 48** cases changed their predicted route. Three trials are too few for a reliable statistical superiority claim.

agent+policy: correct-count population SD **1.414** across three trials; **4 / 48** cases changed their predicted route. Three trials are too few for a reliable statistical superiority claim.

Native service end-to-end median: **22702.500 ms**, across **144** timed investigations. The raw JSON also records harness wall time separately. Per-case three-trial median investigation times and prediction sequences are in [summary.json](../evidence/heldout/summary.json).

## Category results

| Arm / category | Correct routes | Wrong deliveries / bad orders | False holds / eligible | Review rate | Invalid | Median time (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rules-only / structured | 16/16 | 0/16 | 0/0 | 4/16 (25.0%) | 0 | 0.111 |
| rules-only / unstructured | 1/16 | 6/7 | 9/9 | 2/16 (12.5%) | 0 | 0.110 |
| rules-only / clean | 16/16 | 0/0 | 0/16 | 0/16 (0.0%) | 0 | 0.105 |
| agent-only / structured | 36/48 | 12/48 | 0/0 | 0/48 (0.0%) | 0 | 20858.500 |
| agent-only / unstructured | 19/48 | 8/21 | 20/27 | 0/48 (0.0%) | 2 | 23059.000 |
| agent-only / clean | 45/48 | 0/0 | 3/48 | 0/48 (0.0%) | 3 | 22686.000 |
| agent+policy / structured | 48/48 | 0/48 | 0/0 | 12/48 (25.0%) | 0 | 20858.500 |
| agent+policy / unstructured | 3/48 | 8/21 | 27/27 | 16/48 (33.3%) | 0 | 23059.000 |
| agent+policy / clean | 45/48 | 0/0 | 3/48 | 3/48 (6.2%) | 0 | 22686.000 |

Per-trial split correct routes (every other split metric is retained in summary.json):

| Arm / trial | Structured | Unstructured | Clean |
| --- | ---: | ---: | ---: |
| agent-only / 1 | 12/16 | 7/16 | 16/16 |
| agent-only / 2 | 12/16 | 6/16 | 16/16 |
| agent-only / 3 | 12/16 | 6/16 | 13/16 |
| agent+policy / 1 | 16/16 | 1/16 | 16/16 |
| agent+policy / 2 | 16/16 | 1/16 | 16/16 |
| agent+policy / 3 | 16/16 | 1/16 | 13/16 |

## Every failure

No failures are omitted. `HO-*` identifies the frozen scenario; UUID/session identify the actual native case/Visual Trace. Rule-only evaluations do not create business cases. Frozen one-line contractual reasons are in the dataset. `Rules win` marks a correct baseline and incorrect agent arm.

### rules-only

**15 failures.**

| Scenario | Category | Trial | Truth | Observed | Native case / session | Rules win |
| --- | --- | ---: | --- | --- | --- | --- |
| HO-001 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-006 | unstructured | — | ALLOW | REQUEST_REVIEW | not applicable: baseline function | — |
| HO-010 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-013 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-015 | unstructured | — | QUARANTINE | ALLOW | not applicable: baseline function | — |
| HO-016 | unstructured | — | REQUEST_REVIEW | ALLOW | not applicable: baseline function | — |
| HO-017 | unstructured | — | QUARANTINE | ALLOW | not applicable: baseline function | — |
| HO-020 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-027 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-029 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-030 | unstructured | — | QUARANTINE | ALLOW | not applicable: baseline function | — |
| HO-038 | unstructured | — | REQUEST_REVIEW | ALLOW | not applicable: baseline function | — |
| HO-041 | unstructured | — | ALLOW | QUARANTINE | not applicable: baseline function | — |
| HO-045 | unstructured | — | QUARANTINE | ALLOW | not applicable: baseline function | — |
| HO-046 | unstructured | — | ALLOW | REQUEST_REVIEW | not applicable: baseline function | — |

### agent-only

**44 failures.**

| Scenario | Category | Trial | Truth | Observed | Native case / session | Rules win |
| --- | --- | ---: | --- | --- | --- | --- |
| HO-001 | unstructured | 1 | ALLOW | QUARANTINE | 419BD47A-DC05-11F1-A103-A90DC9E483ED / 169 | — |
| HO-007 | structured | 1 | REQUEST_REVIEW | ALLOW | 9098B818-DC05-11F1-A103-A90DC9E483ED / 334 | yes |
| HO-008 | structured | 1 | REQUEST_REVIEW | ALLOW | 9E3C1698-DC05-11F1-A103-A90DC9E483ED / 362 | yes |
| HO-010 | unstructured | 1 | ALLOW | QUARANTINE | B9361C84-DC05-11F1-A103-A90DC9E483ED / 417 | — |
| HO-013 | unstructured | 1 | ALLOW | QUARANTINE | E38CE5ED-DC05-11F1-A103-A90DC9E483ED / 500 | — |
| HO-016 | unstructured | 1 | REQUEST_REVIEW | ALLOW | 0CBE95FF-DC06-11F1-A103-A90DC9E483ED / 584 | — |
| HO-023 | structured | 1 | REQUEST_REVIEW | ALLOW | 63107EE5-DC06-11F1-A103-A90DC9E483ED / 776 | yes |
| HO-027 | unstructured | 1 | ALLOW | QUARANTINE | 8EEF71DF-DC06-11F1-A103-A90DC9E483ED / 886 | — |
| HO-029 | unstructured | 1 | ALLOW | QUARANTINE | A6029EE3-DC06-11F1-A103-A90DC9E483ED / 942 | — |
| HO-036 | structured | 1 | REQUEST_REVIEW | ALLOW | F5208C9C-DC06-11F1-A103-A90DC9E483ED / 1134 | yes |
| HO-038 | unstructured | 1 | REQUEST_REVIEW | ALLOW | 0BD31164-DC07-11F1-A103-A90DC9E483ED / 1190 | — |
| HO-041 | unstructured | 1 | ALLOW | QUARANTINE | 2EC60671-DC07-11F1-A103-A90DC9E483ED / 1272 | — |
| HO-046 | unstructured | 1 | ALLOW | QUARANTINE | 696EF1CB-DC07-11F1-A103-A90DC9E483ED / 1411 | — |
| HO-006 | unstructured | 2 | ALLOW | QUARANTINE | E6C2A20F-DC07-11F1-A103-A90DC9E483ED / 1632 | — |
| HO-007 | structured | 2 | REQUEST_REVIEW | ALLOW | F8DAB526-DC07-11F1-A103-A90DC9E483ED / 1660 | yes |
| HO-008 | structured | 2 | REQUEST_REVIEW | ALLOW | 07229FB7-DC08-11F1-A103-A90DC9E483ED / 1688 | yes |
| HO-010 | unstructured | 2 | ALLOW | QUARANTINE | 23E1B43E-DC08-11F1-A103-A90DC9E483ED / 1743 | — |
| HO-015 | unstructured | 2 | QUARANTINE | ALLOW | 730337E4-DC08-11F1-A103-A90DC9E483ED / 1882 | — |
| HO-016 | unstructured | 2 | REQUEST_REVIEW | ALLOW | 89539426-DC08-11F1-A103-A90DC9E483ED / 1909 | — |
| HO-020 | unstructured | 2 | ALLOW | QUARANTINE | 2C52D7EC-DC0A-11F1-A405-EED9F2289F9B / 2020 | — |
| HO-023 | structured | 2 | REQUEST_REVIEW | ALLOW | 5684A08E-DC0A-11F1-A405-EED9F2289F9B / 2102 | yes |
| HO-027 | unstructured | 2 | ALLOW | QUARANTINE | 88150365-DC0A-11F1-A405-EED9F2289F9B / 2212 | — |
| HO-029 | unstructured | 2 | ALLOW | QUARANTINE | A0231CEA-DC0A-11F1-A405-EED9F2289F9B / 2268 | — |
| HO-036 | structured | 2 | REQUEST_REVIEW | ALLOW | FA77D061-DC0A-11F1-A405-EED9F2289F9B / 2460 | yes |
| HO-038 | unstructured | 2 | REQUEST_REVIEW | ALLOW | 1120D96F-DC0B-11F1-A405-EED9F2289F9B / 2516 | — |
| HO-041 | unstructured | 2 | ALLOW | QUARANTINE | 37946364-DC0B-11F1-A405-EED9F2289F9B / 2598 | — |
| HO-046 | unstructured | 2 | ALLOW | QUARANTINE | 7C34A176-DC0B-11F1-A405-EED9F2289F9B / 2737 | — |
| HO-007 | structured | 3 | REQUEST_REVIEW | ALLOW | F8C92EC8-DC0B-11F1-A405-EED9F2289F9B / 2986 | yes |
| HO-008 | structured | 3 | REQUEST_REVIEW | ALLOW | 04779ED2-DC0C-11F1-A405-EED9F2289F9B / 3014 | yes |
| HO-010 | unstructured | 3 | ALLOW | QUARANTINE | 1EC2E373-DC0C-11F1-A405-EED9F2289F9B / 3069 | — |
| HO-013 | unstructured | 3 | ALLOW | QUARANTINE | 4E703DC5-DC0C-11F1-A405-EED9F2289F9B / 3152 | — |
| HO-015 | unstructured | 3 | QUARANTINE | ALLOW | E5A37081-DC0C-11F1-A405-EED9F2289F9B / 3208 | — |
| HO-016 | unstructured | 3 | REQUEST_REVIEW | ALLOW | F7D99730-DC0C-11F1-A405-EED9F2289F9B / 3235 | — |
| HO-023 | structured | 3 | REQUEST_REVIEW | ALLOW | 765A7294-DC26-11F1-9DB5-369FB6BCC8E5 / 3430 | yes |
| HO-027 | unstructured | 3 | ALLOW | INVALID | 01CE657A-DC27-11F1-9DB5-369FB6BCC8E5 / 3540 | — |
| HO-029 | unstructured | 3 | ALLOW | QUARANTINE | 69210B83-DC27-11F1-9DB5-369FB6BCC8E5 / 3598 | — |
| HO-031 | clean | 3 | ALLOW | INVALID | D5F6F00E-DC27-11F1-9DB5-369FB6BCC8E5 / 3654 | yes |
| HO-033 | clean | 3 | ALLOW | INVALID | 9EFC5D0F-DC28-11F1-9DB6-369FB6BCC8E5 / 3702 | yes |
| HO-034 | clean | 3 | ALLOW | INVALID | 0E52EDB1-DC29-11F1-9DB6-369FB6BCC8E5 / 3722 | yes |
| HO-036 | structured | 3 | REQUEST_REVIEW | ALLOW | 7F709CB3-DC29-11F1-9DB6-369FB6BCC8E5 / 3779 | yes |
| HO-038 | unstructured | 3 | REQUEST_REVIEW | ALLOW | B8287B48-DC29-11F1-9DB6-369FB6BCC8E5 / 3835 | — |
| HO-041 | unstructured | 3 | ALLOW | QUARANTINE | 4A71850B-DC2A-11F1-9DB6-369FB6BCC8E5 / 3917 | — |
| HO-042 | unstructured | 3 | QUARANTINE | INVALID | 77DFEFA8-DC2A-11F1-9DB6-369FB6BCC8E5 / 3945 | yes |
| HO-046 | unstructured | 3 | ALLOW | QUARANTINE | 91F7F7AB-DC2B-11F1-9DB6-369FB6BCC8E5 / 4048 | — |

### agent+policy

**48 failures.**

| Scenario | Category | Trial | Truth | Observed | Native case / session | Rules win |
| --- | --- | ---: | --- | --- | --- | --- |
| HO-001 | unstructured | 1 | ALLOW | QUARANTINE | 419BD47A-DC05-11F1-A103-A90DC9E483ED / 169 | — |
| HO-006 | unstructured | 1 | ALLOW | REQUEST_REVIEW | 80DA163B-DC05-11F1-A103-A90DC9E483ED / 306 | — |
| HO-010 | unstructured | 1 | ALLOW | QUARANTINE | B9361C84-DC05-11F1-A103-A90DC9E483ED / 417 | — |
| HO-013 | unstructured | 1 | ALLOW | QUARANTINE | E38CE5ED-DC05-11F1-A103-A90DC9E483ED / 500 | — |
| HO-015 | unstructured | 1 | QUARANTINE | REQUEST_REVIEW | 00F17A1E-DC06-11F1-A103-A90DC9E483ED / 556 | — |
| HO-016 | unstructured | 1 | REQUEST_REVIEW | ALLOW | 0CBE95FF-DC06-11F1-A103-A90DC9E483ED / 584 | — |
| HO-017 | unstructured | 1 | QUARANTINE | REQUEST_REVIEW | 1B3FF51D-DC06-11F1-A103-A90DC9E483ED / 611 | — |
| HO-020 | unstructured | 1 | ALLOW | QUARANTINE | 410F4578-DC06-11F1-A103-A90DC9E483ED / 694 | — |
| HO-027 | unstructured | 1 | ALLOW | QUARANTINE | 8EEF71DF-DC06-11F1-A103-A90DC9E483ED / 886 | — |
| HO-029 | unstructured | 1 | ALLOW | QUARANTINE | A6029EE3-DC06-11F1-A103-A90DC9E483ED / 942 | — |
| HO-030 | unstructured | 1 | QUARANTINE | REQUEST_REVIEW | B32F3862-DC06-11F1-A103-A90DC9E483ED / 970 | — |
| HO-038 | unstructured | 1 | REQUEST_REVIEW | ALLOW | 0BD31164-DC07-11F1-A103-A90DC9E483ED / 1190 | — |
| HO-041 | unstructured | 1 | ALLOW | QUARANTINE | 2EC60671-DC07-11F1-A103-A90DC9E483ED / 1272 | — |
| HO-045 | unstructured | 1 | QUARANTINE | REQUEST_REVIEW | 5D9DCCA2-DC07-11F1-A103-A90DC9E483ED / 1383 | — |
| HO-046 | unstructured | 1 | ALLOW | REQUEST_REVIEW | 696EF1CB-DC07-11F1-A103-A90DC9E483ED / 1411 | — |
| HO-001 | unstructured | 2 | ALLOW | QUARANTINE | 95AF527A-DC07-11F1-A103-A90DC9E483ED / 1495 | — |
| HO-006 | unstructured | 2 | ALLOW | REQUEST_REVIEW | E6C2A20F-DC07-11F1-A103-A90DC9E483ED / 1632 | — |
| HO-010 | unstructured | 2 | ALLOW | QUARANTINE | 23E1B43E-DC08-11F1-A103-A90DC9E483ED / 1743 | — |
| HO-013 | unstructured | 2 | ALLOW | QUARANTINE | 532C31D4-DC08-11F1-A103-A90DC9E483ED / 1826 | — |
| HO-015 | unstructured | 2 | QUARANTINE | ALLOW | 730337E4-DC08-11F1-A103-A90DC9E483ED / 1882 | — |
| HO-016 | unstructured | 2 | REQUEST_REVIEW | ALLOW | 89539426-DC08-11F1-A103-A90DC9E483ED / 1909 | — |
| HO-017 | unstructured | 2 | QUARANTINE | REQUEST_REVIEW | FD0C8536-DC09-11F1-A405-EED9F2289F9B / 1937 | — |
| HO-020 | unstructured | 2 | ALLOW | QUARANTINE | 2C52D7EC-DC0A-11F1-A405-EED9F2289F9B / 2020 | — |
| HO-027 | unstructured | 2 | ALLOW | QUARANTINE | 88150365-DC0A-11F1-A405-EED9F2289F9B / 2212 | — |
| HO-029 | unstructured | 2 | ALLOW | QUARANTINE | A0231CEA-DC0A-11F1-A405-EED9F2289F9B / 2268 | — |
| HO-030 | unstructured | 2 | QUARANTINE | REQUEST_REVIEW | ACE347EF-DC0A-11F1-A405-EED9F2289F9B / 2296 | — |
| HO-038 | unstructured | 2 | REQUEST_REVIEW | ALLOW | 1120D96F-DC0B-11F1-A405-EED9F2289F9B / 2516 | — |
| HO-041 | unstructured | 2 | ALLOW | QUARANTINE | 37946364-DC0B-11F1-A405-EED9F2289F9B / 2598 | — |
| HO-045 | unstructured | 2 | QUARANTINE | REQUEST_REVIEW | 7038876A-DC0B-11F1-A405-EED9F2289F9B / 2709 | — |
| HO-046 | unstructured | 2 | ALLOW | REQUEST_REVIEW | 7C34A176-DC0B-11F1-A405-EED9F2289F9B / 2737 | — |
| HO-001 | unstructured | 3 | ALLOW | QUARANTINE | A26B8A87-DC0B-11F1-A405-EED9F2289F9B / 2821 | — |
| HO-006 | unstructured | 3 | ALLOW | REQUEST_REVIEW | E8D0E097-DC0B-11F1-A405-EED9F2289F9B / 2958 | — |
| HO-010 | unstructured | 3 | ALLOW | QUARANTINE | 1EC2E373-DC0C-11F1-A405-EED9F2289F9B / 3069 | — |
| HO-013 | unstructured | 3 | ALLOW | QUARANTINE | 4E703DC5-DC0C-11F1-A405-EED9F2289F9B / 3152 | — |
| HO-015 | unstructured | 3 | QUARANTINE | ALLOW | E5A37081-DC0C-11F1-A405-EED9F2289F9B / 3208 | — |
| HO-016 | unstructured | 3 | REQUEST_REVIEW | ALLOW | F7D99730-DC0C-11F1-A405-EED9F2289F9B / 3235 | — |
| HO-017 | unstructured | 3 | QUARANTINE | REQUEST_REVIEW | 0B47BE2F-DC0D-11F1-A405-EED9F2289F9B / 3262 | — |
| HO-020 | unstructured | 3 | ALLOW | QUARANTINE | 29C3820C-DC26-11F1-9DB5-369FB6BCC8E5 / 3348 | — |
| HO-027 | unstructured | 3 | ALLOW | QUARANTINE | 01CE657A-DC27-11F1-9DB5-369FB6BCC8E5 / 3540 | — |
| HO-029 | unstructured | 3 | ALLOW | QUARANTINE | 69210B83-DC27-11F1-9DB5-369FB6BCC8E5 / 3598 | — |
| HO-030 | unstructured | 3 | QUARANTINE | REQUEST_REVIEW | A37EE232-DC27-11F1-9DB5-369FB6BCC8E5 / 3626 | — |
| HO-031 | clean | 3 | ALLOW | REQUEST_REVIEW | D5F6F00E-DC27-11F1-9DB5-369FB6BCC8E5 / 3654 | yes |
| HO-033 | clean | 3 | ALLOW | REQUEST_REVIEW | 9EFC5D0F-DC28-11F1-9DB6-369FB6BCC8E5 / 3702 | yes |
| HO-034 | clean | 3 | ALLOW | REQUEST_REVIEW | 0E52EDB1-DC29-11F1-9DB6-369FB6BCC8E5 / 3722 | yes |
| HO-038 | unstructured | 3 | REQUEST_REVIEW | ALLOW | B8287B48-DC29-11F1-9DB6-369FB6BCC8E5 / 3835 | — |
| HO-041 | unstructured | 3 | ALLOW | QUARANTINE | 4A71850B-DC2A-11F1-9DB6-369FB6BCC8E5 / 3917 | — |
| HO-045 | unstructured | 3 | QUARANTINE | REQUEST_REVIEW | 6B25A5FF-DC2B-11F1-9DB6-369FB6BCC8E5 / 4020 | — |
| HO-046 | unstructured | 3 | ALLOW | REQUEST_REVIEW | 91F7F7AB-DC2B-11F1-9DB6-369FB6BCC8E5 / 4048 | — |

## Limits and interpretation

- This is a small, synthetic, implementation-aware, contract-first challenge set; it was not independently human-adjudicated. Freezing before execution prevents output-driven relabelling, not author or selection bias. It is held out from the original five-case demo, not a randomly sampled production workload.
- The prose cases deliberately supply authoritative text with stale structured export columns. That probes a broader business-semantic task than the shipped structured-authority policy promises. The released prompt includes candidate findings and requires quarantine of current critical contradictions; this can anchor the agent to the structured baseline. Policy vetoes may prevent a correct prose-based recommendation from releasing an order. No runtime/prompt change was made to fix this limitation.
- A prose authority assumption in these synthetic contracts is not evidence of real buyer identity, legal enforceability or external document authenticity. Clean false-positive traps and unstructured scenarios must not be marketed as measured customer coverage.
- Agent-only is a raw recommendation ablation, not a separately deployed autonomous system. Neither baseline nor raw-agent counterfactual ALLOW recommendations caused delivery. All observed deliveries are local simulator effects; no external ERP/bank was contacted.
- Native agent statuses: `{'returned': 139, 'failed': 5}`. Invalid outputs and failed invocations remain counted. Route/effect discrepancies in shipped arm: **0**. See every raw record for failure stage, tool reads and provider metadata.
- **5 / 144** raw responses fail the released output-schema checks (separate from the invalid-decision count). A recognizable raw decision in a schema-invalid object is still scored as that agent-only choice. Schema errors for every response are in summary.json.
- One harness preparation error called a private reference-seeding method before any held-out case or inference existed. It was repaired in test-only code; the failed attempt is retained. Rules-only results were preserved. No selective model rerun or label edit was used.
- After 64 completed investigations, a disk safety-floor pause and VM out-of-memory kills interrupted the test infrastructure. The same evaluation container was restarted after other IRIS instances were stopped; completed cases were not rerun. Runtime, inputs and model configuration were retained. The manifest records this recovery. Timing includes resource contention around the interruption and cannot establish dedicated-server performance.
- Later host-disk pauses also retained their completed cases. Following owner-authorized cleanup, the final resume used the same evaluation container and stopped the normal local app temporarily to avoid running two IRIS instances in the small VM. Dataset bytes and earlier raw trial records were checked against the committed checkpoint. All persisted failures, including provider timeouts, remain in this comparison; none received a selective retry.

## Reproduce and inspect

The first run uses an isolated source-loaded live 154U instance prepared with the existing local verification driver. Setup's original native suite, five live demo cases, warmup and embedding preparation are **outside** the held-out denominators. Local Docker storage was expanded without deleting existing projects or weakening the storage floor. [Environment/setup receipt](../evidence/heldout/setup.json).

```sh
uv run python scripts/run_heldout.py --execute
uv run python scripts/report_heldout.py
```

The runner refuses changed frozen inputs and resumes persisted cases without redispatch. Existing output belongs to its retained native instance; a fresh replication needs a new instance and a separate --output directory. It runs only local inference. Native message/reference payloads are copied without categories or truth labels. Preserve private credentials outside Git.

[Raw run manifest](../evidence/heldout/manifest.json) · [rule-only native output](../evidence/heldout/rules-only.json) · [trial 1](../evidence/heldout/trial-1/) · [trial 2](../evidence/heldout/trial-2/) · [trial 3](../evidence/heldout/trial-3/) · [machine-readable summary, all failures and timings](../evidence/heldout/summary.json). No evidence file exceeds 50 MB.
