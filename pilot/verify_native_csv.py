#!/usr/bin/env python3
"""Verify isolated synthetic CSV imports and two live native order cases.

Requires the local operator's Docker access and private .env. Existing cases and
references are preserved. Run only with --execute to permit local model calls.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from bootstrap import read_env
from orders import ROOT, Client, prepare


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--context", default="colima-silentshift")
    parser.add_argument("--container", default="silentshift-clean-iris-1")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        parser.error("--execute is required: this runs two synthetic local-model investigations")
    if shutil.disk_usage(ROOT).free < 2 * 1024**3:
        parser.error("Native CSV verification requires at least 2 GiB free host space")
    output = args.output_directory.resolve()
    subprocess.run([sys.executable, str(ROOT / "pilot/make_sample.py"), str(output)], check=True)
    docker = ["docker", "--context", args.context]
    remote = "/tmp/ss-csv-" + uuid.uuid4().hex
    checks, imports = {}, {}

    def run(argv, *, data=None):
        result = subprocess.run(argv, input=data, text=True, capture_output=True, timeout=600, check=False)
        if result.returncode:
            raise ValueError("Operator command failed; diagnostics withheld")
        return result.stdout

    def session(code, marker):
        text = run(docker + ["exec", "-i", args.container, "iris", "session", "IRIS", "-U", "SILENTSHIFT"], data=code + "\nhalt\n")
        matches = [line[len(marker):] for line in text.splitlines() if line.startswith(marker)]
        if len(matches) != 1:
            raise ValueError("Native marker missing; no success assumed from terminal exit status")
        return matches[0]

    def private_json(path, value):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "w") as stream:
            json.dump(value, stream, indent=2, allow_nan=False, ensure_ascii=False)
            stream.write("\n")

    def import_bundle(name, value):
        path = output / (name + ".json")
        private_json(path, value)
        target = remote + "-" + name + ".json"
        run(docker + ["cp", str(path), args.container + ":" + target])
        # docker cp retains host ownership. Only this private synthetic bundle
        # is handed to the container's existing irisowner account.
        run(docker + ["exec", "-u", "root", args.container, "chown", "irisowner:irisowner", target])
        result = json.loads(session('write "CSV_IMPORT=",##class(SilentShiftPilot.ReferenceImport).Import("' + target + '"),!', "CSV_IMPORT="))
        imports[name] = result
        return result

    bundle = prepare(output / "orders.csv", output / "approved.csv")
    source = remote + ".cls"
    run(docker + ["cp", str(ROOT / "pilot/ReferenceImport.cls"), args.container + ":" + source])
    compiled = session('set sc=$system.OBJ.Load("' + source + '","ck")\nwrite "CSV_COMPILED=",$system.Status.IsOK(sc),!', "CSV_COMPILED=")
    checks["importer_compiled"] = compiled == "1"
    if not checks["importer_compiled"]:
        raise ValueError("Pilot importer did not compile")
    first = import_bundle("initial", bundle)
    checks["created_two_references"] = first == {"passed": True, "created": 2, "reused": 0}
    if not checks["created_two_references"]:
        raise ValueError("Initial import failed; stop before submitting orders")
    repeat = import_bundle("repeat", bundle)
    checks["repeat_import_reuses_revisions"] = repeat == {"passed": True, "created": 0, "reused": 2}

    conflicting = copy.deepcopy(bundle)
    new_id = "csv-ref:" + uuid.uuid4().hex
    conflicting["references"][0]["id"] = new_id
    conflicting["references"][1]["quantity"] = "999"
    result = import_bundle("conflict", conflicting)
    checks["changed_revision_refused"] = result.get("passed") is False
    present = session('write "CSV_EXISTS=",##class(SilentShift.Data.Reference).%ExistsId(##class(SilentShift.Bridge).PairHash("","' + new_id + '")),!', "CSV_EXISTS=")
    checks["whole_import_rolled_back"] = present == "0"
    unapproved = copy.deepcopy(bundle)
    unapproved["references"][0]["authority"] = "peer"
    checks["peer_cannot_authorize_import"] = import_bundle("peer", unapproved).get("passed") is False
    unsigned = copy.deepcopy(bundle)
    unsigned["references"][0]["approval_provenance"]["approved_by"] = ""
    checks["approval_provenance_required"] = import_bundle("unsigned", unsigned).get("passed") is False
    empty = copy.deepcopy(bundle)
    empty["references"] = []
    checks["empty_import_refused"] = import_bundle("empty", empty).get("passed") is False
    if not all(checks.values()):
        private_json(output / "import-failure.json", {"checks": checks, "imports": imports})
        raise ValueError("Import safety checks failed; no orders submitted")

    env = read_env(ROOT / ".env")
    command = [sys.executable, str(ROOT / "pilot/orders.py"), "--orders", str(output / "orders.csv"),
               "--approved", str(output / "approved.csv"), "--submit-local", "--output"]
    def execute_cli(filename):
        result = subprocess.run(command + [str(output / filename)], env=env, text=True,
                                capture_output=True, timeout=600,
            check=False,
        )
        if result.returncode:
            raise ValueError("Native CSV CLI failed; inspect its private checkpoint before resuming")
        return json.loads((output / filename).read_text())

    first_run = execute_cli("native-first.json")
    lines = first_run["native_results"]["lines"]
    checks["unsupported_order_held"] = lines[0]["routing"] == "QUARANTINED" and lines[0]["delivery_count"] == 0
    checks["matching_order_simulated_once"] = lines[1]["routing"] == "DELIVERED" and lines[1]["delivery_count"] == 1
    client = Client("http://127.0.0.1:52773/silentshift/api", env["SILENTSHIFT_IRIS_USERNAME"], env["SILENTSHIFT_IRIS_PASSWORD"])
    cases = []
    for line in lines:
        status, case = client.call("/cases/" + line["case_id"])
        agent = (case.get("agent") or {}) if isinstance(case, dict) else {}
        reads = agent.get("tool_reads") or {}
        checks["native_four_tools_" + line["line_id"] + "_" + line["order_id"]] = status == 200 and agent.get("status") == "returned" and all(reads.get(k, 0) >= 1 for k in ("message", "contracts", "related", "precedents"))
        cases.append({"case_id": line["case_id"], "trace_id": line["trace_id"], "routing": line["routing"], "delivery_count": line["delivery_count"], "tool_reads": reads,
                      "agent_status": agent.get("status"), "agent_failure_code": agent.get("failure_code")})
    repeated = execute_cli("native-repeat.json")
    checks["repeat_reuses_cases_traces_and_receipts"] = repeated["native_results"] == first_run["native_results"]
    changed = copy.deepcopy(bundle["records"][0]["message"])
    changed["quantity"] = "21"
    status, _ = client.call("/messages", changed)
    checks["changed_event_identity_conflicts"] = status == 409
    checks["no_atomic_order_claim"] = all(not order["atomic_order_delivery"] and order["order_completeness"] == "not_verified" for order in first_run["native_results"]["orders"])
    report = {"passed": all(checks.values()), "synthetic": True, "scope": "CSV reference import and two native per-line simulator cases; no external delivery", "checks": checks, "imports": imports, "cases": cases,
              "feed_sha256": bundle["feed_sha256"], "approved_sha256": bundle["approved_sha256"]}
    private_json(output / "verification.json", report)
    print(json.dumps({"passed": report["passed"], "checks": len(checks), "cases": cases}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError):
        raise SystemExit("CSV native verification stopped; retain the private output and inspect the failed stage.")
