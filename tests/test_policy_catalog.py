"""The displayed policy catalog stays a description of the deterministic policy."""
from silentshift.engine import MAX_UNCERTAINTY, RULES


def test_catalog_preserves_existing_rules_and_uncertainty_threshold():
    assert RULES == [{'id': 'NO_CRITICAL_CONTRADICTION',
      'description': 'Invalid messages and verified critical contradictions cannot be released, '
                     'including by a reviewer.'},
     {'id': 'EVIDENCE_COMPLETE',
      'description': 'Every independent reference must be known and cited before release.'},
     {'id': 'SEMANTICS_RESOLVED',
      'description': 'Only a resolved comparison to an effective approved contract permits release.'},
     {'id': 'RECOMMENDATION_VALID',
      'description': 'Malformed JSON, unsupported actions and unknown evidence IDs fail safely.'},
     {'id': 'UNCERTAINTY_BOUNDED', 'description': 'Uncertainty above 0.35 requires review.'},
     {'id': 'NOT_DUPLICATE',
      'description': 'A duplicate source/event key returns the existing case and never repeats '
                     'delivery.'},
     {'id': 'REVIEW_AUTHORIZATION',
      'description': 'Review requires SSReview, a reason, current version and idempotency key.'}]
    uncertainty = next(rule for rule in RULES if rule["id"] == "UNCERTAINTY_BOUNDED")
    assert uncertainty["description"] == f"Uncertainty above {MAX_UNCERTAINTY:g} requires review."
    assert all(set(rule) == {"id", "description"} for rule in RULES)
    assert len({rule["id"] for rule in RULES}) == len(RULES)
