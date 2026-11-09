"""Semantic assessment and fail-closed policy, with no I/O or model calls.

The caller obtains reference records from its trusted reference store. Message
fields can never grant a reference authority or authorize a routing action.
Decimal strings are compared exactly; the engine never repairs a transaction.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

POLICY_VERSION = "silentshift-policy/1.2.0"
SCHEMA_VERSION = "silentshift-message/1"
MAX_AGE = timedelta(hours=24)
MAX_FUTURE = timedelta(minutes=5)
MAX_UNCERTAINTY = 0.35
DECISIONS = {"ALLOW", "QUARANTINE", "REQUEST_REVIEW"}
CLASSIFICATIONS = {
    "INVALID_MESSAGE", "SUSPICIOUS", "VERIFIED_CONTRADICTION",
    "LEGITIMATE_CHANGE", "INSUFFICIENT_EVIDENCE", "CLEAR",
}
COMMON_FIELDS = {"event_id", "correlation_id", "source", "kind", "occurred_at", "contract_id", "business_unit"}
MESSAGE_FIELDS = COMMON_FIELDS | {
    "product_id", "quantity", "unit", "currency", "amount", "amount_scale", "notes", "timestamp_semantics",
}
KIND_FIELDS = {"order": ("product_id", "quantity", "unit", "business_unit"),
               "payment": ("amount", "amount_scale", "currency", "business_unit")}
NUMERIC_FIELDS = {"quantity", "amount"}
FIELD_CODES = {
    "quantity": "QUANTITY_MISMATCH", "unit": "QUANTITY_UNIT_MISMATCH",
    "amount": "AMOUNT_MISMATCH", "amount_scale": "CURRENCY_SCALE_MISMATCH",
    "currency": "CURRENCY_MISMATCH", "product_id": "PRODUCT_MAPPING_CONFLICT",
    "business_unit": "BUSINESS_UNIT_CHANGE", "timestamp_semantics": "TIMESTAMP_SEMANTICS_MISMATCH",
}


def _time(value: Any) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError("Timestamp must be an ISO 8601 string with an offset")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Timestamp must be valid ISO 8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp requires an explicit timezone")
    return parsed.astimezone(timezone.utc)


def _decimal(value: Any) -> Decimal:
    # JSON floats have already passed through binary rounding, potentially
    # erasing a contradiction before Decimal sees it. Business quantities and
    # amounts must use decimal strings or exact integer values at the boundary.
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("Expected an exact decimal string or integer")
    if len(str(value)) > 40:
        raise ValueError("Decimal representation is too long")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Expected a decimal number") from exc
    if not number.is_finite() or abs(number) > Decimal("1000000000000"):
        raise ValueError("Decimal must be finite and within 10^12")
    if number.as_tuple().exponent < -9 or number.as_tuple().exponent > 9:
        raise ValueError("Decimal precision is outside the supported range")
    return number


def normalize_quantity(quantity: Any, unit: str, units_per_case: Any | None = None) -> str:
    """Explicit utility, never applied to a message by policy or routing.

    CASE conversion requires an independently supplied pack size; absent that,
    comparison cannot assume that one CASE equals any particular number of EA.
    """
    number = _decimal(quantity)
    if number <= 0:
        raise ValueError("Quantity must be positive")
    if unit == "EA":
        return format(number, "f")
    if unit == "CASE" and units_per_case is not None:
        pack = _decimal(units_per_case)
        if pack <= 0 or pack != pack.to_integral_value():
            raise ValueError("Pack size must be a positive whole number")
        result = number * pack
        if abs(result) > Decimal("1000000000000"):
            raise ValueError("Normalized quantity exceeds the supported range")
        return format(result, "f")
    raise ValueError("Conversion requires a supported unit and explicit pack size")


def normalize_currency(amount: Any, scale: str, minor_digits: int = 2) -> str:
    """Normalize an explicitly supplied scale for tests/explanations, never repair."""
    number = _decimal(amount)
    if number < 0 or isinstance(minor_digits, bool) or not isinstance(minor_digits, int) or not 0 <= minor_digits <= 4:
        raise ValueError("Invalid amount or currency precision")
    if scale == "minor":
        if number != number.to_integral_value():
            raise ValueError("Minor-unit amount must be a whole number")
        number /= Decimal(10) ** minor_digits
    elif scale != "major":
        raise ValueError("Unknown currency scale")
    return format(number, "f")


def _text(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= 160 and not any(ord(c) < 32 for c in value)


def _finding(code: str, field: str, observed: Any, expected: Any, severity: str,
             evidence_ids: list[str], explanation: str) -> dict[str, Any]:
    return {"code": code, "field": field, "observed": observed, "expected": expected,
            "severity": severity, "evidence_ids": sorted(set(evidence_ids)), "explanation": explanation}


def _result(classification: str, findings: list[dict], evidence_ids: list[str],
            active_ids: list[str] | None = None) -> dict[str, Any]:
    return {"classification": classification, "findings": findings,
            "evidence_ids": sorted(set(evidence_ids)), "active_reference_ids": sorted(active_ids or []),
            "critical": any(item["severity"] == "critical" for item in findings),
            "schema_version": SCHEMA_VERSION}


def _validate_message(message: Any) -> list[dict]:
    errors: list[dict] = []
    if not isinstance(message, dict):
        return [_finding("INVALID_SCHEMA", "$", type(message).__name__, "object", "critical", [], "Message must be a JSON object.")]
    unknown = set(message) - MESSAGE_FIELDS
    if unknown:
        errors.append(_finding("UNKNOWN_FIELDS", "$", sorted(unknown), sorted(MESSAGE_FIELDS), "critical", [], "Unknown fields are rejected by the versioned message contract."))
    kind = message.get("kind")
    required = COMMON_FIELDS | set(KIND_FIELDS.get(kind, ())) if isinstance(kind, str) else COMMON_FIELDS
    if not isinstance(kind, str) or kind not in KIND_FIELDS:
        errors.append(_finding("INVALID_KIND", "kind", kind, list(KIND_FIELDS), "critical", [], "Unsupported message kind."))
    for field in sorted(required):
        if field in NUMERIC_FIELDS:
            try:
                value = _decimal(message.get(field))
                if value < 0 or (field == "quantity" and value == 0):
                    raise ValueError("Numeric value is outside its business range")
            except ValueError as exc:
                errors.append(_finding("INVALID_NUMBER", field, message.get(field), "valid nonnegative decimal", "critical", [], str(exc)))
        elif not _text(message.get(field)):
            errors.append(_finding("INVALID_FIELD", field, message.get(field), "nonempty bounded string", "critical", [], "Required field is absent or malformed."))
    if kind == "payment":
        if not isinstance(message.get("amount_scale"), str) or message["amount_scale"] not in {"major", "minor"}:
            errors.append(_finding("INVALID_SCALE", "amount_scale", message.get("amount_scale"), "major or minor", "critical", [], "Currency scale must be explicit."))
        if not isinstance(message.get("currency"), str) or not re.fullmatch(r"[A-Z]{3}", message["currency"]):
            errors.append(_finding("INVALID_CURRENCY", "currency", message.get("currency"), "three uppercase letters", "critical", [], "Currency must use its ISO code."))
        if message.get("amount_scale") == "minor":
            try:
                number = _decimal(message.get("amount"))
                if number != number.to_integral_value():
                    raise ValueError("Minor-unit amount must be a whole number")
            except ValueError as exc:
                errors.append(_finding("INVALID_MINOR_AMOUNT", "amount", message.get("amount"), "whole minor units", "critical", [], str(exc)))
    try:
        _time(message.get("occurred_at"))
    except ValueError as exc:
        errors.append(_finding("INVALID_TIMESTAMP", "occurred_at", message.get("occurred_at"), "ISO 8601 with timezone", "critical", [], str(exc)))
    if "notes" in message and (not isinstance(message["notes"], str) or len(message["notes"]) > 4096):
        errors.append(_finding("INVALID_NOTES", "notes", None, "text up to 4096 characters", "critical", [], "Notes are opaque untrusted data with a size limit."))
    if "timestamp_semantics" in message and not _text(message["timestamp_semantics"]):
        errors.append(_finding("INVALID_FIELD", "timestamp_semantics", None, "bounded string", "critical", [], "Timestamp semantics must be a string."))
    return errors


def _same(left: Any, right: Any, field: str) -> bool:
    return _decimal(left) == _decimal(right) if field in NUMERIC_FIELDS else left == right


def assess(message: Any, references: Any, now_iso: str) -> dict[str, Any]:
    """Assess against independent references; unusual values alone prove nothing.

    Reference validity intervals are half-open [from, to), evaluated against
    event time. Conflicting active approved references cannot be picked away.
    Two peer references cannot grant release authority, even when they agree.
    """
    errors = _validate_message(message)
    if errors:
        return _result("INVALID_MESSAGE", errors, [])
    now = _time(now_iso)  # A caller clock error is an operational error, not a bad message.
    event_time = _time(message["occurred_at"])
    findings: list[dict] = []
    clock_id = "clock:" + now.isoformat()
    if now - event_time > MAX_AGE:
        findings.append(_finding("STALE_EVENT", "occurred_at", message["occurred_at"], "within 24 hours of receipt", "warning", [clock_id], "A late event requires review; lateness alone does not prove the business data is wrong."))
    if event_time - now > MAX_FUTURE:
        findings.append(_finding("FUTURE_EVENT", "occurred_at", message["occurred_at"], "no more than 5 minutes after receipt", "warning", [clock_id], "Future event time exceeds clock-skew tolerance."))
    if not isinstance(references, list) or len(references) > 100:
        findings.append(_finding("INVALID_REFERENCE_SET", "$references", None, "up to 100 trusted records", "warning", [], "Reference retrieval failed or returned an invalid set."))
        return _result("INSUFFICIENT_EVIDENCE", findings, [clock_id] if findings[0]["code"] in {"STALE_EVENT", "FUTURE_EVENT"} else [])
    relevant: list[dict] = []
    active: list[dict] = []
    malformed = False
    # occurred_at is defined by this schema as event time, even when the partner
    # omits the optional explicit label. A processing-time reference cannot pass.
    fields = list(KIND_FIELDS[message["kind"]]) + ["timestamp_semantics"]
    for ref in references:
        if not isinstance(ref, dict):
            malformed = True
            continue
        if ref.get("contract_id") != message["contract_id"]:
            continue
        try:
            if not _text(ref.get("id")) or ref.get("authority") not in {"approved", "peer"}:
                raise ValueError("Reference requires a stable ID and known authority")
            start = _time(ref.get("effective_from"))
            end = _time(ref["effective_to"]) if ref.get("effective_to") is not None else None
            if end is not None and end <= start:
                raise ValueError("Reference interval must be nonempty")
            for field in fields:
                if field in NUMERIC_FIELDS:
                    value = _decimal(ref.get(field))
                    if value < 0 or (field == "quantity" and value == 0):
                        raise ValueError("Reference number outside business range")
                elif not _text(ref.get(field)):
                    raise ValueError("Reference is missing a required semantic field")
            if message["kind"] == "payment" and ref.get("amount_scale") not in {"major", "minor"}:
                raise ValueError("Reference scale is unknown")
            relevant.append(ref)
            if start <= event_time and (end is None or event_time < end):
                active.append(ref)
        except (ValueError, TypeError):
            malformed = True
    ids = [ref["id"] for ref in relevant]
    if any(item["code"] in {"STALE_EVENT", "FUTURE_EVENT"} for item in findings):
        ids.append(clock_id)
    if len(ids) != len(set(ids)):
        malformed = True
    if malformed:
        findings.append(_finding("INCOMPLETE_REFERENCE", "$references", None, "valid independently retrieved records", "warning", sorted(set(ids)), "Malformed or duplicate-ID references prevent a complete evidence comparison."))
        return _result("INSUFFICIENT_EVIDENCE", findings, ids)
    if not active:
        findings.append(_finding("MISSING_REFERENCE", "contract_id", message["contract_id"], "approved contract effective at event time", "warning", ids, "No valid reference covers this event time."))
        return _result("INSUFFICIENT_EVIDENCE", findings, ids)
    approved = [ref for ref in active if ref["authority"] == "approved"]
    comparison = approved or active
    for field in fields:
        values = [ref[field] for ref in comparison]
        if any(not _same(values[0], value, field) for value in values[1:]):
            findings.append(_finding("CONFLICTING_REFERENCES", field, values, "one unambiguous authoritative value", "warning", [ref["id"] for ref in comparison], "Independent active references disagree; the engine cannot select a convenient answer."))
    if any(item["code"] == "CONFLICTING_REFERENCES" for item in findings):
        return _result("INSUFFICIENT_EVIDENCE", findings, ids, [ref["id"] for ref in active])
    if not approved:
        findings.append(_finding("NO_RELEASE_AUTHORITY", "$references", "peer records", "approved contract", "warning", [ref["id"] for ref in active], "Peer data can raise a concern but cannot authorize release."))
        return _result("INSUFFICIENT_EVIDENCE", findings, ids, [ref["id"] for ref in active])
    chosen = approved[0]
    for field in fields:
        observed = message.get(field, "event_time" if field == "timestamp_semantics" else None)
        if not _same(observed, chosen[field], field):
            findings.append(_finding(FIELD_CODES[field], field, observed, chosen[field], "critical", [ref["id"] for ref in approved], "The event contradicts an approved contract effective at event time. No transformation is authorized."))
    if any(item["severity"] == "critical" for item in findings):
        return _result("VERIFIED_CONTRADICTION", findings, ids, [ref["id"] for ref in active])
    if findings:
        return _result("SUSPICIOUS", findings, ids, [ref["id"] for ref in active])
    amendment = chosen.get("amendment_of")
    predecessors = [ref for ref in relevant if ref["id"] == amendment and ref["authority"] == "approved"]
    if amendment and not predecessors:
        findings.append(_finding("MISSING_AMENDMENT_LINEAGE", "amendment_of", amendment, "retrieved prior approved contract", "warning", [chosen["id"]], "An amendment references a predecessor that was not independently retrieved."))
        return _result("INSUFFICIENT_EVIDENCE", findings, ids, [ref["id"] for ref in active])
    if predecessors:
        predecessor = predecessors[0]
        previous_end = _time(predecessor["effective_to"]) if predecessor.get("effective_to") else None
        if (previous_end is None or previous_end > _time(chosen["effective_from"])
                or _time(predecessor["effective_from"]) >= _time(chosen["effective_from"])):
            findings.append(_finding("INVALID_AMENDMENT_LINEAGE", "amendment_of", amendment, "expired predecessor before amendment", "warning", [amendment, chosen["id"]], "The claimed predecessor does not precede this amendment in time."))
            return _result("INSUFFICIENT_EVIDENCE", findings, ids, [ref["id"] for ref in active])
    if predecessors and any(not _same(chosen[field], predecessors[0][field], field) for field in fields):
        findings.append(_finding("APPROVED_AMENDMENT", "$contract", amendment, chosen["id"], "info", [amendment, chosen["id"]], "The event exactly matches a current approved amendment; historical difference is legitimate."))
        return _result("LEGITIMATE_CHANGE", findings, ids, [ref["id"] for ref in active])
    return _result("CLEAR", findings, ids, [ref["id"] for ref in active])


def rule_only(assessment: dict[str, Any], duplicate: bool = False) -> str:
    """Frozen deterministic baseline, not an agent recommendation."""
    if duplicate or assessment.get("critical") or assessment.get("classification") in {"INVALID_MESSAGE", "VERIFIED_CONTRADICTION"}:
        return "QUARANTINE"
    if assessment.get("classification") in {"CLEAR", "LEGITIMATE_CHANGE"} and assessment.get("active_reference_ids"):
        return "ALLOW"
    return "REQUEST_REVIEW"


def _recommendation_errors(recommendation: Any, known_ids: set[str]) -> list[str]:
    if not isinstance(recommendation, dict):
        return ["Agent output must be a JSON object."]
    if set(recommendation) not in ({"decision", "evidence_ids", "explanation", "uncertainty"},
                                    {"decision", "evidence_ids", "explanation", "uncertainty", "cited_findings"}):
        return ["Agent output does not match the exact recommendation schema."]
    errors: list[str] = []
    if not isinstance(recommendation["decision"], str) or recommendation["decision"] not in DECISIONS:
        errors.append("Agent proposed an unsupported decision.")
    evidence = recommendation["evidence_ids"]
    if not isinstance(evidence, list) or len(evidence) > 101 or any(not isinstance(item, str) for item in evidence):
        errors.append("Agent evidence must be a bounded list of reference IDs.")
    elif len(evidence) != len(set(evidence)) or not set(evidence) <= known_ids:
        errors.append("Agent cited duplicate or unknown evidence.")
    explanation = recommendation["explanation"]
    if not isinstance(explanation, str) or not explanation.strip() or len(explanation) > 4000:
        errors.append("Agent explanation is absent or exceeds its bound.")
    uncertainty = recommendation["uncertainty"]
    if isinstance(uncertainty, bool) or not isinstance(uncertainty, (int, float)) or not 0 <= uncertainty <= 1 or not math.isfinite(uncertainty):
        errors.append("Agent uncertainty must be a finite number from zero to one.")
    findings = recommendation.get("cited_findings", [])
    if (not isinstance(findings, list) or len(findings) > 2
            or any(not isinstance(f, dict) or set(f) != {"reference_id", "path", "quote"}
                   or not all(isinstance(f[k], str) for k in f)
                   or not 12 <= len(f["quote"]) <= 800
                   or not 1 <= len(f["path"]) <= 240 for f in findings)):
        errors.append("Cited findings must be at most two bounded reference/path/exact-quote objects.")
    return errors


def _grounded_findings(assessment: dict, recommendation: dict, context: Any) -> bool:
    """Check provenance only. This does NOT verify a model's semantic inference.

    Only server-supplied snapshots and independently assessed active references
    are eligible. A citation can contain a transaction, never authorize release.
    """
    findings = recommendation.get("cited_findings", [])
    if not findings or not isinstance(context, dict):
        return False
    message, references = context.get("message"), context.get("references")
    if not isinstance(message, dict) or not isinstance(references, list):
        return False
    active = set(assessment["active_reference_ids"])
    refs = {r.get("id"): r for r in references if isinstance(r, dict)}
    # Metadata and structured fields are not operative prose. Unknown text
    # extensions remain usable; this is not a whitelist of fixture wording.
    reserved = (MESSAGE_FIELDS - {"notes"}) | {"id", "authority", "effective_from", "effective_to",
                                "amendment_of", "approved_at", "verified_by", "sender"}
    for finding in findings:
        ref = refs.get(finding["reference_id"])
        if (not ref or ref.get("id") not in active or ref.get("authority") != "approved"
                or ref.get("contract_id") != message.get("contract_id")):
            return False
        pointer = finding["path"]
        if not pointer.startswith("/") or re.search(r"~(?![01])", pointer):
            return False
        parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer[1:].split("/")]
        if len(parts) > 6 or any(not p or p in reserved for p in parts):
            return False
        value = ref
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return False
            # Nested approval metadata, if present, must already be effective.
            try:
                event_at = _time(message.get("occurred_at"))
                if (value.get("authority", "approved") != "approved"
                        or any(k in value and _time(value[k]) > event_at
                               for k in ("approved_at", "effective_from"))
                        or (value.get("effective_to") is not None
                            and _time(value["effective_to"]) <= event_at)):
                    return False
            except (ValueError, TypeError):
                return False
            value = value[part]
        if not isinstance(value, str) or finding["quote"] not in value:
            return False
    return True


def validate_policy(assessment: Any, recommendation: Any, duplicate: bool = False,
                    evidence_context: Any = None) -> dict[str, Any]:
    """An agent cannot authorize mutation, repair, or bypass a hold.

    All evidence retrieved for an ALLOW must be cited, including an amendment's
    predecessor. This intentionally favors review over an unsupported release.
    """
    checks: list[dict[str, Any]] = []
    reasons: list[str] = []
    def check(code: str, passed: bool, reason: str) -> None:
        checks.append({"code": code, "passed": passed, "reason": reason})
        if not passed:
            reasons.append(reason)
    valid_assessment = (isinstance(assessment, dict)
                        and isinstance(assessment.get("classification"), str)
                        and assessment["classification"] in CLASSIFICATIONS
                        and isinstance(assessment.get("critical"), bool)
                        and isinstance(assessment.get("evidence_ids"), list)
                        and all(isinstance(item, str) for item in assessment.get("evidence_ids", []))
                        and isinstance(assessment.get("findings"), list)
                        and isinstance(assessment.get("active_reference_ids"), list)
                        and all(isinstance(item, str) for item in assessment.get("active_reference_ids", []))
                        and set(assessment["active_reference_ids"]) <= set(assessment["evidence_ids"])
                        and all(isinstance(item, dict) and item.get("severity") in ("critical", "warning", "info") for item in assessment.get("findings", [])))
    check("ASSESSMENT_VALID", valid_assessment, "Deterministic assessment must be complete and valid.")
    check("NOT_DUPLICATE", duplicate is False, "Duplicate event cannot create a second downstream effect.")
    critical = (not valid_assessment or assessment["critical"]
                or any(item["severity"] == "critical" for item in assessment["findings"])
                or assessment.get("classification") in {"INVALID_MESSAGE", "VERIFIED_CONTRADICTION"})
    check("NO_CRITICAL_CONTRADICTION", not critical, "Invalid messages and critical contradictions cannot be released.")
    known = set(assessment["evidence_ids"]) if valid_assessment else set()
    errors = _recommendation_errors(recommendation, known)
    check("RECOMMENDATION_VALID", not errors, "Agent output must satisfy the strict recommendation schema.")
    reasons.extend(errors)
    decision = "QUARANTINE" if critical or duplicate is not False else "REQUEST_REVIEW"
    release_eligible = False
    if not errors and valid_assessment and duplicate is False:
        cited = set(recommendation["evidence_ids"])
        covered = bool(known) and known <= cited
        resolved = assessment["classification"] in {"CLEAR", "LEGITIMATE_CHANGE"} and bool(assessment["active_reference_ids"])
        confident = recommendation["uncertainty"] <= MAX_UNCERTAINTY
        check("EVIDENCE_COMPLETE", covered, "Every independently retrieved evidence record must be cited for release.")
        check("SEMANTICS_RESOLVED", resolved, "Only a resolved comparison to an approved contract can permit release.")
        check("UNCERTAINTY_BOUNDED", confident, "Uncertainty above 0.35 requires human review.")
        release_eligible = not critical and covered and resolved and confident
        if not critical:
            proposed = recommendation["decision"]
            # A model's concern cannot turn inconclusive evidence into a
            # verified contradiction. Keep it held for a reviewer instead.
            decision = "ALLOW" if proposed == "ALLOW" and release_eligible else "REQUEST_REVIEW"
            if recommendation.get("cited_findings"):
                grounded = _grounded_findings(assessment, recommendation, evidence_context)
                check("CITED_PROSE_GROUNDED", grounded,
                      "Prose findings must quote current approved case evidence exactly; this verifies provenance, not entailment.")
                # A quoted model concern permits containment only. In particular
                # neither this path nor an ALLOW with contradictory findings can
                # authorize a release that the unchanged baseline would hold.
                if proposed == "QUARANTINE" and grounded and confident and covered:
                    if len({f["reference_id"] for f in recommendation["cited_findings"]}) > 1:
                        decision = "REQUEST_REVIEW"
                        reasons.append("A multi-record prose concern requires review; quote provenance does not establish precedence between approved records.")
                    else:
                        decision = "QUARANTINE"
                        reasons.append("Preventive hold from cited prose; semantic interpretation is model-generated, not a verified deterministic contradiction.")
                elif proposed == "ALLOW":
                    decision = "REQUEST_REVIEW"
            if proposed != "ALLOW" and decision != "QUARANTINE":
                reasons.append("Agent concerns without a grounded current-evidence citation require human review.")
    return {"decision": decision, "reasons": list(dict.fromkeys(reasons)) or ["Recommendation satisfies all deterministic release gates."],
            "checks": checks, "policy_version": POLICY_VERSION,
            "release_eligible": release_eligible, "downstream_permitted": decision == "ALLOW"}


def _reject_constant(value: str) -> None:
    raise ValueError(f"Nonfinite JSON constant {value} is not permitted")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object keys are not permitted")
        result[key] = value
    return result


def strict_loads(value: str, max_bytes: int = 131072) -> Any:
    if not isinstance(value, str) or len(value.encode("utf-8")) > max_bytes:
        raise ValueError("JSON input exceeds its size limit")
    def finite_float(raw: str) -> float:
        parsed = float(raw)
        if not math.isfinite(parsed):
            raise ValueError("Nonfinite JSON number is not permitted")
        return parsed
    return json.loads(value, parse_constant=_reject_constant, parse_float=finite_float, object_pairs_hook=_unique_object)


def _dump(value: Any) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)


def assess_json(message_json: str, refs_json: str, now_iso: str) -> str:
    try:
        message = strict_loads(message_json)
    except (ValueError, TypeError, RecursionError):
        return _dump(_result("INVALID_MESSAGE", [_finding("INVALID_JSON", "$", None, "strict JSON", "critical", [], "Payload is malformed, nonfinite, oversized, or contains duplicate keys.")], []))
    try:
        refs = strict_loads(refs_json)
    except (ValueError, TypeError, RecursionError):
        refs = None
    return _dump(assess(message, refs, now_iso))


def policy_json(assessment_json: str, recommendation_json: str, duplicate: bool = False,
                evidence_context_json: str = "") -> str:
    try:
        assessment = strict_loads(assessment_json)
    except (ValueError, TypeError, RecursionError):
        assessment = None
    try:
        recommendation = strict_loads(recommendation_json)
    except (ValueError, TypeError, RecursionError):
        recommendation = None
    try:
        context = strict_loads(evidence_context_json) if evidence_context_json else None
    except (ValueError, TypeError, RecursionError):
        context = None
    return _dump(validate_policy(assessment, recommendation, duplicate, context))


def evaluate_json(message_json: str, refs_json: str, recommendation_json: str,
                  now_iso: str, duplicate: bool = False) -> str:
    assessment = assess_json(message_json, refs_json, now_iso)
    policy = policy_json(assessment, recommendation_json, duplicate)
    return _dump({"assessment": strict_loads(assessment), "policy": strict_loads(policy)})
