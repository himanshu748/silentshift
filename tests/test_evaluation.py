import copy
import json
from pathlib import Path

import pytest

from silentshift.engine import assess, validate_policy
from silentshift.evaluation import aggregate_native, load_dataset, policy_regression, _build154

DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures/v1/scenarios.json"
DATASET = load_dataset(DATASET_PATH)


def synthetic_export_for_aggregator_test():
    """Explicit test data for aggregation logic; never saved as native evidence."""
    records = []
    for case in DATASET["scenarios"]:
        assessment = assess(case["message"], case["references"], DATASET["clock"])
        recommendation = copy.deepcopy(case["test_recommendation"])
        policy = validate_policy(assessment, recommendation)
        records.append({"scenario_id": case["id"], "dataset_version": DATASET["dataset_version"],
                        "message": copy.deepcopy(case["message"]), "assessment": assessment,
                        "recommendation": recommendation, "policy": policy,
                        "routing": {"ALLOW": "DELIVERED", "QUARANTINE": "QUARANTINED", "REQUEST_REVIEW": "REVIEW"}[policy["decision"]],
                        "agent": {"mode": "native-ai-hub", "model": "test-only", "elapsed_ms": 100,
                                  "tool_reads": {"message": 1, "contracts": 1, "related": 1},
                                  "usage": {"total_prompt_tokens": 10, "total_completion_tokens": 4, "total_tool_calls": 3}}})
    return {"dataset_version": DATASET["dataset_version"], "iris_version": "2026.3.0AI.154.0",
            "production": "SilentShift.Production", "native_verified": True, "records": records}


def test_no_native_runs_never_become_perfect_accuracy():
    report = aggregate_native(None, DATASET)
    assert report["status"] == "NOT_RUN"
    assert report["final_accuracy"] == {"value": None, "numerator": 0, "denominator": 0}
    assert report["unsafe_release"] == {"count": None, "denominator": 0}
    assert report["latency"]["mean_ms"] is None
    assert report["model_usage"]["total_prompt_tokens"]["value"] is None
    assert not report["passed"]


def test_local_regression_has_honest_scope_and_measured_denominators():
    report = policy_regression(DATASET)
    assert report["execution"] == "local-deterministic-policy"
    assert "no model invoked" in report["recommendation_source"]
    assert report["policy_regression_pass_rate"] == {"value": 1.0, "numerator": 5, "denominator": 5}


def test_aggregate_actual_fields_with_explicit_denominators():
    report = aggregate_native(synthetic_export_for_aggregator_test(), DATASET)
    assert report["status"] == "MEASURED_COMPLETE"
    assert report["passed"]
    assert report["final_accuracy"]["value"] == 1
    assert report["proposal_accuracy"] == {"value": 0.8, "numerator": 4, "denominator": 5}
    assert report["false_quarantine_rate"]["denominator"] == 1
    assert report["unsafe_release"] == {"count": 0, "denominator": 4}
    assert report["review_rate"] == {"value": 0.2, "numerator": 1, "denominator": 5}
    assert report["latency"]["p95_ms"] == 100
    assert report["model_usage"]["total_prompt_tokens"]["value"] == 50
    assert report["model_cost"] is None


@pytest.mark.parametrize("version", ["2026.3.0AI.154.0", "IRIS for UNIX Version2026.3.0AI (Build154)", "IRIS 2026.3.0AI (Build 154)"])
def test_mandatory_build154_formats(version):
    assert _build154(version)


@pytest.mark.parametrize("version", ["2026.3.0AI.154.01", "2026.3.0AI.1154.0", "2026.3.0AI (Build1154)", "2026.3.0AI (Build1540)", "2026.4.0 (Build154)", None])
def test_wrong_build_is_rejected(version):
    assert not _build154(version)


@pytest.mark.parametrize("mutation", [
    lambda artifact: artifact.update({"native_verified": False}),
    lambda artifact: artifact.update({"dataset_version": "invented"}),
    lambda artifact: artifact.update({"production": "Some.OtherProduction"}),
    lambda artifact: artifact.update({"iris_version": "2026.3.0AI.153.0"}),
])
def test_invalid_native_proof_yields_no_native_metrics(mutation):
    artifact = synthetic_export_for_aggregator_test()
    mutation(artifact)
    report = aggregate_native(artifact, DATASET)
    assert report["final_accuracy"]["value"] is None
    assert report["accepted_records"] == 0
    assert report["issues"]


