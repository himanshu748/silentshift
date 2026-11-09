import copy
import json
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from silentshift.engine import (
    assess, assess_json, evaluate_json, normalize_currency, normalize_quantity,
    policy_json, rule_only, strict_loads, validate_policy,
)

DATASET = json.loads((Path(__file__).resolve().parents[1] / "fixtures/v1/scenarios.json").read_text())
NOW = DATASET["clock"]
SCENARIOS = DATASET["scenarios"]


def clean_case():
    case = copy.deepcopy(SCENARIOS[0])
    case["message"]["unit"] = "EA"
    case["message"]["quantity"] = "240"
    return case


def allow(assessment):
    return {"decision": "ALLOW", "evidence_ids": assessment["evidence_ids"],
            "explanation": "All independent contract records support this event.", "uncertainty": 0.1}


@pytest.mark.parametrize("case", SCENARIOS, ids=lambda case: case["id"])
def test_frozen_scenarios_exercise_assessment_and_policy(case):
    assessment = assess(case["message"], case["references"], NOW)
    policy = validate_policy(assessment, case["test_recommendation"])
    assert assessment["classification"] == case["ground_truth"]["classification"]
    assert policy["decision"] == case["ground_truth"]["decision"]
    assert rule_only(assessment) == case["ground_truth"]["decision"]
    assert policy["downstream_permitted"] == (policy["decision"] == "ALLOW")


def test_approved_change_is_not_quarantined_for_unusual_units():
    case = SCENARIOS[2]
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "LEGITIMATE_CHANGE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "ALLOW"
    assert assessment["findings"][0]["evidence_ids"] == ["contract:PO-2048:v1", "contract:PO-2048:v2"]


def test_high_similarity_delivered_precedent_cannot_release_current_critical_case():
    case = SCENARIOS[0]
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "VERIFIED_CONTRADICTION"
    original_ids = assessment["evidence_ids"].copy()
    assessment["precedent_context"] = {
        "status": "retrieved", "implementation": "IRIS VECTOR_COSINE",
        "model": "all-minilm:22m", "dimensions": 384, "decision_authority": False,
        "matches": [{"precedent_id": "precedent:synthetic-delivered", "source_id": "synthetic-old-case",
                     "source_type": "resolved_case", "contract_id": case["message"]["contract_id"],
                     "kind": case["message"]["kind"], "summary": "A similar historical transaction was delivered.",
                     "outcome": "DELIVERED", "similarity": 0.9999, "decision_authority": False}],
    }
    proposal = {**allow(assessment), "uncertainty": 0.0,
                "explanation": "The similar delivered precedent suggests allowing this case."}
    assert proposal["evidence_ids"] == original_ids
    result = validate_policy(assessment, proposal)
    checks = {check["code"]: check["passed"] for check in result["checks"]}
    assert checks["ASSESSMENT_VALID"] and checks["RECOMMENDATION_VALID"] and checks["EVIDENCE_COMPLETE"]
    assert not checks["NO_CRITICAL_CONTRADICTION"]
    assert result["decision"] == "QUARANTINE"
    assert result["downstream_permitted"] is False
    assert result["release_eligible"] is False


