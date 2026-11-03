#!/usr/bin/env python3
"""Read actual per-provider-call native headers and typed metadata, no model runs.

The case must already have traversed the local native SDK HTTP gateway. This
script never compiles classes, edits configuration, opens leases or invokes an
LLM. It does not export prompt text, tool arguments, bearer tokens or raw bodies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bootstrap import read_env
from verify_native_trace import native

ROOT = Path(__file__).resolve().parents[1]


def validate(observed: dict, *, require_failure: bool = False) -> dict[str, bool]:
    messages = observed["provider_messages"]
    requests = [m for m in messages if m["event_kind"] == "provider_request"]
    responses = [m for m in messages if m["event_kind"] == "provider_response"]
    headers = {str(h["id"]): h for h in observed["native_headers"]}
    by_call = {m["call_id"]: m for m in requests}
    trace = str(observed["trace_id"])
    invocation = (observed.get("invocation_trace") or {}).get("invocation_id")
    pairs = []
    for response in responses:
        request = by_call.get(response["call_id"])
        if request is None:
            pairs.append(False)
            continue
        req_header = headers.get(str(request["message_header_id"]), {})
        res_header = headers.get(str(response["message_header_id"]), {})
        pairs.append(
            str(res_header.get("corresponding_message_id")) == str(req_header.get("id"))
            and req_header.get("source") == "ProviderIngress"
            and req_header.get("target") == "ProviderForwarder"
            and res_header.get("source") == "ProviderForwarder"
            and res_header.get("target") == "ProviderIngress"
            and request["round"] == response["round"]
        )
    forbidden = {"prompt", "messages", "arguments", "content", "api_key", "authorization", "raw_response", "raw_request"}
    checks = {
        "actual_native_provider_request_response_pairs": bool(requests) and len(requests) == len(responses) == len(by_call) and all(pairs),
        "original_case_session": bool(messages) and all(m["case_id"] == observed["case_id"] and str(m["production_session_id"]) == trace for m in messages) and all(str(h["session_id"]) == trace for h in headers.values()),
        "original_invocation_span": bool(invocation) and all(m["invocation_span_id"] == invocation for m in messages),
        "bounded_sequential_gateway_calls": bool(requests) and len(requests) <= 8 and sorted(m["round"] for m in requests) == list(range(1, len(requests) + 1)),
        "local_model_only": bool(messages) and all(m["model"] == "qwen3-silentshift:4b-instruct" for m in messages),
        "per_call_timing_and_http_outcome": bool(responses) and all(m["duration_ms"] >= 0 and m["started_at"] and m["finished_at"] and 100 <= m["http_status"] <= 599 for m in responses),
        "honest_unknown_retry_and_cost": bool(messages) and all(m["provider_retry_count"] is None and m["billing_cost"] is None and m["application_retry_count"] == 0 and m["fallback_used"] is False and m["usage_scope"] == "actual_http_response_only" for m in messages),
        "persistent_messages_metadata_only": bool(messages) and all(m["content_retained"] is False and not (forbidden & m.keys()) and len(json.dumps(m).encode()) <= 8192 for m in messages),
        "temporary_payload_cleanup": observed["transient_call_count"] == 0,
        "real_tool_call_metadata": any(m.get("tool_calls") for m in responses),
    }
    if require_failure:
        checks["real_provider_failure_visible"] = any(m["error_code"] and m["http_status"] >= 400 for m in responses)
        checks.pop("real_tool_call_metadata")
    else:
        checks["actual_upstream_http_responses"] = all(m["upstream_http_status"] == m["http_status"] for m in responses)
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--context")
    parser.add_argument("--container")
    parser.add_argument("--inspect-case", action="append", default=[], required=True)
    parser.add_argument("--require-failure", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/provider-calls.json")
    args = parser.parse_args()
    artifact = {"created_at": datetime.now(timezone.utc).isoformat(), "granularity": "provider_http_call", "cases": [], "passed": False}
    try:
        args.runtime_env = read_env(args.env_file)
        args.context = args.context or args.runtime_env.get("DOCKER_CONTEXT")
        project = args.runtime_env.get("COMPOSE_PROJECT_NAME", ROOT.name.lower())
        args.container = args.container or f"{project}-iris-1"
        contract = json.loads(native(args, 'write "PROVIDER_CONTRACT=",##class(SilentShift.Test.ProviderChecks).TransportContract(),!', "PROVIDER_CONTRACT="))
        artifact["transport_contract"] = contract
        contract_ok = all(contract.get(k) is True for k in ("temporary_store_safe", "entity_body_iris_temp", "response_stream_tmp", "raw_modes", "unknown_bearer_rejected", "outbound_utf8_bytes_exact", "response_cap_before_allocation", "identity_response_contract", "nonidentity_response_rejected", "replacement_response_sink_rejected"))
        if not contract_ok:
            raise ValueError("Native temporary transport contract failed")
        for case_id in args.inspect_case:
            if not re.fullmatch(r"[A-Fa-f0-9-]{36}", case_id):
                raise ValueError("Invalid native case identifier")
            observed = json.loads(native(args, f'write "PROVIDER_EXPORT=",##class(SilentShift.Test.ProviderChecks).InspectCase("{case_id}"),!', "PROVIDER_EXPORT="))
            observed["checks"] = validate(observed, require_failure=args.require_failure)
            artifact["cases"].append(observed)
            print(f"case={case_id} provider_messages={len(observed['provider_messages'])} passed={all(observed['checks'].values())}")
        artifact["passed"] = bool(artifact["cases"]) and all(all(case["checks"].values()) for case in artifact["cases"])
        return 0 if artifact["passed"] else 1
    except Exception as error:
        artifact["error"] = str(error) if isinstance(error, ValueError) else type(error).__name__
        print("FAILED: " + artifact["error"], file=sys.stderr)
        return 1
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
        print(f"Redacted native provider evidence: {args.output}")


if __name__ == "__main__":
    raise SystemExit(main())