def test_duplicate_scenarios_cannot_be_cherry_picked():
    artifact = synthetic_export_for_aggregator_test()
    artifact["records"].append(copy.deepcopy(artifact["records"][0]))
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 4
    assert report["excluded_records"] == 2
    assert report["status"] == "PARTIAL"
    assert not report["passed"]


def test_changed_semantics_and_missing_native_tools_are_excluded():
    artifact = synthetic_export_for_aggregator_test()
    artifact["records"][0]["message"]["unit"] = "EA"
    artifact["records"][1]["agent"]["tool_reads"]["contracts"] = 0
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 3
    assert report["excluded_records"] == 2


@pytest.mark.parametrize("prompt_version", ["silentshift-investigator/1.0.0", "silentshift-investigator/1.2.0"])
def test_historical_three_tool_catalog_remains_accepted(prompt_version):
    artifact = synthetic_export_for_aggregator_test()
    for record in artifact["records"]:
        record["agent"]["prompt_version"] = prompt_version
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 5
    assert report["passed"]


@pytest.mark.parametrize("prompt_version", ["silentshift-investigator/1.3.0", "silentshift-investigator/1.10.0", "silentshift-investigator/2.0.0"])
def test_current_prompt_requires_actual_fourth_read(prompt_version):
    artifact = synthetic_export_for_aggregator_test()
    for record in artifact["records"]:
        record["agent"].update({"prompt_version": prompt_version, "tool_catalog_version": "silentshift-evidence-tools/1"})
        record["agent"]["tool_reads"]["precedents"] = 1
    artifact["records"][0]["agent"]["tool_reads"]["precedents"] = 0
    del artifact["records"][1]["agent"]["tool_reads"]["precedents"]
    artifact["records"][2]["agent"]["tool_reads"]["precedents"] = True
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 2
    assert report["excluded_records"] == 3
    assert sum("four required" in issue for issue in report["issues"]) == 3
    assert not report["passed"]


def test_explicit_current_catalog_requires_fourth_read_with_older_prompt():
    artifact = synthetic_export_for_aggregator_test()
    for record in artifact["records"]:
        record["agent"].update({"prompt_version": "silentshift-investigator/1.2.0", "tool_catalog_version": "silentshift-evidence-tools/2"})
        record["agent"]["tool_reads"]["precedents"] = 1
    del artifact["records"][0]["agent"]["tool_reads"]["precedents"]
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 4
    assert report["excluded_records"] == 1
    assert "four required" in report["issues"][0]


def test_current_four_tool_catalog_is_accepted_with_all_observed_reads():
    artifact = synthetic_export_for_aggregator_test()
    for record in artifact["records"]:
        record["agent"].update({"prompt_version": "silentshift-investigator/1.3.0", "tool_catalog_version": "silentshift-evidence-tools/2"})
        record["agent"]["tool_reads"]["precedents"] = 1
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 5
    assert report["passed"]


def test_unsafe_delivery_uses_persisted_routing_even_if_policy_says_quarantine():
    artifact = synthetic_export_for_aggregator_test()
    artifact["records"][0]["routing"] = "DELIVERED"
    report = aggregate_native(artifact, DATASET)
    assert report["final_accuracy"]["value"] == 1
    assert report["unsafe_release"] == {"count": 1, "denominator": 4}
    assert not report["cases"][0]["passed"]
    assert not report["passed"]


def test_malformed_recommendation_counts_as_wrong_not_excluded():
    artifact = synthetic_export_for_aggregator_test()
    artifact["records"][2]["recommendation"] = "not json"
    report = aggregate_native(artifact, DATASET)
    assert report["accepted_records"] == 5
    assert report["proposal_accuracy"]["numerator"] == 3
    assert report["proposal_validity"]["numerator"] == 4


def test_missing_usage_is_null_and_never_extrapolated():
    artifact = synthetic_export_for_aggregator_test()
    del artifact["records"][0]["agent"]["usage"]
    del artifact["records"][0]["agent"]["elapsed_ms"]
    report = aggregate_native(artifact, DATASET)
    assert report["model_usage"]["total_prompt_tokens"]["value"] is None
    assert report["model_usage"]["total_prompt_tokens"]["observed_records"] == 4
    assert report["latency"]["observed_records"] == 4


def test_changed_frozen_dataset_checksum_is_rejected(tmp_path):
    source = tmp_path / "scenarios.json"
    source.write_bytes(DATASET_PATH.read_bytes() + b" ")
    source.with_name("manifest.json").write_bytes(DATASET_PATH.with_name("manifest.json").read_bytes())
    with pytest.raises(ValueError, match="checksum"):
        load_dataset(source)