def test_missing_reference_does_not_authorize_release():
    assessment = assess(clean_case()["message"], [], NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "REQUEST_REVIEW"


def test_peers_that_agree_still_cannot_authorize_release():
    case = clean_case()
    case["references"][0]["authority"] = "peer"
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "REQUEST_REVIEW"


@pytest.mark.parametrize("context", ["clear", "missing", "conflict"])
def test_model_quarantine_cannot_claim_unverified_contradiction(context):
    case = copy.deepcopy(SCENARIOS[3]) if context == "conflict" else clean_case()
    references = [] if context == "missing" else case["references"]
    assessment = assess(case["message"], references, NOW)
    assert assessment["critical"] is False
    proposal = {**allow(assessment), "decision": "QUARANTINE"}
    policy = validate_policy(assessment, proposal)
    assert policy["decision"] == "REQUEST_REVIEW"
    assert policy["downstream_permitted"] is False


def test_conflicting_approved_references_cannot_be_selected_away():
    case = clean_case()
    conflict = {**case["references"][0], "id": "contract:other", "unit": "CASE"}
    case["references"].append(conflict)
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "REQUEST_REVIEW"


@pytest.mark.parametrize("field,value,code", [
    ("unit", "CASE", "QUANTITY_UNIT_MISMATCH"),
    ("quantity", "239", "QUANTITY_MISMATCH"),
    ("product_id", "P-WRONG", "PRODUCT_MAPPING_CONFLICT"),
    ("business_unit", "US-EAST", "BUSINESS_UNIT_CHANGE"),
])
def test_authoritative_order_mismatches_are_critical(field, value, code):
    case = clean_case()
    case["message"][field] = value
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "VERIFIED_CONTRADICTION"
    assert code in {finding["code"] for finding in assessment["findings"]}
    assert validate_policy(assessment, allow(assessment))["decision"] == "QUARANTINE"


@pytest.mark.parametrize("timestamp,expected", [
    ("2026-10-31T07:00:00Z", "STALE_EVENT"),
    ("2026-11-02T08:00:00Z", "FUTURE_EVENT"),
])
def test_timestamp_suspicion_requires_review_not_a_claim_of_wrong_data(timestamp, expected):
    case = clean_case()
    case["message"]["occurred_at"] = timestamp
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "SUSPICIOUS"
    assert not assessment["critical"]
    assert expected in {finding["code"] for finding in assessment["findings"]}
    assert validate_policy(assessment, allow(assessment))["decision"] == "REQUEST_REVIEW"


def test_timestamp_meaning_must_match_contract():
    case = clean_case()
    case["message"]["timestamp_semantics"] = "processing_time"
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "VERIFIED_CONTRADICTION"
    assert any(f["code"] == "TIMESTAMP_SEMANTICS_MISMATCH" for f in assessment["findings"])


def test_omitted_timestamp_label_still_means_event_time():
    case = clean_case()
    case["references"][0]["timestamp_semantics"] = "processing_time"
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "VERIFIED_CONTRADICTION"
    assert any(f["code"] == "TIMESTAMP_SEMANTICS_MISMATCH" for f in assessment["findings"])


def test_contract_validity_uses_event_time_and_half_open_intervals():
    case = copy.deepcopy(SCENARIOS[2])
    # At the boundary only the new amendment is active, independent of receipt time.
    case["message"]["occurred_at"] = "2026-11-01T00:00:00Z"
    assessment = assess(case["message"], case["references"], "2026-11-01T00:01:00Z")
    assert assessment["classification"] == "LEGITIMATE_CHANGE"
    assert assessment["active_reference_ids"] == ["contract:PO-2048:v2"]
    case["message"]["occurred_at"] = "2026-10-31T23:59:59Z"
    assessment = assess(case["message"], case["references"], "2026-11-01T00:01:00Z")
    assert assessment["classification"] == "VERIFIED_CONTRADICTION"
    assert assessment["active_reference_ids"] == ["contract:PO-2048:v1"]


def test_incomplete_amendment_lineage_blocks_release():
    case = copy.deepcopy(SCENARIOS[2])
    assessment = assess(case["message"], case["references"][1:], NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "REQUEST_REVIEW"


def test_future_predecessor_is_not_valid_amendment_lineage():
    case = copy.deepcopy(SCENARIOS[2])
    case["references"][0].update({"effective_from": "2026-11-05T00:00:00Z", "effective_to": "2026-11-06T00:00:00Z"})
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"
    assert any(f["code"] == "INVALID_AMENDMENT_LINEAGE" for f in assessment["findings"])


@pytest.mark.parametrize("mutation", [
    lambda case: case["message"].update({"occurred_at": "2026-11-02T07:00:00"}),
    lambda case: case["message"].update({"quantity": "NaN"}),
    lambda case: case["message"].update({"quantity": True}),
    lambda case: case["message"].update({"quantity": "-1"}),
    lambda case: case["message"].update({"quantity": "1e999999"}),
    lambda case: case["message"].update({"authority": "approved"}),
    lambda case: case["message"].update({"kind": []}),
    lambda case: case["message"].update({"notes": "x" * 4097}),
    lambda case: case["message"].pop("contract_id"),
])
def test_invalid_message_fails_closed(mutation):
    case = clean_case()
    mutation(case)
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "INVALID_MESSAGE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "QUARANTINE"


@pytest.mark.parametrize("references", [None, {}, [None], [{"id": "bad", "contract_id": "PO-2048"}]])
def test_invalid_reference_data_cannot_release(references):
    assessment = assess(clean_case()["message"], references, NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"
    assert validate_policy(assessment, allow(assessment))["decision"] == "REQUEST_REVIEW"


def test_duplicate_reference_ids_are_not_independent_evidence():
    case = clean_case()
    case["references"].append(copy.deepcopy(case["references"][0]))
    assessment = assess(case["message"], case["references"], NOW)
    assert assessment["classification"] == "INSUFFICIENT_EVIDENCE"


@pytest.mark.parametrize("recommendation", [None, "ALLOW", [], {},
    {"decision": "ALLOW", "evidence_ids": [], "explanation": "go", "uncertainty": 0, "execute": "send"},
    {"decision": "RELEASE", "evidence_ids": [], "explanation": "go", "uncertainty": 0},
    {"decision": "ALLOW", "evidence_ids": [], "explanation": "go", "uncertainty": True},
    {"decision": [], "evidence_ids": [], "explanation": "go", "uncertainty": float("nan")},
])
def test_malformed_or_mutating_agent_output_fails_safely(recommendation):
    case = clean_case()
    assessment = assess(case["message"], case["references"], NOW)
    assert validate_policy(assessment, recommendation)["decision"] == "REQUEST_REVIEW"
    contradiction = assess(SCENARIOS[0]["message"], SCENARIOS[0]["references"], NOW)
    assert validate_policy(contradiction, recommendation)["decision"] == "QUARANTINE"


def test_all_substantive_evidence_must_be_cited_and_fabricated_ids_fail():
    case = SCENARIOS[2]
    assessment = assess(case["message"], case["references"], NOW)
    recommendation = allow(assessment)
    recommendation["evidence_ids"] = ["contract:PO-2048:v2"]
    assert validate_policy(assessment, recommendation)["decision"] == "REQUEST_REVIEW"
    recommendation["evidence_ids"] = assessment["evidence_ids"] + ["imagined:approved"]
    assert validate_policy(assessment, recommendation)["decision"] == "REQUEST_REVIEW"


def test_uncertainty_is_bounded_even_for_matching_contract():
    case = clean_case()
    assessment = assess(case["message"], case["references"], NOW)
    recommendation = allow(assessment)
    recommendation["uncertainty"] = 0.36
    assert validate_policy(assessment, recommendation)["decision"] == "REQUEST_REVIEW"
    recommendation["uncertainty"] = 0.35
    assert validate_policy(assessment, recommendation)["decision"] == "ALLOW"


@pytest.mark.parametrize("mutation", [
    lambda a: a.update({"classification": []}),
    lambda a: a.update({"active_reference_ids": ["invented:release"]}),
    lambda a: a.update({"findings": [{"severity": "critical"}]}),
])
def test_corrupt_assessment_cannot_authorize_release(mutation):
    case = clean_case()
    assessment = assess(case["message"], case["references"], NOW)
    recommendation = allow(assessment)
    mutation(assessment)
    assert validate_policy(assessment, recommendation)["decision"] == "QUARANTINE"


def test_prompt_injection_is_opaque_data_and_cannot_change_assessment():
    case = clean_case()
    before = assess(case["message"], case["references"], NOW)
    case["message"]["notes"] = SCENARIOS[4]["message"]["notes"]
    assert assess(case["message"], case["references"], NOW) == before
    # The deliberately unsafe recommendation in case E is vetoed despite confidence=0 uncertainty.
    hostile = SCENARIOS[4]
    assessment = assess(hostile["message"], hostile["references"], NOW)
    result = validate_policy(assessment, hostile["test_recommendation"])
    assert not result["downstream_permitted"]
    assert not result["release_eligible"]


@pytest.mark.parametrize("payload", ['{"quantity":NaN}', '{"quantity":Infinity}', '{"quantity":1e9999}',
    '{"event_id":"a","event_id":"b"}', 'not json', '[]'])
def test_json_boundary_rejects_nonfinite_duplicate_and_malformed_payloads(payload):
    result = json.loads(assess_json(payload, "[]", NOW))
    assert result["classification"] == "INVALID_MESSAGE"


@pytest.mark.parametrize("agent_payload", ['{"decision":"ALLOW","decision":"QUARANTINE"}', 'NaN',
    '{"decision":"ALLOW","evidence_ids":[],"explanation":"go","uncertainty":1e999}', '```json\n{}\n```'])
def test_policy_json_does_not_repair_malformed_model_output(agent_payload):
    case = clean_case()
    assessment = assess_json(json.dumps(case["message"]), json.dumps(case["references"]), NOW)
    result = json.loads(policy_json(assessment, agent_payload))
    assert result["decision"] == "REQUEST_REVIEW"


def test_embedded_python_json_wrappers_execute_the_same_functions():
    case = SCENARIOS[2]
    output = json.loads(evaluate_json(json.dumps(case["message"]), json.dumps(case["references"]),
                                     json.dumps(case["test_recommendation"]), NOW))
    assert output["assessment"] == assess(case["message"], case["references"], NOW)
    assert output["policy"]["decision"] == "ALLOW"


# Property assertions establish correctness; measured latency belongs in native evidence.
# Wall-clock deadlines fluctuate under host scheduling and are not a policy contract.
@settings(deadline=None)
@given(st.integers(min_value=1, max_value=1_000_000), st.integers(min_value=1, max_value=1000))
def test_quantity_normalization_is_exact_and_requires_explicit_pack_size(cases, pack):
    assert normalize_quantity(str(cases), "CASE", str(pack)) == str(cases * pack)
    with pytest.raises(ValueError):
        normalize_quantity(str(cases), "CASE")


@settings(deadline=None)
@given(st.integers(min_value=0, max_value=100_000_000), st.integers(min_value=0, max_value=4))
def test_currency_scaling_uses_exact_decimal_arithmetic(minor, digits):
    from decimal import Decimal
    value = normalize_currency(str(minor), "minor", digits)
    assert Decimal(value) * (Decimal(10) ** digits) == Decimal(minor)


@settings(deadline=None)
@given(st.sampled_from(["ALLOW", "QUARANTINE", "REQUEST_REVIEW"]), st.floats(min_value=0, max_value=1))
def test_no_agent_recommendation_can_release_a_critical_contradiction(decision, uncertainty):
    case = SCENARIOS[0]
    assessment = assess(case["message"], case["references"], NOW)
    recommendation = {**allow(assessment), "decision": decision, "uncertainty": uncertainty}
    result = validate_policy(assessment, recommendation)
    assert result["decision"] == "QUARANTINE"
    assert not result["downstream_permitted"]


@settings(deadline=None)
@given(st.sampled_from(["ALLOW", "QUARANTINE", "REQUEST_REVIEW"]), st.text(max_size=100))
def test_duplicate_flag_never_permits_a_second_delivery(decision, explanation):
    case = clean_case()
    assessment = assess(case["message"], case["references"], NOW)
    recommendation = {**allow(assessment), "decision": decision, "explanation": explanation}
    result = validate_policy(assessment, recommendation, duplicate=True)
    assert result["decision"] == "QUARANTINE"
    assert not result["downstream_permitted"]


@settings(deadline=None)
@given(st.permutations(SCENARIOS[2]["references"]))
def test_reference_order_does_not_change_release_decision(references):
    case = SCENARIOS[2]
    assessment = assess(case["message"], list(references), NOW)
    assert validate_policy(assessment, allow(assessment))["decision"] == "ALLOW"


@settings(deadline=None)
@given(st.text(max_size=300))
def test_malformed_json_never_escapes_policy_boundary(raw):
    case = clean_case()
    assessment = assess_json(json.dumps(case["message"]), json.dumps(case["references"]), NOW)
    result = json.loads(policy_json(assessment, raw))
    assert result["decision"] in {"REQUEST_REVIEW", "QUARANTINE"}


JSON_VALUE = st.recursive(st.none() | st.booleans() | st.integers(min_value=-10**20, max_value=10**20) | st.text(max_size=30),
                          lambda children: st.lists(children, max_size=4) | st.dictionaries(st.text(max_size=20), children, max_size=4), max_leaves=10)


@settings(deadline=None)
@given(JSON_VALUE)
def test_arbitrary_json_agent_values_never_escape_policy_boundary(value):
    case = clean_case()
    assessment = assess_json(json.dumps(case["message"]), json.dumps(case["references"]), NOW)
    result = json.loads(policy_json(assessment, json.dumps(value)))
    assert result["decision"] in {"REQUEST_REVIEW", "QUARANTINE"}


@settings(deadline=None)
@given(st.dictionaries(st.sampled_from(["kind", "event_id", "amount_scale", "quantity", "notes"]), JSON_VALUE, max_size=5))
def test_arbitrary_partial_message_objects_are_contained(value):
    result = json.loads(assess_json(json.dumps(value), "[]", NOW))
    assert result["classification"] == "INVALID_MESSAGE"
