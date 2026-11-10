#!/usr/bin/env python3
"""Seed/query real local embeddings in IRIS, or inspect a persisted case read-only.

Procedures supplement approved contracts; they never authorize delivery. The
six authored retrieval probes are not a general relevance benchmark.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bootstrap import read_env
from verify_native import Client
from verify_native_trace import native

ROOT = Path(__file__).resolve().parents[1]
PROBES = (
    ("quantity unit CASE EA conversion approved amendment", "runbook:units:v1"),
    ("payment amount currency decimal scale minor units", "runbook:money:v1"),
    ("approved contract amendment supersedes effective dates", "runbook:amendment:v1"),
    ("conflicting peer evidence missing approved authority human review", "runbook:authority:v1"),
    ("event time contract effective expiry timestamp", "runbook:time:v1"),
    ("unrelated beach holiday weather forecast", None),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--context")
    parser.add_argument("--container")
    parser.add_argument("--api")
    parser.add_argument("--allow-local-embedding-calls", action="store_true")
    parser.add_argument("--inspect-case", help="Inspect existing context only; no seed, query or model call")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/runbooks.json")
    args = parser.parse_args()
    artifact = {"created_at": datetime.now(timezone.utc).isoformat(), "passed": False,
                "decision_authority": False, "probes": [], "embedding_calls": 0}
    try:
        env = read_env(args.env_file)
        args.runtime_env = env
        args.context = args.context or env.get("DOCKER_CONTEXT")
        args.container = args.container or env.get("COMPOSE_PROJECT_NAME", ROOT.name.lower()) + "-iris-1"
        args.api = args.api or env.get("SILENTSHIFT_API_URL", "http://127.0.0.1:52773/silentshift/api")
        if args.inspect_case:
            if not re.fullmatch(r"[A-Fa-f0-9-]{36}", args.inspect_case):
                raise ValueError("Invalid case identifier")
            client = Client(args.api, env["SILENTSHIFT_VIEWER_USERNAME"], env["SILENTSHIFT_VIEWER_PASSWORD"])
            status, case = client.call("/cases/" + args.inspect_case)
            if status != 200 or not isinstance(case, dict):
                raise ValueError("Persisted case was unavailable")
            context, agent = case.get("runbook_context") or {}, case.get("agent") or {}
            kinds = [event["kind"] for event in case.get("events", [])]
            checks = {
                "native_vector_context": context.get("status") == "retrieved" and context.get("implementation") == "IRIS VECTOR_COSINE" and context.get("dimensions") == 384,
                "context_never_authority": context.get("decision_authority") is False and all(m.get("decision_authority") is False for m in context.get("matches", [])),
                "native_agent_read_related": agent.get("status") == "returned" and (agent.get("tool_reads") or {}).get("related", 0) >= 1,
                "retrieval_before_investigation": "runbook_retrieved" in kinds and "agent_invoked" in kinds and kinds.index("runbook_retrieved") < kinds.index("agent_invoked"),
                "known_prompt": agent.get("prompt_version") in {"silentshift-investigator/1.1.0", "silentshift-investigator/1.2.0", "silentshift-investigator/1.3.0", "silentshift-investigator/1.3.1"},
            }
            artifact["case"] = {"id": case["id"], "trace_id": case.get("trace_id"), "routing": case.get("routing"),
                                "delivery_count": case.get("delivery_count"), "context": context,
                                "prompt_version": agent.get("prompt_version"), "tool_reads": agent.get("tool_reads"), "checks": checks}
            artifact["passed"] = all(checks.values())
        else:
            if not args.allow_local_embedding_calls:
                print("Use --allow-local-embedding-calls to seed five procedures and run six native queries; no LLM investigations are created.")
                return 2
            seeded = native(args, 'set sc=##class(SilentShift.Runbooks).Seed()\nwrite "RUNBOOK_SEEDED=",$SYSTEM.Status.IsOK(sc),!', "RUNBOOK_SEEDED=")
            artifact["embedding_calls"] += 1
            if seeded != "1":
                raise ValueError("Native runbook seed failed")
            for query, expected in PROBES:
                # Probe strings are fixed source literals, never user input.
                result = json.loads(native(args, 'write "RUNBOOK_QUERY=",##class(SilentShift.Runbooks).Search("' + query + '"),!', "RUNBOOK_QUERY="))
                artifact["embedding_calls"] += 1
                matches = result.get("matches", [])
                passed = (matches[0]["id"] == expected if expected else not matches)
                artifact["probes"].append({"query": query, "expected_first": expected, "result": result, "passed": passed})
            artifact["passed"] = all(p["passed"] for p in artifact["probes"])
        return 0 if artifact["passed"] else 1
    except Exception as error:
        artifact["error"] = str(error) if isinstance(error, ValueError) else type(error).__name__
        print("FAILED: " + artifact["error"], file=sys.stderr)
        return 1
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
