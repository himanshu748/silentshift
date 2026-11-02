"""Evaluation reporting that keeps local safety regressions separate from AI runs.

Native metadata is checked for consistency. The caller must obtain exports from
the actual IRIS production; this module cannot authenticate a hand-authored file.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import mean
from typing import Any

from .engine import DECISIONS, assess, rule_only, strict_loads, validate_policy, _recommendation_errors


def load_dataset(path: str | Path) -> dict[str, Any]:
    """Reject a changed dataset until its manifest/version is deliberately updated."""
    source = Path(path)
    manifest = strict_loads(source.with_name("manifest.json").read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Frozen dataset checksum does not match manifest")
    dataset = strict_loads(source.read_text())
    if dataset["dataset_version"] != manifest["dataset_version"] or len(dataset["scenarios"]) != manifest["scenario_count"]:
        raise ValueError("Dataset version or case count does not match manifest")
    ids = [case["id"] for case in dataset["scenarios"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Dataset scenario IDs must be unique")
    return dataset


def _rate(numerator: int, denominator: int) -> dict[str, Any]:
    return {"value": numerator / denominator if denominator else None,
            "numerator": numerator, "denominator": denominator}


def policy_regression(dataset: dict[str, Any]) -> dict[str, Any]:
    """Execute frozen local policy inputs, with no AI execution claim."""
    rows = []
    for case in dataset["scenarios"]:
        assessment = assess(case["message"], case["references"], dataset["clock"])
        policy = validate_policy(assessment, case["test_recommendation"])
        rows.append({"scenario_id": case["id"], "expected": case["ground_truth"]["decision"],
                     "classification": assessment["classification"], "baseline": rule_only(assessment),
                     "test_proposal": case["test_recommendation"]["decision"], "policy": policy["decision"],
                     "passed": policy["decision"] == case["ground_truth"]["decision"]})
    return {"dataset_version": dataset["dataset_version"], "execution": "local-deterministic-policy",
            "recommendation_source": "frozen test inputs; no model invoked",
            "baseline_accuracy": _rate(sum(row["baseline"] == row["expected"] for row in rows), len(rows)),
            "policy_regression_pass_rate": _rate(sum(row["passed"] for row in rows), len(rows)),
            "cases": rows}


def _build154(version: Any) -> bool:
    if not isinstance(version, str):
        return False
    if re.search(r"(?<![\d.])2026\.3\.0AI\.154\.0(?![\d.])", version, re.I):
        return True
    return (bool(re.search(r"(?<![\d.])2026\.3\.0AI(?![\d.])", version, re.I))
            and bool(re.search(r"\bBuild\s*154\b", version, re.I)))


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 10**15 and math.isfinite(value)


def _identity_free(message: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in message.items() if key not in {"event_id", "correlation_id"}}


def aggregate_native(artifact: Any, dataset: dict[str, Any]) -> dict[str, Any]:
    """Aggregate persisted actual native records; never fill absent runs with fixtures.

    Repeated trials require separate exports/run IDs. Within one run every frozen
    scenario is accepted at most once; duplicate scenario IDs are all excluded.
    """
    issues: list[str] = []
    accepted: list[tuple[dict, dict, Any]] = []
    cases = {case["id"]: case for case in dataset["scenarios"]}
    if artifact is None:
        issues.append("No native execution export supplied.")
    elif not isinstance(artifact, dict):
        issues.append("Native export must be an object.")
    else:
        if artifact.get("dataset_version") != dataset["dataset_version"]:
            issues.append("Native export dataset version does not match frozen ground truth.")
        if not _build154(artifact.get("iris_version")):
            issues.append("Native export does not identify IRIS 2026.3.0AI build 154.")
        if artifact.get("production") != "SilentShift.Production":
            issues.append("Native export does not identify SilentShift.Production.")
        if artifact.get("native_verified") is not True:
            issues.append("Actual HTTP, native tool, trace and routing verification has not been attested by the verification script.")
        if not isinstance(artifact.get("records"), list):
            issues.append("Native export records are absent.")
    export_valid = not issues
    records = artifact["records"] if export_valid else []
    counts = Counter(record.get("scenario_id") for record in records if isinstance(record, dict) and isinstance(record.get("scenario_id"), str))
    for index, record in enumerate(records):
        prefix = f"Record {index + 1}"
        if not isinstance(record, dict):
            issues.append(prefix + " is not an object.")
            continue
        sid = record.get("scenario_id")
        if not isinstance(sid, str) or sid not in cases or counts[sid] != 1:
            issues.append(prefix + " has an unknown or duplicate scenario ID.")
            continue
        case = cases[sid]
        if record.get("dataset_version") != dataset["dataset_version"]:
            issues.append(prefix + " dataset version does not match.")
            continue
        message = record.get("message")
        if not isinstance(message, dict) or _identity_free(message) != _identity_free(case["message"]):
            issues.append(prefix + " event differs from the frozen semantic fixture.")
            continue
        agent = record.get("agent")
        reads = agent.get("tool_reads") if isinstance(agent, dict) else None
        if (not isinstance(agent, dict) or agent.get("mode") != "native-ai-hub"
                or not isinstance(reads, dict)
                or any(not _number(reads.get(name)) or reads[name] < 1 for name in ("message", "contracts", "related"))):
            issues.append(prefix + " lacks the three required native read-only tool invocations.")
            continue
        policy = record.get("policy")
        if not isinstance(policy, dict) or not isinstance(policy.get("decision"), str) or policy["decision"] not in DECISIONS:
            issues.append(prefix + " has no persisted supported final policy decision.")
            continue
        routing = record.get("routing")
        if not isinstance(routing, str) or routing.upper() not in {"DELIVERED", "QUARANTINED", "QUARANTINE", "REVIEW", "REQUEST_REVIEW", "PENDING_REVIEW"}:
            issues.append(prefix + " lacks an observed final routing state.")
            continue
        recommendation = record.get("recommendation")
        if isinstance(recommendation, str):
            try:
                recommendation = strict_loads(recommendation)
            except (ValueError, TypeError, RecursionError):
                recommendation = None
        accepted.append((record, case, recommendation))
    total = len(accepted)
    allowed_truth = sum(case["ground_truth"]["decision"] == "ALLOW" for _, case, _ in accepted)
    held_truth = total - allowed_truth
    proposal_correct = 0
    proposal_valid = 0
    final_correct = 0
    false_quarantine = 0
    unsafe_release = 0
    unsafe_allow = 0
    reviews = 0
    latencies: list[float] = []
    usage_values: dict[str, list[int | float]] = {name: [] for name in ("total_prompt_tokens", "total_completion_tokens", "total_tool_calls")}
    rows = []
    for record, case, recommendation in accepted:
        expected = case["ground_truth"]["decision"]
        final = record["policy"]["decision"]
        assessment = assess(case["message"], case["references"], dataset["clock"])
        valid = not _recommendation_errors(recommendation, set(assessment["evidence_ids"]))
        proposed = recommendation["decision"] if valid else None
        proposal_valid += int(valid)
        proposal_correct += int(valid and proposed == expected)
        final_correct += int(final == expected)
        false_quarantine += int(expected == "ALLOW" and final == "QUARANTINE")
        unsafe_release += int(expected != "ALLOW" and record["routing"].upper() == "DELIVERED")
        unsafe_allow += int(expected != "ALLOW" and final == "ALLOW")
        reviews += int(final == "REQUEST_REVIEW")
        latency = record["agent"].get("elapsed_ms")
        if _number(latency):
            latencies.append(float(latency))
        usage = record["agent"].get("usage")
        if isinstance(usage, dict):
            aliases = {"total_prompt_tokens": "prompt_tokens", "total_completion_tokens": "completion_tokens", "total_tool_calls": "total_tool_calls"}
            for name in usage_values:
                value = usage.get(name, usage.get(aliases[name]))
                if _number(value):
                    usage_values[name].append(value)
        route = record["routing"].upper()
        expected_routes = {"ALLOW": {"DELIVERED"}, "QUARANTINE": {"QUARANTINE", "QUARANTINED"},
                           "REQUEST_REVIEW": {"REVIEW", "REQUEST_REVIEW", "PENDING_REVIEW"}}
        rows.append({"scenario_id": case["id"], "expected": expected, "proposal": proposed,
                     "proposal_valid": valid, "final": final, "routing": record["routing"],
                     "passed": final == expected and route in expected_routes[expected]})
    observed_usage = {name: {"value": sum(values) if values and len(values) == total else None,
                             "observed_records": len(values), "total_records": total}
                      for name, values in usage_values.items()}
    return {"dataset_version": dataset["dataset_version"],
            "status": "NOT_RUN" if not total else ("MEASURED_COMPLETE" if total == len(cases) and not issues else "PARTIAL"),
            "passed": bool(total == len(cases) and not issues and all(row["passed"] for row in rows)),
            "execution": "native-ai-hub-export", "provenance": "Metadata validated; source authenticity depends on the actual native verification script and retained traces.",
            "expected_cases": len(cases), "accepted_records": total,
            "excluded_records": len(records) - total,
            "proposal_accuracy": _rate(proposal_correct, total), "proposal_validity": _rate(proposal_valid, total),
            "final_accuracy": _rate(final_correct, total), "false_quarantine_rate": _rate(false_quarantine, allowed_truth),
            "unsafe_release": {"count": unsafe_release if total else None, "denominator": held_truth},
            "unsafe_allow": {"count": unsafe_allow if total else None, "denominator": held_truth},
            "review_rate": _rate(reviews, total),
            "latency": {"scope": "agent invocation only", "mean_ms": mean(latencies) if latencies else None,
                        "p95_ms": sorted(latencies)[math.ceil(len(latencies) * 0.95) - 1] if latencies else None,
                        "observed_records": len(latencies), "total_records": total},
            "model_usage": observed_usage, "model_cost": None,
            "model_cost_note": "No billing-derived cost supplied; no estimates inferred from tokens.",
            "issues": issues, "cases": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Path to frozen scenarios.json beside manifest.json")
    parser.add_argument("--native-export", help="Export written by actual native verification; omit for no-run metrics")
    parser.add_argument("--output", help="Optional JSON report path; otherwise prints to stdout")
    args = parser.parse_args()
    dataset = load_dataset(args.dataset)
    artifact = strict_loads(Path(args.native_export).read_text(), max_bytes=5_000_000) if args.native_export else None
    report = {"local_safety": policy_regression(dataset), "native": aggregate_native(artifact, dataset)}
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
