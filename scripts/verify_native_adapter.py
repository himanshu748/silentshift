#!/usr/bin/env python3
"""Prove the production partner-file adapter with at most TWO local model cases.

Operator setup (central bootstrap/compose owns this wiring):
  * mount .local/partner-inbox RW at /var/opt/silentshift/partner-inbox;
  * allow only the trusted operator and container irisowner to write that inbox;
  * enable PartnerFiles (SilentShift.Service.PartnerFiles), CallInterval=1;
  * set SILENTSHIFT_PARTNER_FILES_ENABLED=1 (default is 0).

Partner usage: write UTF-8 MESSAGE JSON to <name>.json.part, close it, then
atomically rename to <name>.json.ready on the SAME filesystem. Basenames use
1-80 ASCII letters/digits/hyphens/underscores, starting with a letter/digit.
The adapter claims .work, keeps exact original bytes in .done/.hold, and writes
<name>.json.ack.json atomically only from a persisted terminal outcome. Acks
contain hashes, native trace/policy and the included IRIS simulator receipt.
They are not proof of delivery to an external partner. No input/archive is deleted.

Three unexpected failures hold .work for an operator, with durable error state.
After repairing a transient ack/path problem, an operator may call the test
helper ResumeHeld(name); it only clears the retry hold and never dispatches.
DISPATCH_UNCERTAIN requires native-header/operator investigation, never automatic
redispatch. Existing jobs keep running even when acknowledgment writing fails.
An outcome still PROCESSING after ten minutes produces OPERATOR_HOLD, not a
completion claim; the queued job is preserved for native operator recovery.
Keep fewer than 256 active files per suffix; archive retention is operator-owned.

This driver writes ONLY uniquely named synthetic files in .local/partner-inbox.
If the model requests review of the CLEAR test order, it approves that isolated
native task only after validating the current deterministic assessment and all
four actual evidence reads. This is review test coverage, not an AI release.
It never changes production configuration, compiles classes, deletes case data,
calls an external provider, or retries a new model case after a failed assertion.
Read-only --inspect-file exports existing adapter state and never submits data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from bootstrap import read_env
from verify_native import Client, native_build

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / ".local" / "partner-inbox"
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")


def native(args: argparse.Namespace, command: str, marker: str) -> str:
    docker = ["docker"] + (["--context", args.context] if args.context else [])
    result = subprocess.run(
        docker + ["exec", "-i", args.container, "iris", "session", "IRIS", "-U", "SILENTSHIFT"],
        input=command + "\nhalt\n", text=True, capture_output=True,
        timeout=30, check=False, env=args.runtime_env,
    )
    lines = [line[len(marker):] for line in result.stdout.splitlines() if line.startswith(marker)]
    if result.returncode or len(lines) != 1:
        raise ValueError("Native adapter inspection failed; terminal diagnostics withheld")
    return lines[0]


def inspect(args: argparse.Namespace, name: str) -> dict:
    if not NAME.fullmatch(name):
        raise ValueError("Unsafe synthetic basename")
    return json.loads(native(args, f'write "ADAPTER_STATE=",##class(SilentShift.Test.AdapterChecks).Inspect("{name}"),!', "ADAPTER_STATE="))


def wait_for(predicate, description: str, *, seconds: float = 180):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(0.3)
    raise ValueError("Timed out waiting for " + description)


def path(name: str, suffix: str) -> Path:
    if not NAME.fullmatch(name):
        raise ValueError("Unsafe synthetic basename")
    return INBOX / (name + ".json" + suffix)


def submit(name: str, raw: bytes) -> None:
    temporary, ready = path(name, ".part"), path(name, ".ready")
    if temporary.exists() or ready.exists() or ready.is_symlink():
        raise ValueError("Synthetic ready-file collision")
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.chmod(0o660)
    os.replace(temporary, ready)


def acknowledgment(name: str) -> dict | None:
    target = path(name, ".ack.json")
    if not target.is_file() or target.is_symlink():
        return None
    return json.loads(target.read_text(encoding="utf-8"))


def record(client: Client, case_id: str) -> dict:
    status, item = client.call("/cases/" + case_id)
    if status != 200 or not isinstance(item, dict):
        raise ValueError("Persisted file case could not be read")
    return item


def verify_case(args, client, name: str, raw: bytes, route: str, count: int, *, ack_snapshot: dict | None = None) -> dict:
    ack = wait_for(lambda: acknowledgment(name), "actual outcome acknowledgment")
    wait_for(lambda: path(name, ".done").is_file(), "retained original")
    state = inspect(args, name)
    item = record(client, ack["case_id"])
    headers = state["headers"]
    digest = hashlib.sha256(raw).hexdigest()
    ack_route = ack_snapshot["routing"] if ack_snapshot else route
    ack_count = ack_snapshot["delivery_count"] if ack_snapshot else count
    ack_policy = "REQUEST_REVIEW" if ack_snapshot and ack_route == "REVIEW" else item["policy"]["decision"]
    checks = {
        "one_actual_adapter_dispatch": sum(h["source"] == "PartnerFiles" and h["target"] == "Semantic" for h in headers) == 1,
        "one_actual_native_investigation": sum(h["source"] == "Semantic" and h["target"] == "Investigator" for h in headers) == 1,
        "model_returned_four_reads": item["agent"]["mode"] == "native-ai-hub" and item["agent"]["status"] == "returned" and all(item["agent"]["tool_reads"].get(k, 0) >= 1 for k in ("message", "contracts", "related", "precedents")),
        "native_precedent_retrieval": any(h["source"] == "Semantic" and h["target"] == "Precedents" for h in headers),
        "precedents_have_no_release_authority": (item.get("precedent_context") or {}).get("decision_authority") is False,
        "expected_persisted_outcome": item["routing"] == route and item["delivery_count"] == count,
        "immutable_ack_matches_observed_outcome": ack["routing"] == ack_route and ack["delivery_count"] == ack_count,
        "actual_trace_association": bool(item["trace_id"]) and str(item["trace_id"]) == str(ack["trace_id"]) == str(state["trace_id"]),
        "raw_bytes_retained": path(name, ".done").read_bytes() == raw and item["raw_payload"].encode() == raw,
        "byte_count_and_digest": ack["input_sha256"] == state["input_sha256"] == digest and ack["input_bytes"] == state["input_bytes"] == len(raw),
        "general_catalog_server_clock": state["scenario_id"] == "" and state["clock"] == state["received_at"] and state["reference_count"] >= 1,
        "ack_matches_policy": ack["status"] == "COMPLETED" and ack["policy_decision"] == ack_policy,
        "receipt_truthful": (ack["delivery_receipt"] is None if ack_count == 0 else isinstance(ack["delivery_receipt"], dict) and ack["delivery_receipt"]["case_id"] == item["id"] and ack["delivery_receipt"]["destination"] == "included-iris-simulator"),
        "ack_completion_not_still_held": state["completed"] is True and state["held"] is False,
    }
    # Export only scoped metadata, never original partner data, prompts or responses.
    context = item.get("runbook_context") or {}
    supporting = {"status": context.get("status"), "implementation": context.get("implementation"), "model": context.get("model"), "dimensions": context.get("dimensions"), "match_count": len(context.get("matches") or []), "decision_authority": context.get("decision_authority")}
    precedents = item.get("precedent_context") or {}
    precedent_metadata = {"status": precedents.get("status"), "model": precedents.get("model"), "dimensions": precedents.get("dimensions"), "match_count": len(precedents.get("matches") or []), "decision_authority": precedents.get("decision_authority")}
    return {"file": name, "case_id": item["id"], "trace_id": item["trace_id"], "routing": item["routing"], "ack": ack, "native_state": state, "runbook_context": supporting, "precedent_context": precedent_metadata, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--context")
    parser.add_argument("--container")
    parser.add_argument("--allow-local-model-calls", action="store_true", help="Authorize exactly two new synthetic local model cases")
    parser.add_argument("--resume-run", type=Path, help="Resume this driver's failed first ack test without another first case; requires local-model opt-in for the second case")
    parser.add_argument("--inspect-file", help="Read existing state only; no compilation, input writes or model calls")
    parser.add_argument("--output", type=Path, help="Defaults to adapter.json for a live run; separate contracts/inspection artifacts otherwise")
    args = parser.parse_args()
    mode = "inspection" if args.inspect_file else "live" if args.allow_local_model_calls else "contracts"
    args.output = args.output or ROOT / "evidence/native" / ("adapter.json" if mode == "live" else "adapter-" + mode + ".json")
    artifact = {"suite": "native-partner-adapter/1", "mode": mode, "created_at": datetime.now(timezone.utc).isoformat(), "new_model_cases_requested": 0, "synthetic": True, "cases": [], "checks": {}, "passed": False}
    try:
        env = read_env(args.env_file)
        args.runtime_env = env
        args.context = args.context or env.get("DOCKER_CONTEXT")
        args.container = args.container or env.get("COMPOSE_PROJECT_NAME", ROOT.name.lower()) + "-iris-1"
        present = native(args, 'write "ADAPTER_CHECKS=",##class(%Dictionary.CompiledClass).%ExistsId("SilentShift.Test.AdapterChecks"),!', "ADAPTER_CHECKS=")
        if present != "1":
            raise ValueError("Compile tests/iris/AdapterChecks.cls explicitly before verification")
        contracts = json.loads(native(args, 'write "ADAPTER_CONTRACTS=",##class(SilentShift.Test.AdapterChecks).Contracts().%ToJSON(),!', "ADAPTER_CONTRACTS="))
        artifact["contract_checks"] = contracts
        if not contracts or not all(contracts.values()):
            raise ValueError("Native adapter contract checks failed")
        if args.inspect_file:
            artifact["inspection"] = inspect(args, args.inspect_file)
            artifact["inspection_complete"] = True
            artifact["passed"] = None  # Export success is not a live journey pass.
            return 0
        if not args.allow_local_model_calls:
            print("Native contracts passed. Use --allow-local-model-calls only after coordinated production activation.")
            return 2
        ready = native(args, 'write "ADAPTER_READY=",##class(SilentShift.Test.AdapterChecks).LocalReady(),!', "ADAPTER_READY=")
        if ready != "1":
            raise ValueError("Actual adapter flag/mount/local Qwen route is not ready")
        iterator = json.loads(native(args, 'write "ADAPTER_ITERATOR=",##class(SilentShift.Test.AdapterChecks).IteratorContracts().%ToJSON(),!', "ADAPTER_ITERATOR="))
        artifact["iterator_checks"] = iterator
        if not iterator.get("checks") or not all(iterator["checks"].values()):
            raise ValueError("Native production iterator regression checks failed before model calls")
        if not INBOX.is_dir() or INBOX.is_symlink() or INBOX.resolve() != INBOX:
            raise ValueError("Expected trusted local partner-inbox directory is missing or unsafe")
        client = Client(env.get("SILENTSHIFT_API_URL", "http://127.0.0.1:52773/silentshift/api"), env["SILENTSHIFT_IRIS_USERNAME"], env["SILENTSHIFT_IRIS_PASSWORD"])
        status, health = client.call("/health")
        if status != 200 or not native_build(health.get("build")) or health.get("production", {}).get("running") is not True:
            raise ValueError("Actual native build154 production is unavailable")
        previous = json.loads(args.resume_run.read_text()) if args.resume_run else None
        if previous is not None and (previous.get("passed") is not False or previous.get("new_model_cases_requested") != 1 or previous.get("cases") or not re.fullmatch(r"[a-f0-9]{32}", previous.get("run_id", ""))):
            raise ValueError("Resume requires a failed first-case adapter receipt")
        run_id = previous["run_id"] if previous else uuid.uuid4().hex
        artifact["run_id"] = run_id
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        message = {"event_id": "file-" + run_id, "correlation_id": "file-" + run_id, "source": "silentshift-native-file-test", "kind": "order", "occurred_at": timestamp, "contract_id": "PO-2048", "business_unit": "EU-WEST", "product_id": "P-ALLOY-8", "quantity": "240", "unit": "EA", "notes": "Synthetic native file adapter verification; no external partner delivery."}
        raw = (json.dumps(message, indent=2) + "\n").encode()
        allow = "adapter-" + run_id + "-allow"
        # Deliberate ack-only failure. The only directory removed below is this
        # exact empty synthetic obstruction; production/model jobs remain intact.
        obstruction = path(allow, ".ack.json")
        if previous:
            if previous["ack_failure"]["native_state"]["file"] != allow:
                raise ValueError("Resume filename does not match original run")
            raw = path(allow, ".done" if path(allow, ".done").is_file() else ".work").read_bytes()
            message = json.loads(raw)
            if (hashlib.sha256(raw).hexdigest() != previous["ack_failure"]["native_state"]["input_sha256"] or message.get("event_id") != "file-" + run_id or message.get("source") != "silentshift-native-file-test"):
                raise ValueError("Resume input differs from the driver's original synthetic file")
            artifact["resumed_from"] = {"receipt": args.resume_run.name, "case_id": previous["ack_failure"]["native_state"]["case_id"], "new_first_case_created": False}
            if previous.get("explicit_review"):
                artifact["explicit_review"] = previous["explicit_review"]
        else:
            obstruction.mkdir(mode=0o770)
            submit(allow, raw)
        artifact["new_model_cases_requested"] = 1
        completed = inspect(args, allow) if previous else None
        held = completed if completed and completed["completed"] else wait_for(lambda: (s if (s := inspect(args, allow))["held"] and s["case_id"] else None), "bounded ack failure hold", seconds=150)
        held_case = record(client, held["case_id"])
        artifact["ack_failure"] = previous["ack_failure"] if completed and completed["completed"] else {"native_state": held, "routing": held_case["routing"], "delivery_count": held_case["delivery_count"]}
        if held_case["routing"] == "REVIEW":
            if (held_case.get("assessment", {}).get("classification") != "CLEAR" or held_case["assessment"].get("critical") is not False or held_case.get("agent", {}).get("status") != "returned" or not all(held_case["agent"].get("tool_reads", {}).get(k, 0) >= 1 for k in ("message", "contracts", "related", "precedents"))):
                raise ValueError("Synthetic order is not eligible for the driver's explicit review")
            request = {"action": "APPROVE", "reason": "Synthetic adapter recovery test: current approved contract and CLEAR deterministic assessment match 240 EA; historical concerns confer no authority.", "expected_version": held_case["version"], "idempotency_key": "adapter-review-" + run_id}
            status, _ = client.call("/cases/" + held["case_id"] + "/review", request)
            if status != 200:
                raise ValueError("Native review of the clear synthetic order failed")
            held_case = record(client, held["case_id"])
            artifact["explicit_review"] = {"case_id": held["case_id"], "original_route": "REVIEW", "action": "APPROVE", "http_status": status, "reason": request["reason"], "version_before": request["expected_version"], "version_after": held_case["version"]}
        if held_case["routing"] != "DELIVERED" or held_case["delivery_count"] != 1 or not (path(allow, ".work").is_file() or path(allow, ".done").is_file()):
            raise ValueError("Ack failure did not preserve the completed native job and original")
        if not (completed and completed["completed"]):
            obstruction.rmdir()
            resumed = native(args, f'set sc=##class(SilentShift.Test.AdapterChecks).ResumeHeld("{allow}")\nwrite "ADAPTER_RESUME=",$SYSTEM.Status.IsOK(sc),!', "ADAPTER_RESUME=")
            if resumed != "1":
                raise ValueError("Ack retry hold could not be resumed")
        first = verify_case(args, client, allow, raw, "DELIVERED", 1, ack_snapshot=artifact["ack_failure"] if artifact.get("explicit_review") else None)
        first["checks"]["ack_failure_recovered_same_case"] = first["case_id"] == held["case_id"] and first["trace_id"] == held_case["trace_id"]
        artifact["cases"].append(first)
        if not all(first["checks"].values()):
            raise ValueError("First native adapter case failed; second model case stopped")
        critical = dict(message, event_id="file-critical-" + run_id, correlation_id="file-critical-" + run_id, quantity="20", unit="CASE")
        critical_raw = (json.dumps(critical, indent=2) + "\n").encode()
        critical_name = "adapter-" + run_id + "-critical"
        artifact["new_model_cases_requested"] = 2
        submit(critical_name, critical_raw)
        second = verify_case(args, client, critical_name, critical_raw, "QUARANTINED", 0)
        artifact["cases"].append(second)
        if not all(second["checks"].values()):
            raise ValueError("Critical adapter case failed")
        duplicate = "adapter-" + run_id + "-duplicate"
        submit(duplicate, raw)
        dup = verify_case(args, client, duplicate, raw, "DELIVERED", 1)
        artifact["duplicate"] = dup
        artifact["checks"]["duplicate_event_same_case_receipt"] = all(dup["checks"].values()) and dup["case_id"] == first["case_id"] and dup["trace_id"] == first["trace_id"] and dup["ack"]["delivery_receipt"]["case_id"] == first["case_id"] and record(client, first["case_id"])["delivery_count"] == 1 and dup["ack"]["duplicate_event"] is True
        submit(allow, raw)
        wait_for(lambda: not path(allow, ".ready").exists() and not path(allow, ".work").exists() and any(INBOX.glob(allow + ".json.duplicate.*")), "same filename idempotent redrop")
        artifact["checks"]["same_file_same_ack"] = acknowledgment(allow) == first["ack"] and record(client, first["case_id"])["delivery_count"] == 1
        failures = []
        for label, payload in (("malformed", b"{"), ("oversize", b" " * 131073), ("envelope", json.dumps({"message": message, "clock": "2099-01-01T00:00:00Z", "scenario_id": "approved-amendment", "fault": {"decision": "ALLOW"}, "references": []}).encode())):
            name = "adapter-" + run_id + "-" + label
            submit(name, payload)
            ack = wait_for(lambda: acknowledgment(name), label + " rejection")
            wait_for(lambda: path(name, ".hold").is_file(), label + " retained input")
            state = inspect(args, name)
            ok = ack["status"] == "REJECTED_INPUT" and ack["case_id"] == state["case_id"] == "" and ack["delivery_receipt"] is None and path(name, ".hold").read_bytes() == payload
            failures.append({"file": name, "input_bytes": len(payload), "ack": ack, "native_state": state, "passed": ok})
        artifact["rejected_inputs"] = failures
        artifact["checks"]["invalid_inputs_never_create_cases"] = all(f["passed"] for f in failures)
        symlink_name = "adapter-" + run_id + "-symlink"
        sentinel = INBOX / ("adapter-" + run_id + "-sentinel.txt")
        sentinel.write_bytes(b"Synthetic sentinel: the adapter must never open this through a symlink.\n")
        path(symlink_name, ".ready").symlink_to(sentinel.name)
        linked = wait_for(lambda: (s if (s := inspect(args, symlink_name))["held"] else None), "symlink rejection")
        artifact["symlink"] = linked
        artifact["checks"]["symlink_not_followed"] = linked["case_id"] == "" and path(symlink_name, ".ready").is_symlink() and sentinel.read_bytes() == b"Synthetic sentinel: the adapter must never open this through a symlink.\n"
        artifact["passed"] = all(artifact["checks"].values()) and all(all(c["checks"].values()) for c in artifact["cases"])
        return 0 if artifact["passed"] else 1
    except (ValueError, KeyError, TypeError, OSError, TimeoutError, subprocess.TimeoutExpired) as error:
        artifact["error"] = str(error) if isinstance(error, ValueError) else type(error).__name__
        trace = error.__traceback__
        while trace and trace.tb_next:
            trace = trace.tb_next
        artifact["error_location"] = {"file": Path(trace.tb_frame.f_code.co_filename).name, "line": trace.tb_lineno} if trace else None
        print("FAILED: " + artifact["error"], file=sys.stderr)
        return 1
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
        print(f"Native adapter evidence: {args.output}")


if __name__ == "__main__":
    raise SystemExit(main())
