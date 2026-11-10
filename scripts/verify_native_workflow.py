#!/usr/bin/env python3
"""Prove native task creation/claim/completion through the real review API.

One new local-model D case is rejected. A separate11-reference boundary case
skips inference and proves a safe human approval. Existing cases are untouched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from bootstrap import read_env
from verify_native import Client, native_build
from verify_native_trace import native

ROOT = Path(__file__).resolve().parents[1]


def observed(args, case_id: str, complete: bool = False) -> dict:
    if not re.fullmatch(r"[A-Fa-f0-9-]{36}", case_id):
        raise ValueError("Invalid workflow case identifier")
    result = {}
    for _ in range(30):
        statement = f'write "WORKFLOW_EXPORT=",##class(SilentShift.Test.WorkflowChecks).Inspect("{case_id}"),!'
        result = json.loads(native(args, statement, "WORKFLOW_EXPORT="))
        task = result.get("native_task") or {}
        if task and (not complete or task.get("is_complete") is True and (result.get("workflow") or {}).get("completion_received") is True):
            return result
        time.sleep(0.2)
    return result


def task_checks(record: dict, reviewer: str, action: str | None = None) -> dict:
    task = record.get("native_task") or {}
    workflow = record.get("workflow") or {}
    headers = record.get("native_headers") or []
    checks = {
        "actual_native_task": bool(task) and str(task.get("task_id")) == str(workflow.get("task_id")) and task.get("case_id") == record["case_id"],
        "native_role_case_version": task.get("role") == "ReviewWorklist" and isinstance(task.get("created_case_version"), int) and task["created_case_version"] > 0,
        "native_role_has_one_member": task.get("role_membership_count") == 1,
        "native_coordinator_request": any(h["source"] == "Semantic" and h["target"] == "ReviewCoordinator" for h in headers),
        "native_worklist_request": any(h["source"] == "ReviewCoordinator" and h["target"] == "ReviewWorklist" and h["body_class"] == "SilentShift.Workflow.ReviewRequest" for h in headers),
    }
    if action is None:
        checks["pending_native_worklist"] = task.get("is_complete") is False and task.get("worklist_count") == 1 and task.get("assigned_to") in ("", None)
    else:
        review = record.get("review") or {}
        checks.update({
            "actual_native_completion": task.get("is_complete") is True and task.get("action") == action.upper() and bool(task.get("time_completed")),
            "native_owner_bound_to_reviewer": task.get("assigned_to") == reviewer and task.get("user") == reviewer,
            "native_worklist_consumed": task.get("worklist_count") == 0,
            "actual_deferred_response": any(h["source"] == "ReviewWorklist" and h["target"] == "ReviewCoordinator" and h["body_class"] == "SilentShift.Workflow.ReviewTask" and str(h["body_id"]) == str(task.get("task_id")) for h in headers),
            "completion_receipt_received": workflow.get("completion_received") is True and bool(workflow.get("completion_header_id")),
            "reason_version_idempotency_preserved": task.get("review_reason") == review.get("reason") and task.get("review_idempotency_key") == review.get("idempotency_key") and task.get("reviewed_case_version") == review.get("expected_version"),
            "claim_audited": any(e["kind"] == "workflow_task_claimed" for e in record.get("workflow_events", [])),
        })
    return checks


def review_case(args, client: Client, viewer: Client, case_id: str, reviewer: str, action: str, fault: bool = False) -> dict:
    before = observed(args, case_id)
    checks = task_checks(before, reviewer)
    if not all(checks.values()):
        raise ValueError("Native workflow task was not created; remaining model calls stopped")
    bypass = native(args, f'write "WORKFLOW_BYPASS_DENIED=",##class(SilentShift.Test.WorkflowChecks).BypassDenied("{case_id}"),!', "WORKFLOW_BYPASS_DENIED=")
    checks["native_callback_bypass_denied"] = bypass == "1"
    request = {"action": action.upper(), "reason": "Synthetic native workflow verification: " + action,
               "expected_version": before["version"], "idempotency_key": str(uuid.uuid4())}
    status, _ = viewer.call(f"/cases/{case_id}/review", request)
    checks["viewer_denied"] = status == 403
    stale = dict(request, expected_version=before["version"] - 1, idempotency_key=str(uuid.uuid4()))
    status, _ = client.call(f"/cases/{case_id}/review", stale)
    checks["stale_version_denied"] = status == 409
    if action == "reject":
        denied = dict(request, action="APPROVE", idempotency_key=str(uuid.uuid4()))
        status, _ = client.call(f"/cases/{case_id}/review", denied)
        checks["unresolved_evidence_approval_denied"] = status == 403
    if not all(checks.values()):
        raise ValueError("Workflow boundary check failed before the authorized decision")
    if fault:
        armed = native(args, f'set sc=##class(SilentShift.Test.WorkflowChecks).ArmCompletionFault("{case_id}")\nwrite "WF_FAULT=",$SYSTEM.Status.IsOK(sc),!', "WF_FAULT=")
        if armed != "1":
            raise ValueError("Native completion fault could not be armed")
        try:
            status, _ = client.call(f"/cases/{case_id}/review", request)
            pending = observed(args, case_id)
            pending_checks = {
                "actual_postcommit_http503": status == 503,
                "review_receipt_committed": (pending.get("review") or {}).get("idempotency_key") == request["idempotency_key"],
                "completion_pending_without_delivery": (pending.get("workflow") or {}).get("status") == "completion_pending" and pending["routing"] == "REVIEW" and pending["delivery_count"] == 0,
                "native_task_not_completed": (pending.get("native_task") or {}).get("is_complete") is False,
            }
        finally:
            restored = native(args, f'set sc=##class(SilentShift.Test.WorkflowChecks).RestoreCompletionToken("{case_id}")\nwrite "WF_RESTORED=",$SYSTEM.Status.IsOK(sc),!', "WF_RESTORED=")
        pending_checks["exact_native_token_restored"] = restored == "1"
        checks.update(pending_checks)
        if args.pause_after_fault or not all(pending_checks.values()):
            return {"case_id": case_id, "before": before, "pending": pending, "request": request,
                    "checks": checks, "phase": "completion_pending", "passed": False}
    status, _ = client.call(f"/cases/{case_id}/review", request)
    if status != 200:
        return {"before": before, "request": request, "passed": False,
                "error": f"Workflow review failed (HTTP{status}); replay this exact request for postcommit recovery"}
    after = observed(args, case_id, complete=True)
    checks.update(task_checks(after, reviewer, action))
    checks["expected_case_route"] = after["routing"] == ("REJECTED" if action == "reject" else "DELIVERED")
    checks["expected_delivery_effect"] = after["delivery_count"] == (0 if action == "reject" else 1)
    status, repeated = client.call(f"/cases/{case_id}/review", request)
    checks["idempotent_review_retry"] = status == 200 and repeated.get("version") == after["version"] and repeated.get("delivery_count") == after["delivery_count"] and str((repeated.get("workflow") or {}).get("task_id")) == str((after.get("workflow") or {}).get("task_id"))
    after["checks"] = checks
    return {"before": before, "after": after, "request": request, "passed": all(checks.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--context")
    parser.add_argument("--container")
    parser.add_argument("--api")
    parser.add_argument("--allow-one-local-model-call", action="store_true")
    parser.add_argument("--review-case-id", help="Use an existing newly created D test case; no new model invocation")
    parser.add_argument("--safe-case-id", help="Use an existing new safe boundary test case; no new case creation")
    parser.add_argument("--postcommit-fault", action="store_true", help="Inject an actual native deferred-response production mismatch on the NEW safe case")
    parser.add_argument("--pause-after-fault", action="store_true", help="Restore token but retain pending case for UI recovery inspection")
    parser.add_argument("--resume-pending-file", type=Path, help="Replay the EXACT private pending review request; no model or case creation")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/workflow.json")
    args = parser.parse_args()
    artifact = {"created_at": datetime.now(timezone.utc).isoformat(), "cases": [], "passed": False, "model_case_runs": 0}
    try:
        env = read_env(args.env_file)
        args.runtime_env = env
        args.context = args.context or env.get("DOCKER_CONTEXT")
        args.container = args.container or (env.get("COMPOSE_PROJECT_NAME", ROOT.name.lower()) + "-iris-1")
        args.api = args.api or env.get("SILENTSHIFT_API_URL", "http://127.0.0.1:52773/silentshift/api")
        script = 'set ok=1\nfor f="TraceChecks","WorkflowChecks" {set sc=$SYSTEM.OBJ.Load("/opt/silentshift/tests/iris/"_f_".cls","ck") if $SYSTEM.Status.IsError(sc) set ok=0}\nwrite "WORKFLOW_TESTS=",ok,!'
        if native(args, script, "WORKFLOW_TESTS=") != "1":
            raise ValueError("Workflow test classes did not compile")
        reviewer = env["SILENTSHIFT_IRIS_USERNAME"]
        client = Client(args.api, reviewer, env["SILENTSHIFT_IRIS_PASSWORD"])
        viewer = Client(args.api, env["SILENTSHIFT_VIEWER_USERNAME"], env["SILENTSHIFT_VIEWER_PASSWORD"])
        status, health = client.call("/health")
        if status != 200 or not native_build(health.get("build")) or health.get("production", {}).get("running") is not True:
            raise ValueError("Native build154 production is not running")
        if args.resume_pending_file:
            artifact = json.loads(args.resume_pending_file.read_text())
            pending = artifact["cases"][-1]
            case_id = pending["case_id"]
            status, _ = client.call(f"/cases/{case_id}/review", pending["request"])
            if status != 200:
                raise ValueError(f"Exact pending review replay failed (HTTP{status})")
            after = observed(args, case_id, complete=True)
            checks = dict(pending["checks"])
            checks.update(task_checks(after, reviewer, "approve"))
            checks["same_key_recovery_delivered_once"] = after["routing"] == "DELIVERED" and after["delivery_count"] == 1
            status, repeated = client.call(f"/cases/{case_id}/review", pending["request"])
            checks["recovery_retry_idempotent"] = status == 200 and repeated.get("version") == after["version"] and repeated.get("delivery_count") == 1
            pending.update({"after": after, "checks": checks, "phase": "recovered", "passed": all(checks.values())})
            artifact["phase"] = "completed"
            artifact["resumed_at"] = datetime.now(timezone.utc).isoformat()
            artifact["new_model_case_runs_during_resume"] = 0
            artifact["passed"] = all(c["passed"] for c in artifact["cases"])
            return 0 if artifact["passed"] else 1
        case_id = args.review_case_id
        if not case_id:
            if not args.allow_one_local_model_call:
                print("Native tests compiled. Explicitly allow one local model run to create a fresh D case.")
                return 2
            if native(args, 'write "WF_LOCAL=",##class(SilentShift.Test.TraceChecks).LocalRouteSafe(),!', "WF_LOCAL=") != "1":
                raise ValueError("Actual provider route is not configured local Qwen/Ollama")
            artifact["run_id"] = str(uuid.uuid4())
            artifact["model_case_runs"] = 1
            status, case = client.call("/scenarios/conflicting-references/run", {"run_id": artifact["run_id"]})
            if status != 200:
                raise ValueError(f"New D case failed (HTTP{status}); no automatic model retry")
            case_id = str(case["id"])
        artifact["d_case_id"] = case_id
        artifact["cases"].append(review_case(args, client, viewer, case_id, reviewer, "reject"))
        if not artifact["cases"][-1]["passed"]:
            raise ValueError("Native rejection checks failed")
        safe_id = args.safe_case_id
        if not safe_id:
            safe_id = native(args, 'set sc=##class(SilentShift.Test.TraceChecks).RunBudgetCase(.id)\nif $SYSTEM.Status.IsOK(sc) write "WF_SAFE_ID=",id,!', "WF_SAFE_ID=")
        artifact["safe_case_id"] = safe_id
        artifact["cases"].append(review_case(args, client, viewer, safe_id, reviewer, "approve", args.postcommit_fault))
        if args.pause_after_fault and artifact["cases"][-1].get("phase") == "completion_pending":
            artifact["phase"] = "completion_pending_token_restored"
            print("Actual503 pending case retained with exact native token restored; replay the saved request to finish.")
            return 0
        artifact["passed"] = all(c["passed"] for c in artifact["cases"])
        return 0 if artifact["passed"] else 1
    except Exception as error:
        artifact["error"] = str(error) if isinstance(error, ValueError) else type(error).__name__
        print("FAILED: " + artifact["error"], file=sys.stderr)
        return 1
    finally:
        if artifact["cases"] or artifact.get("error"):
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
            print(f"Private native evidence: {args.output}")


if __name__ == "__main__":
    raise SystemExit(main())
