# Why the prose did not change the route

The v3 labels were committed before this diagnosis (`9c8d937`). v2 is now the dev set. Its original labels and historical receipts remain unchanged. No v3 case file was opened for this analysis.

## What the historical evidence supports

`GetApprovedContracts` pushes each entire approved reference object, including nested email bodies and notes, into its response. `GetRelatedRecords` returns the remaining references. Neither projects away prose. Completed tool-read counts demonstrate tool execution; historical provider exports deliberately retain metadata rather than request contents, so they do not prove the exact prompt bytes seen by the model. This diagnosis separates source inspection from observed recommendations.

The prompt anchors on `candidate_assessment`, instructs critical contradictions to be quarantined, and permits only a short explanation plus a list of all reference IDs. It has no field-level quotation contract. The old policy turns every agent-only QUARANTINE concern into REQUEST_REVIEW unless structured assessment is already critical. Thus some correct model concerns are deliberately downgraded; other prose is simply interpreted incorrectly.

## Every unstructured miss

Observed values below come from the original three trials. A/Q/R mean ALLOW/QUARANTINE/REQUEST_REVIEW; — means no accepted recommendation. The invariant requested for this repair forbids releasing any baseline hold. That makes the legitimate prose-authorized release cases an explicit ceiling, not something to fix by weakening the gate.

| Dev ID | Truth | Rule | Raw agent, trials 1–3 | Policy, trials 1–3 | Cause and repair / retained limit |
| --- | --- | --- | --- | --- | --- |
| HO-001 | A | Q | Q/A/A | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model sometimes reads the authorization correctly, but the gate must retain the hold. |
| HO-006 | A | R | A/Q/A | R/R/R | Baseline hold cannot be released under the required invariant. Model sometimes reads the authorization correctly, but the gate must retain the hold. |
| HO-010 | A | Q | Q/Q/Q | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model also misses the prose authorization; improve prose inspection, without granting release authority. |
| HO-013 | A | Q | Q/A/Q | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model sometimes reads the authorization correctly, but the gate must retain the hold. |
| HO-015 | Q | A | Q/A/A | R/A/A | Model concern is downgraded by the policy; some trials also miss it. Add a bounded exact-quote finding validated against the current approved case snapshot; allow containment only. |
| HO-016 | R | A | A/A/A | A/A/A | Model misses equally authoritative prose conflict despite matching structured rows. Require explicit inspection of all text and grounded conflict citations; hold for review. |
| HO-017 | Q | A | Q/Q/Q | R/R/R | Model concern is downgraded by the policy; Add a bounded exact-quote finding validated against the current approved case snapshot; allow containment only. |
| HO-020 | A | Q | A/Q/A | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model sometimes reads the authorization correctly, but the gate must retain the hold. |
| HO-027 | A | Q | Q/Q/— | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model also misses the prose authorization; improve prose inspection, without granting release authority. |
| HO-029 | A | Q | Q/Q/Q | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model also misses the prose authorization; improve prose inspection, without granting release authority. |
| HO-030 | Q | A | Q/Q/Q | R/R/R | Model concern is downgraded by the policy; Add a bounded exact-quote finding validated against the current approved case snapshot; allow containment only. |
| HO-038 | R | A | A/A/A | A/A/A | Model misses equally authoritative prose conflict despite matching structured rows. Require explicit inspection of all text and grounded conflict citations; hold for review. |
| HO-041 | A | Q | Q/Q/Q | Q/Q/Q | Baseline hold cannot be released under the required invariant. Model also misses the prose authorization; improve prose inspection, without granting release authority. |
| HO-045 | Q | A | Q/Q/Q | R/R/R | Model concern is downgraded by the policy; Add a bounded exact-quote finding validated against the current approved case snapshot; allow containment only. |
| HO-046 | A | R | Q/Q/Q | R/R/R | Baseline hold cannot be released under the required invariant. Model also misses the prose authorization; improve prose inspection, without granting release authority. |

## Repair contract

Keep `assess` and `rule_only` byte-for-byte unchanged. Add an optional, bounded `cited_findings` array to recommendations, preserving legacy replay responses. The prompt must inspect operative prose and quote the relevant leaf with its reference ID and JSON pointer. The server independently validates the citation against its immutable message/reference snapshot and the baseline’s active approved references. Unknown IDs, altered quotes, expired/peer/foreign references and malformed output cannot justify a grounded quarantine.

A valid quote establishes provenance, not semantic truth. A model interpretation remains fallible; grounded QUARANTINE is preventive containment, not a newly verified deterministic contradiction. It can never authorize delivery or make an existing rule hold releasable. Review proposals remain review. Report false holds and model misses rather than describing quotation checks as entailment verification.

Increase the bounded final response allowance to fit quotations; record the changed prompt version. Validate the changed production with dev inputs and regression tests before freezing its source for sealed execution. No sealed-set tuning or post-run relabelling is permitted.

Historical receipts: [rules](../evidence/heldout/rules-only.json), [all trial records](../evidence/heldout/manifest.json), [original report](EVAL_HELDOUT.md).

## Implemented on push/top3, before sealed access

Prompt `silentshift-investigator/1.4.1` explicitly distinguishes structured assessment from operative prose and asks for field-level quotations. Approved-contract results now include bounded JSON pointer locations for prose leaves, alongside the unchanged complete references. This native projection uses ObjectScript only, avoiding nested Embedded Python inside AI Hub tool callbacks. Structured baseline functions are unchanged; a regression test compares their source against the pre-repair commit.

Policy `silentshift-policy/1.2.0` accepts the legacy four-field replay response or a bounded five-field response with `cited_findings`. It checks exact quotations against the server snapshot, active approved reference IDs, contract identity, and any nested approval/effective dates. A grounded, sufficiently certain single-record concern can quarantine. A multi-record prose concern goes to review because quotation provenance cannot resolve approved-record precedence. Neither path releases a baseline hold. An ALLOW accompanied by prose concerns also goes to review.

The first two-case dev probe used prompt 1.4.0: HO-016 supplied both correct quotes but proposed quarantine; HO-017 returned duplicate JSON keys and empty quotations. Both raw attempts are retained in [the first dev probe](../evidence/dev-prose-probe/). This motivated the conservative multi-record review gate, citation locations and clearer response contract. It was not a sealed-set observation.

The subsequent dev probe on prompt 1.4.1 held HO-016 for review and quarantined HO-017 with the exact buyer-note quote. [Raw second probe](../evidence/dev-prose-probe-final/). These two development examples demonstrate the mechanism, not a held-out accuracy result. No tuning decision used v3 case contents.

The native projection test initially tried to replace a case's protected reference snapshot with SaveCase. IRIS correctly preserved the immutable snapshot. The test now seeds its own synthetic catalog scope and calls the actual SnapshotReferences method. No production immutability rule was relaxed.
