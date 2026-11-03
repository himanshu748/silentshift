#!/usr/bin/env python3
"""Seed native local vectors, or inspect already executed precedent retrieval.

--seed requires --allow-local-embedding-calls and only indexes eligible native
sources. --inspect-case is strictly read-only: it never seeds, compiles, embeds,
starts a production, or invokes an LLM. Case exports contain bounded context and
native header metadata, never raw payloads, prompts, replies, or credentials.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from bootstrap import read_env
from verify_native import Client, native_build
from verify_native_trace import native

ROOT = Path(__file__).resolve().parents[1]
TOOL_NAMES = {
    "message": "GetCurrentMessage",
    "contracts": "GetApprovedContracts",
    "related": "GetRelatedRecords",
    "precedents": "find_similar_precedents",
}
MATCH_TEXT = {"precedent_id": 80, "source_id": 160, "source_type": 24,
              "contract_id": 160, "kind": 20, "summary": 400, "outcome": 40}
REPORT_NUMBERS = (
    "eligible_sources", "written", "unchanged", "local_embedding_requests",
    "scanned_cases", "case_limit",
)


def integer(value: object, minimum: int = 0) -> bool:
    return type(value) is int and value >= minimum


def score(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and -1 <= value <= 1


def text(value: object, limit: int) -> bool:
    return isinstance(value, str) and 0 < len(value) <= limit


def bounded(value: object, limit: int) -> str | None:
    return value[:limit] if isinstance(value, str) else None


def headers_for(args: argparse.Namespace, case_id: str, trace_id: object) -> list[dict]:
    trace = str(trace_id)
    if not re.fullmatch(r"[1-9][0-9]{0,17}", trace):
        raise ValueError("PRECEDENT_NATIVE_SESSION_REQUIRED")
    # Only metadata is selected. Opening a typed request reads its fixed case
    # association and Action; no request/reply content is exported. Filtering
    # Action below distinguishes retrieval from asynchronous history indexing.
    commands = f'''set headers=[],statement=##class(%SQL.Statement).%New()
set sc=statement.%Prepare("SELECT TOP 32 ID,Type,SessionId,CorrespondingMessageId,SourceConfigName,TargetConfigName,MessageBodyClassName,MessageBodyId,TimeCreated FROM Ens.MessageHeader WHERE SessionId=? AND ((SourceConfigName='Semantic' AND TargetConfigName='Precedents') OR (SourceConfigName='Precedents' AND TargetConfigName='Semantic')) ORDER BY ID")
if $SYSTEM.Status.IsOK(sc) {{
 set rows=statement.%Execute({trace})
 if rows.%SQLCODE>=0 {{
  while rows.%Next() {{
   set item={{"id":(rows.%Get("ID")),"type":(rows.%Get("Type")),"session_id":(rows.%Get("SessionId")),"corresponding_message_id":(rows.%Get("CorrespondingMessageId")),"source":(rows.%Get("SourceConfigName")),"target":(rows.%Get("TargetConfigName")),"body_class":(rows.%Get("MessageBodyClassName")),"body_id":(rows.%Get("MessageBodyId")),"created_at":(rows.%Get("TimeCreated"))}}
   if rows.%Get("MessageBodyClassName")="SilentShift.Message" {{
    set message=##class(SilentShift.Message).%OpenId(rows.%Get("MessageBodyId"))
    if $isobject(message) {{ do item.%Set("request_case_id",message.CaseId),item.%Set("request_action",message.Action) }}
   }}
   do headers.%Push(item)
  }}
  write "PRECEDENT_HEADERS=",headers.%ToJSON(),!
 }}
}}'''
    # Terminal ObjectScript blocks stay on one command line; unlike class
    # methods, interactive session input must not rely on multiline parsing.
    commands = " ".join(line.strip() for line in commands.splitlines())
    result = json.loads(native(args, commands, "PRECEDENT_HEADERS="))
    if not isinstance(result, list):
        raise ValueError("PRECEDENT_HEADER_CONTRACT_FAILED")
    return result


def validate(case: dict, headers: list[dict]) -> dict[str, bool]:
    context = case.get("precedent_context") or {}
    matches = context.get("matches") if isinstance(context.get("matches"), list) else []
    message, agent, policy = case.get("message") or {}, case.get("agent") or {}, case.get("policy") or {}
    reads = agent.get("tool_reads") or {}
    events = case.get("events") or []
    kinds = [event.get("kind") for event in events]
    retrieved = [i for i, kind in enumerate(kinds) if kind == "precedents_retrieved"]
    invoked = [i for i, kind in enumerate(kinds) if kind == "agent_invoked"]
    tool_audits = [event for event in events if event.get("kind") == "agent_tool_read" and (event.get("detail") or {}).get("tool") == "find_similar_precedents"]
    source_types = {"resolved_case", "approved_amendment"}
    requests = [header for header in headers if header.get("type") == 1 and header.get("source") == "Semantic" and header.get("target") == "Precedents" and header.get("request_action") == "process" and header.get("request_case_id") == case.get("id")]
    responses = [header for header in headers if header.get("type") == 2 and header.get("source") == "Precedents" and header.get("target") == "Semantic"]
    paired = any(str(response.get("corresponding_message_id")) == str(request.get("id")) and str(request.get("corresponding_message_id")) == str(response.get("id")) for request in requests for response in responses)
    critical = (case.get("assessment") or {}).get("critical") is True
    checks = {
        "native_local_vector_context": context.get("status") == "retrieved" and context.get("implementation") == "IRIS VECTOR_COSINE" and context.get("model") == "all-minilm:22m" and context.get("dimensions") == 384,
        "context_bound_to_current_case": context.get("case_id") == case.get("id"),
        "one_to_three_actual_matches": 1 <= len(matches) <= 3,
        "bounded_unique_ids_and_summaries": bool(matches) and all(text(match.get("precedent_id"), 80) and text(match.get("source_id"), 160) and text(match.get("summary"), 400) and text(match.get("outcome"), 40) for match in matches) and len({match.get("precedent_id") for match in matches}) == len(matches),
        "finite_descending_cosine_scores": bool(matches) and all(score(match.get("similarity")) for match in matches) and all(matches[i]["similarity"] >= matches[i + 1]["similarity"] for i in range(len(matches) - 1)),
        "case_scoped_source_types": bool(matches) and message.get("kind") in {"order", "payment"} and text(message.get("contract_id"), 160) and all(match.get("source_type") in source_types and match.get("contract_id") == message.get("contract_id") and match.get("kind") == message.get("kind") and (match.get("source_type") != "resolved_case" or match.get("source_id") != case.get("id")) for match in matches),
        "precedents_never_release_authority": context.get("decision_authority") is False and bool(matches) and all(match.get("decision_authority") is False for match in matches),
        "honest_synthetic_labels": bool(matches) and all(match.get("synthetic") is None or type(match.get("synthetic")) is bool for match in matches),
        "returned_native_local_agent": agent.get("mode") == "native-ai-hub" and agent.get("status") == "returned" and agent.get("model") == "qwen3-silentshift:4b-instruct",
        "four_actual_tool_reads": all(integer(reads.get(name), 1) for name in TOOL_NAMES),
        "actual_precedent_tool_audit": bool(tool_audits) and all((event.get("detail") or {}).get("decision_authority") is False and (event.get("detail") or {}).get("status") == "retrieved" and (event.get("detail") or {}).get("record_count") == len(matches) for event in tool_audits),
        "retrieval_before_native_investigation": bool(retrieved) and bool(invoked) and max(retrieved) < min(invoked),
        "known_four_tool_prompt": agent.get("prompt_version") in {"silentshift-investigator/1.3.0", "silentshift-investigator/1.3.1"},
        "actual_native_retrieval_request_and_response": bool(requests) and paired and all(str(header.get("session_id")) == str(case.get("trace_id")) for header in headers),
        "critical_contradictions_stay_held": not critical or case.get("routing") == "QUARANTINED" and case.get("delivery_count") == 0 and policy.get("downstream_permitted") is False,
    }
    return checks


def redacted_case(case: dict, headers: list[dict], checks: dict[str, bool]) -> dict:
    context, agent = case.get("precedent_context") or {}, case.get("agent") or {}
    matches = []
    for match in context.get("matches", [])[:3]:
        item = {field: bounded(match.get(field), limit) for field, limit in MATCH_TEXT.items()}
        item.update(similarity=match.get("similarity") if score(match.get("similarity")) else None,
                    synthetic=match.get("synthetic") if type(match.get("synthetic")) is bool else None,
                    decision_authority=match.get("decision_authority") if type(match.get("decision_authority")) is bool else None)
        matches.append(item)
    critical = (case.get("assessment") or {}).get("critical") is True
    misleading = [match["precedent_id"] for match in matches if match.get("source_type") == "resolved_case" and match.get("outcome") == "DELIVERED"]
    return {
        "case_id": case.get("id"), "scenario_id": case.get("scenario_id"), "trace_id": case.get("trace_id"),
        "routing": case.get("routing"), "delivery_count": case.get("delivery_count"), "critical": critical,
        "downstream_permitted": (case.get("policy") or {}).get("downstream_permitted"),
        "context": {key: context.get(key) for key in ("status", "implementation", "case_id", "model", "dimensions", "decision_authority")} | {"matches": matches},
        "agent": {"mode": agent.get("mode"), "status": agent.get("status"), "model": agent.get("model"), "prompt_version": agent.get("prompt_version"), "tool_reads": {key: (agent.get("tool_reads") or {}).get(key) for key in TOOL_NAMES}},
        "native_headers": headers,
        "misleading_past_delivery_precedent_ids": misleading,
        "misleading_past_delivery_containment_observed": bool(misleading) and critical and all(checks.values()),
        "checks": checks,
    }


def seed(args: argparse.Namespace) -> dict:
    commands = f'''set sc=##class(SilentShift.Precedents).Seed(.report,{args.max_cases})
set result={{"ok":false,"report":null}}
do result.%Set("ok",$SYSTEM.Status.IsOK(sc),"boolean")
if $SYSTEM.Status.IsOK(sc),report'="" {{ do result.%Set("report",##class(%DynamicObject).%FromJSON(report)) }}
write "PRECEDENT_SEED=",result.%ToJSON(),!'''
    result = json.loads(native(args, commands, "PRECEDENT_SEED="))
    report = result.get("report") or {}
    parts = {key: report.get(key) or {} for key in ("approved_amendments", "resolved_cases")}
    checks = {
        "native_seed_succeeded": result.get("ok") is True,
        "local_model_and_native_dimensions": report.get("status") == "indexed" and report.get("model") == "all-minilm:22m" and report.get("dimensions") == 384 and report.get("decision_authority") is False,
        "both_source_types_indexed": all(integer(part.get("eligible_sources"), 1) for part in parts.values()),
        "native_source_accounting": all(part.get("status") == "indexed" and part.get("model") == "all-minilm:22m" and part.get("dimensions") == 384 and part.get("decision_authority") is False and all(integer(part.get(key)) for key in ("eligible_sources", "written", "unchanged", "local_embedding_requests")) and part["written"] + part["unchanged"] == part["eligible_sources"] for part in parts.values()),
    }
    redacted = {"status": report.get("status"), "model": report.get("model"), "dimensions": report.get("dimensions"), "decision_authority": report.get("decision_authority")}
    for key, part in parts.items():
        redacted[key] = {field: part.get(field) for field in ("status", "model", "dimensions", "decision_authority", *REPORT_NUMBERS) if field in part}
    return {"report": redacted, "checks": checks, "passed": all(checks.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--context")
    parser.add_argument("--container")
    parser.add_argument("--api")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--seed", action="store_true")
    mode.add_argument("--inspect-case", action="append", default=[], help="Repeat for existing cases; strictly read-only")
    parser.add_argument("--allow-local-embedding-calls", action="store_true")
    parser.add_argument("--max-cases", type=int, default=100, help="Bound resolved history indexing to1..100 cases")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/precedents.json")
    args = parser.parse_args()
    if args.seed and not args.allow_local_embedding_calls:
        parser.error("--seed requires --allow-local-embedding-calls; no local model was invoked")
    if not 1 <= args.max_cases <= 100:
        parser.error("--max-cases must be between1 and100")
    artifact = {
        "created_at": datetime.now(timezone.utc).isoformat(), "mode": "seed" if args.seed else "read-only-inspection",
        "llm_calls": 0, "cases": [], "passed": False,
        "limits": ["Local synthetic source evidence, not a relevance benchmark or an award claim.", "Seeding alone does not prove production retrieval or a fourth agent tool read.", "Missing past delivered matches do not establish the misleading-precedent containment demonstration."],
    }
    try:
        args.runtime_env = read_env(args.env_file)
        args.context = args.context or args.runtime_env.get("DOCKER_CONTEXT")
        args.container = args.container or args.runtime_env.get("COMPOSE_PROJECT_NAME", ROOT.name.lower()) + "-iris-1"
        args.api = args.api or args.runtime_env.get("SILENTSHIFT_API_URL", "http://127.0.0.1:52773/silentshift/api")
        if args.seed:
            artifact["seed"] = seed(args)
            artifact["passed"] = artifact["seed"]["passed"]
        else:
            if urlparse(args.api).hostname not in {"127.0.0.1", "localhost", "::1"}:
                raise ValueError("PRECEDENT_INSPECTION_REQUIRES_LOCAL_API")
            client = Client(args.api, args.runtime_env["SILENTSHIFT_VIEWER_USERNAME"], args.runtime_env["SILENTSHIFT_VIEWER_PASSWORD"])
            status, health = client.call("/health")
            if status != 200 or not isinstance(health, dict) or not native_build(health.get("build")) or health.get("production", {}).get("running") is not True:
                raise ValueError("PRECEDENT_LIVE_BUILD154_REQUIRED")
            artifact["iris_version"] = health["build"]
            for case_id in args.inspect_case:
                if not re.fullmatch(r"[A-Fa-f0-9-]{36}", case_id):
                    raise ValueError("PRECEDENT_CASE_IDENTIFIER_INVALID")
                status, case = client.call("/cases/" + case_id)
                if status != 200 or not isinstance(case, dict) or case.get("id") != case_id:
                    raise ValueError("PRECEDENT_PERSISTED_CASE_UNAVAILABLE")
                headers = headers_for(args, case_id, case.get("trace_id"))
                checks = validate(case, headers)
                artifact["cases"].append(redacted_case(case, headers, checks))
                print(f"case={case_id} trace={case.get('trace_id')} matches={len((case.get('precedent_context') or {}).get('matches', []))} passed={all(checks.values())}")
            artifact["passed"] = bool(artifact["cases"]) and all(all(case["checks"].values()) for case in artifact["cases"])
        return 0 if artifact["passed"] else 1
    except Exception as error:
        artifact["error"] = "PRECEDENT_JSON_CONTRACT_INVALID" if isinstance(error, json.JSONDecodeError) else str(error) if isinstance(error, ValueError) else type(error).__name__
        print("FAILED: " + artifact["error"], file=sys.stderr)
        return 1
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
        print(f"Redacted native precedent evidence: {args.output}")


if __name__ == "__main__":
    raise SystemExit(main())
