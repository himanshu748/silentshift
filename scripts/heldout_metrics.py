"""Preregistered metrics: keep failures in denominators and effects distinct."""
from __future__ import annotations
import json
from statistics import median

DECISIONS = {"ALLOW", "QUARANTINE", "REQUEST_REVIEW"}
ROUTES = {"DELIVERED": "ALLOW", "QUARANTINED": "QUARANTINE", "REVIEW": "REQUEST_REVIEW"}


def raw_proposal(record):
    agent = record.get("agent") or {}
    raw = agent.get("raw_response") or record.get("recommendation")
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (ValueError, TypeError):
        data = None
    decision = data.get("decision") if isinstance(data, dict) else None
    return decision if isinstance(decision, str) and decision in DECISIONS else "INVALID"


def score_row(case, prediction, *, delivery_count=None, elapsed_ms=None, trial=None, case_id=None, trace_id=None):
    truth = case["ground_truth"]["decision"]
    bad = truth != "ALLOW"
    return {"scenario_id": case["id"], "category": case["category"], "truth": truth,
        "prediction": prediction, "correct": prediction == truth,
        "wrong_delivery": bad and (delivery_count > 0 if delivery_count is not None else prediction == "ALLOW"),
        "wrong_delivery_scope": "actual simulator receipt" if delivery_count is not None else "counterfactual ALLOW choice",
        "false_hold": truth == "ALLOW" and prediction != "ALLOW", "review": prediction == "REQUEST_REVIEW",
        "invalid": prediction not in DECISIONS, "elapsed_ms": elapsed_ms,
        "trial": trial, "case_id": case_id, "trace_id": trace_id,
        "delivery_count": delivery_count,
        "route_effect_discrepancy": delivery_count is not None and ((prediction == "ALLOW") != (delivery_count > 0))}


def summarize(rows):
    values = [r["elapsed_ms"] for r in rows if isinstance(r.get("elapsed_ms"), (int,float))]
    total = len(rows)
    return {"n": total, "correct": sum(r["correct"] for r in rows),
        "wrong_deliveries": sum(r["wrong_delivery"] for r in rows),
        "bad_orders": sum(r["truth"] != "ALLOW" for r in rows),
        "false_holds": sum(r["false_hold"] for r in rows),
        "allow_eligible": sum(r["truth"] == "ALLOW" for r in rows),
        "reviews": sum(r["review"] for r in rows), "review_rate": sum(r["review"] for r in rows)/total if total else None,
        "invalid": sum(r["invalid"] for r in rows),
        "median_elapsed_ms": median(values) if values else None, "timing_observations": len(values),
        "route_effect_discrepancies": sum(r["route_effect_discrepancy"] for r in rows)}
