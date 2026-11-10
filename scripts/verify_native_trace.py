#!/usr/bin/env python3
"""Verify real native invocation/tool traces with TWO local model runs.

Creates fresh C/A scenario cases and one isolated evidence-budget failure case.
Existing benchmark cases remain untouched. Export contains metadata only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError

from bootstrap import read_env
from verify_native import Client, native_build

ROOT = Path(__file__).resolve().parents[1]


def native(args: argparse.Namespace, commands: str, marker: str) -> str:
    docker = ["docker"] + (["--context", args.context] if args.context else [])
    process = subprocess.run(
        docker + ["exec", "-i", args.container,
         "iris", "session", "IRIS", "-U", "SILENTSHIFT"],
        input=commands + "\nhalt\n", text=True, capture_output=True,
        timeout=30, check=False, env=args.runtime_env,
    )
    values = [line[len(marker):] for line in process.stdout.splitlines() if line.startswith(marker)]
    if process.returncode or len(values) != 1:
        raise ValueError("Native trace command failed; raw terminal diagnostics withheld")
    return values[0]


def inspect(args: argparse.Namespace, case_id: str) -> dict:
    if not re.fullmatch(r"[A-Fa-f0-9-]{36}", case_id):
        raise ValueError("Invalid native case identifier")
    statement = f'write "TRACE_EXPORT=",##class(SilentShift.Test.TraceChecks).InspectCase("{case_id}"),!'
    observed = {}
    for _ in range(20):
        observed = json.loads(native(args, statement, "TRACE_EXPORT="))
        expected = (observed.get("agent", {}).get("trace") or {}).get("enqueued_events", -1)
        if len(observed.get("trace_payloads", [])) == expected and observed.get("trace_audit_count") == expected:
            break
        time.sleep(0.25)
    return observed


def validate(observed: dict, *, budget: bool = False) -> dict[str, bool]:
    agent = observed["agent"]
    tracing = agent.get("trace") or {}
    spans = observed["trace_payloads"]
    headers = observed["native_headers"]
    trace_id = str(observed["trace_id"])
    invocation_id = tracing.get("invocation_id")
    trace_headers = [h for h in headers if h["body_class"] == "SilentShift.TraceEvent"]
    audits = observed["trace_audits"]
    tools = ("GetCurrentMessage", "GetApprovedContracts", "GetRelatedRecords")
    if agent.get("prompt_version") in {"silentshift-investigator/1.3.0", "silentshift-investigator/1.3.1"}:
        tools += ("find_similar_precedents",)
    expected_minimum = 1 if budget else 2 + 2 * len(tools)
    terminal_kind = "invocation_skipped" if budget else "invocation_completed"
    terminal = [s for s in spans if s["event_kind"] == terminal_kind]
    checks = {
        "native_partner_semantic_chain": any(h["source"] == "Partner" and h["target"] == "Semantic" for h in headers),
        "native_investigator_chain": any(h["source"] == "Semantic" and h["target"] == "Investigator" for h in headers),
        "native_trace_header_count": len(trace_headers) == len(spans) == len(audits) == tracing.get("enqueued_events") and len(spans) >= expected_minimum,
        "native_trace_header_association": bool(trace_headers) and all(h["source"] == "Investigator" and h["target"] == "AITrace" and str(h["session_id"]) == trace_id for h in trace_headers),
        "audit_header_association": {a["message_header_id"] for a in audits} == {h["id"] for h in trace_headers},
        "case_and_invocation_association": bool(spans) and all(s["case_id"] == observed["case_id"] and str(s["production_session_id"]) == trace_id and (s["span_id"] == invocation_id or s["parent_span_id"] == invocation_id) for s in spans),
        "no_capture_or_enqueue_failures": tracing.get("enqueue_failures") == 0 and tracing.get("capture_failures") == 0,
        "known_granularity_and_prompt_version": bool(spans) and agent.get("prompt_version") in {"silentshift-investigator/1.0.0", "silentshift-investigator/1.1.0", "silentshift-investigator/1.2.0", "silentshift-investigator/1.3.0", "silentshift-investigator/1.3.1"} and all(s["granularity"] == "agent_invocation_and_tool" and s["prompt_version"] == agent["prompt_version"] for s in spans),
        "honest_usage_retry_fallback_fields": bool(spans) and all(s["usage_scope"] == "final_response_only" and s["session_totals"] is None and s["provider_round_usage"] is None and s["provider_round_count"] is None and s["provider_retry_count"] is None and s["billing_cost"] is None and s["application_retry_count"] == 0 and s["fallback_used"] is False for s in spans),
        "bounded_metadata_without_content": bool(spans) and all(len(json.dumps(s).encode()) <= 8192 and s["content_retained"] is False and not ({"prompt", "arguments", "content", "api_key", "raw_response"} & s.keys()) for s in spans),
        "one_terminal_invocation": len(terminal) == 1,
    }
    if budget:
        checks.update({
            "pre_model_failure_visible": len(terminal) == 1 and terminal[0]["failure_code"] == "EVIDENCE_REFERENCE_LIMIT" and terminal[0]["model_invoked"] is False,
            "no_tool_or_invocation_start": all(s["span_kind"] != "tool" and s["event_kind"] != "invocation_started" for s in spans),
            "held_without_delivery": observed["routing"] == "REVIEW" and observed["delivery_count"] == 0,
        })
    else:
        starts = [s for s in spans if s["event_kind"] == "invocation_started"]
        completed = [s for s in spans if s["event_kind"] == "tool_completed"]
        checks.update({
            "actual_native_chat_returned": len(starts) == 1 and len(terminal) == 1 and terminal[0]["native_chat_returned"] is True and terminal[0]["model_invoked"] is True and agent["status"] == "returned",
            "all_required_tool_spans": all(any(s["tool_name"] == name and s["status"] == "completed" for s in completed) for name in tools),
            "paired_actual_tool_spans": all(sum(s["span_id"] == t["span_id"] and s["event_kind"] == "tool_started" for s in spans) == 1 and t["duration_ms"] is not None and t["duration_ms"] >= 0 and bool(t["started_at"]) and bool(t["finished_at"]) for t in completed),
            "final_usage_matches_sdk_response": len(terminal) == 1 and terminal[0]["final_response_usage"] == agent.get("response_usage") and terminal[0]["duration_ms"] is not None,
        })
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--context", help="Docker context; defaults to DOCKER_CONTEXT/current context")
    parser.add_argument("--container", help="Defaults to COMPOSE_PROJECT_NAME (or repository name) + -iris-1")
    parser.add_argument("--api", help="Defaults to SILENTSHIFT_API_URL or the local52773 API")
    parser.add_argument("--allow-local-model-calls", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/traceability.json")
    parser.add_argument("--inspect-case", help="Read-only export/validation of an existing case; never runs a model")
    args = parser.parse_args()
    artifact = {"created_at": datetime.now(timezone.utc).isoformat(), "granularity": "agent_invocation_and_tool", "provider_round_coverage": False, "cases": [], "passed": False}
    try:
        env = read_env(args.env_file)
        args.runtime_env = env
        args.context = args.context or env.get("DOCKER_CONTEXT")
        project = env.get("COMPOSE_PROJECT_NAME", ROOT.name.lower())
        args.container = args.container or f"{project}-iris-1"
        args.api = args.api or env.get("SILENTSHIFT_API_URL", "http://127.0.0.1:52773/silentshift/api")
        if args.inspect_case:
            present = native(args, 'write "TRACE_PRESENT=",##class(%Dictionary.CompiledClass).%ExistsId("SilentShift.Test.TraceChecks"),!', "TRACE_PRESENT=")
            if present != "1":
                raise ValueError("TraceChecks must already be compiled before read-only inspection")
            observed = inspect(args, args.inspect_case)
            observed["checks"] = validate(observed, budget=observed["agent"].get("model_invoked") is False)
            artifact["cases"].append(observed)
        else:
            if not args.allow_local_model_calls:
                print("Use --allow-local-model-calls to compile the test class and run two fresh synthetic investigations.")
                return 2
            compiled = native(args, 'set sc=$SYSTEM.OBJ.Load("/opt/silentshift/tests/iris/TraceChecks.cls","ck")\nwrite "TRACE_COMPILED=",$SYSTEM.Status.IsOK(sc),!', "TRACE_COMPILED=")
            if compiled != "1":
                raise ValueError("Native trace test class failed compilation")
            safe = native(args, 'write "TRACE_LOCAL=",##class(SilentShift.Test.TraceChecks).LocalRouteSafe(),!', "TRACE_LOCAL=")
            if safe != "1":
                raise ValueError("Actual container route is not explicit local Qwen/Ollama11434")
            client = Client(args.api, env["SILENTSHIFT_IRIS_USERNAME"], env["SILENTSHIFT_IRIS_PASSWORD"])
            status, health = client.call("/health")
            if status != 200 or not native_build(health.get("build")) or health.get("production", {}).get("running") is not True:
                raise ValueError("Actual native154 production is unavailable")
            artifact["run_id"] = str(uuid.uuid4())
            for scenario, route, count in (("approved-amendment", "DELIVERED", 1), ("quantity-mismatch", "QUARANTINED", 0)):
                status, record = client.call(f"/scenarios/{scenario}/run", {"run_id": artifact["run_id"]})
                if status != 200 or not isinstance(record, dict):
                    raise ValueError(f"Scenario failed (HTTP{status}); remaining model calls stopped")
                observed = inspect(args, str(record["id"]))
                checks = validate(observed)
                checks["expected_route_and_receipt"] = observed["routing"] == route and observed["delivery_count"] == count
                observed["checks"] = checks
                artifact["cases"].append(observed)
                print(f"{scenario}: trace={observed['trace_id']} headers={len(observed['trace_payloads'])} route={observed['routing']} passed={all(checks.values())}")
                if not all(checks.values()):
                    raise ValueError("Native trace assertions failed; remaining model calls stopped")
            budget_id = native(args, 'set sc=##class(SilentShift.Test.TraceChecks).RunBudgetCase(.id)\nif $SYSTEM.Status.IsOK(sc) write "TRACE_BUDGET_ID=",id,!', "TRACE_BUDGET_ID=")
            observed = inspect(args, budget_id)
            observed["checks"] = validate(observed, budget=True)
            artifact["cases"].append(observed)
        artifact["passed"] = bool(artifact["cases"]) and all(all(c["checks"].values()) for c in artifact["cases"])
        return 0 if artifact["passed"] else 1
    except (ValueError, KeyError, TypeError, OSError, URLError, TimeoutError, subprocess.TimeoutExpired) as error:
        artifact["error"] = str(error) if isinstance(error, ValueError) else type(error).__name__
        print("FAILED: " + artifact["error"], file=sys.stderr)
        return 1
    finally:
        if artifact["cases"] or artifact.get("error"):
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
            print(f"Redacted native evidence: {args.output}")


if __name__ == "__main__":
    raise SystemExit(main())
