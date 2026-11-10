"""Pure, deterministic functions shared by IRIS Embedded Python and local tests.

This package is not an interoperability runtime or an AI Hub substitute.
"""

from .engine import (
    assess,
    assess_json,
    evaluate_json,
    policy_json,
    rule_only,
    validate_policy,
)

__all__ = ["assess", "assess_json", "evaluate_json", "policy_json", "rule_only", "validate_policy"]
