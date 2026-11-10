"""Protect semantic meaning before binary floating-point can erase a mismatch."""
import json
from pathlib import Path

import pytest
from silentshift.engine import assess_json, strict_loads, validate_policy

DATA = json.loads((Path(__file__).parents[1] / "fixtures/v1/scenarios.json").read_text())


@pytest.mark.parametrize("lexical,approved", [
    ("999999999999.99999", "1000000000000"),
    ("1e-9999", "0"),
    ("125.50000000000000001", "125.50"),
])
@pytest.mark.parametrize("canonicalize_at_ingress", [False, True])
def test_json_business_float_cannot_erase_contradiction(lexical, approved, canonicalize_at_ingress):
    case = DATA["scenarios"][1]
    message = {**case["message"], "amount": "REPLACE", "amount_scale": "major"}
    raw = json.dumps(message).replace('"REPLACE"', lexical)
    if canonicalize_at_ingress:
        # Match API.StrictJSON's normalization before the IRIS case is stored.
        raw = json.dumps(strict_loads(raw), allow_nan=False)
    refs = [{**case["references"][0], "amount": approved, "amount_scale": "major"}]
    result = json.loads(assess_json(raw, json.dumps(refs), DATA["clock"]))
    proposal = {"decision": "ALLOW", "evidence_ids": [refs[0]["id"]],
                "explanation": "Test proposal must not release a rounded value.", "uncertainty": 0.0}
    assert result["classification"] == "INVALID_MESSAGE"
    assert validate_policy(result, proposal)["decision"] == "QUARANTINE"


def test_exact_decimal_string_keeps_meaning():
    case = DATA["scenarios"][1]
    message = {**case["message"], "amount": "125.50", "amount_scale": "major"}
    assessment = json.loads(assess_json(json.dumps(message), json.dumps(case["references"]), DATA["clock"]))
    assert assessment["classification"] == "CLEAR"
