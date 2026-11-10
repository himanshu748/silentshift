#!/usr/bin/env python3
"""Run preregistered paired held-out trials through the shipped native production.

No prompt/policy changes, fixture relabelling, output repair, or selective retries.
The operator-only harness is excluded from the native release manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from bootstrap import read_env
from verify_ipm_native import literal

ROOT = Path(__file__).resolve().parents[1]
LABEL_COMMIT = "a50a551a92b5f52ba5212a91dca3de0d21f57da5"
DATA_SHA = "e02747e587495dd2587a3813277a15451c7715638d9ff9962186a09e8986ef55"
MODEL = "qwen3-silentshift:4b-instruct"
PROMPT = "silentshift-investigator/1.3.1"


def frozen_dataset() -> dict:
    raw = (ROOT / "fixtures/v2-heldout/scenarios.json").read_bytes()
    committed = subprocess.check_output(
        ["git", "show", LABEL_COMMIT + ":fixtures/v2-heldout/scenarios.json"], cwd=ROOT
    )
    if raw != committed or hashlib.sha256(raw).hexdigest() != DATA_SHA:
        raise ValueError("Frozen contract inputs/labels changed; evaluation refused")
    return json.loads(raw)


def write_json(path: Path, value) -> None:
    raw = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if len(raw.encode()) > 49_000_000:
        raise ValueError("Evidence file exceeds Git size bound")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(raw)
    tmp.replace(path)


class Native:
    def __init__(self, args):
        self.args = args
        self.env = {**os.environ, **read_env(args.env_file)}
        self.docker = ["docker", "--context", args.context]

    def shell(self, commands: str, *, timeout=240):
        p = subprocess.run(
            self.docker + ["exec", "-i", self.args.container, "iris", "session", "IRIS", "-U", "SILENTSHIFT"],
            input=commands + "\nhalt\n", capture_output=True, text=True,
            timeout=timeout, cwd=ROOT, env=self.env,
        )
        lines = [line.removeprefix("HELDOUT=") for line in p.stdout.splitlines() if line.startswith("HELDOUT=")]
        if p.returncode or len(lines) != 1:
            private = ROOT / ".local/heldout/last-terminal.txt"
            private.write_text(p.stdout + p.stderr)
            private.chmod(0o600)
            raise RuntimeError("Native harness failed; private terminal output retained")
        try:
            return json.loads(lines[0])
        except ValueError:
            private = ROOT / ".local/heldout/last-terminal.txt"
            private.write_text(p.stdout + p.stderr)
            private.chmod(0o600)
            raise RuntimeError("Native result was not JSON; private diagnostics retained") from None

    def call(self, method, *args):
        encoded = ",".join(str(a) if isinstance(a, int) else literal(str(a)) for a in args)
        return self.shell('set result=##class(SilentShift.Test.HeldoutEval).' + method + "(" + encoded + ')\nwrite "HELDOUT=",result,!')

    def copy(self, source, target):
        subprocess.run(self.docker + ["cp", str(source), self.args.container + ":" + target], check=True, capture_output=True)


def baseline_matches(record, case):
    message = dict(record["message"])
    for k in ("event_id", "correlation_id"):
        message[k] = case["message"][k]
    return (message == case["message"] and
            sorted(record["references"], key=lambda r: r["id"]) == sorted(case["references"], key=lambda r: r["id"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Permit the 144 preregistered local native investigations")
    parser.add_argument("--container", default="silentshift-bonus-load-heldout-nov9")
    parser.add_argument("--context", default="colima-silentshift")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/heldout")
    args = parser.parse_args()
    dataset = frozen_dataset()
    if not args.execute:
        print("Frozen inputs verified; --execute permits local inference. No model/rules ran.")
        return 0
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    native = Native(args)
    target = "/home/irisowner/silentshift-bonus/HeldoutEval.cls"
    native.copy(ROOT / "tests/iris/HeldoutEval.cls", target)
    compiled = native.shell('set sc=$system.OBJ.Load(' + literal(target) + ',"ck")\nwrite "HELDOUT=",{"compiled":($system.Status.IsOK(sc))}.%ToJSON(),!')
    if not compiled["compiled"]:
        raise RuntimeError("Native evaluation class did not compile")
    identity = native.call("Identity")
    engine_sha = hashlib.sha256((ROOT / "python/silentshift/engine.py").read_bytes()).hexdigest()
    if ("Build 154U" not in identity["runtime"] or "ARM64" not in identity["runtime"]
            or identity["execution_mode"] != "live" or identity["model"] != MODEL
            or identity["prompt_version"] != PROMPT or identity["assets"]["engine_sha256"] != engine_sha
            or identity["module_version"] != "0.3.0"):
        raise RuntimeError("Actual native release/model/build identity mismatch")
    manifest_file = out / "manifest.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        if manifest["dataset_sha256"] != DATA_SHA or manifest["identity"] != identity:
            raise ValueError("Cannot resume against changed dataset/runtime identity")
    else:
        manifest = {"created_at": datetime.now(timezone.utc).isoformat(), "run_id": str(uuid.uuid4()),
            "dataset_sha256": DATA_SHA, "labels_commit": LABEL_COMMIT, "identity": identity,
            "execution": "three paired native trials per case; raw agent recommendation and shipped policy route",
            "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "synthetic": True, "status": "running", "completed": 0, "planned": 144,
            "actual_agent_only_delivery_executed": False, "policy_delivery_target": "IRIS simulator only"}
        stripped = {"clock": dataset["clock"], "dataset_version": dataset["dataset_version"],
            "scenarios": [{k: case[k] for k in ("id", "message", "references")} for case in dataset["scenarios"]]}
        payload = ROOT / ".local/heldout/native-input.json"
        write_json(payload, stripped)
        native.copy(payload, "/home/irisowner/silentshift-bonus/heldout-input.json")
        init = native.call("Initialize", "/home/irisowner/silentshift-bonus/heldout-input.json", manifest["run_id"])
        if init.get("cases") != 48:
            raise ValueError("Native input initialization did not retain every case")
        manifest["native_input_sha256"] = hashlib.sha256(payload.read_bytes()).hexdigest()
        write_json(manifest_file, manifest)
    run_id = manifest["run_id"]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest.setdefault("harness_revisions", [])
    if revision not in manifest["harness_revisions"]:
        manifest["harness_revisions"].append(revision)
    if manifest["status"] == "paused-infrastructure":
        manifest.setdefault("resume_events", []).append({
            "resumed_at": datetime.now(timezone.utc).isoformat(),
            "completed_retained": manifest["completed"], "harness_commit": revision})
        manifest["status"] = "running"
    write_json(manifest_file, manifest)
    rules_path = out / "rules-only.json"
    if not rules_path.exists():
        rows = [native.call("Rules", run_id, case["id"]) for case in dataset["scenarios"]]
        write_json(rules_path, {"identity": identity, "dataset_sha256": DATA_SHA, "cases": rows,
            "timing_scope": "assess + unchanged rule_only inside IRIS Embedded Python; session overhead excluded"})
        print("Rules-only completed: 48 frozen cases inside IRIS", flush=True)
    for trial in range(1, 4):
        directory = out / f"trial-{trial}"
        directory.mkdir(exist_ok=True)
        for case in dataset["scenarios"]:
            frozen_dataset()
            host_free = shutil.disk_usage(ROOT).free
            if host_free < 1.8 * 1024**3:
                manifest.update(status="paused-infrastructure",
                    paused_at=datetime.now(timezone.utc).isoformat(),
                    pause_reason="Host disk below unchanged storage floor",
                    host_free_bytes_at_pause=host_free)
                write_json(manifest_file, manifest)
                raise RuntimeError("Host disk below unchanged storage floor; checkpoint retained")
            dest = directory / (case["id"] + ".json")
            if dest.exists():
                existing = json.loads(dest.read_text())
                if existing["run_id"] != run_id or existing["scenario_id"] != case["id"]:
                    raise ValueError("Checkpoint identity mismatch")
                continue
            started = time.monotonic()
            prior = native.call("Read", run_id, case["id"], trial)
            observed = prior if prior["exists"] else native.call("Run", run_id, case["id"], trial)
            if not observed.get("exists"):
                write_json(directory / (case["id"] + "-incomplete.json"), observed)
                raise RuntimeError("No persisted case returned; no selective model retry")
            record = observed["record"]
            # Re-read persisted work; a failed native caller never permits redispatch.
            for _ in range(60):
                if record["routing"] != "PROCESSING":
                    break
                time.sleep(1)
                observed = native.call("Read", run_id, case["id"], trial)
                record = observed["record"]
            if record["routing"] == "PROCESSING" or not baseline_matches(record, case):
                write_json(directory / (case["id"] + "-incomplete.json"), observed)
                raise RuntimeError("Persisted case incomplete or inputs differ; checkpoint retained")
            export = native.shell('write "HELDOUT=",##class(SilentShift.Test.ProviderChecks).InspectCase(' + literal(record["id"]) + "),!")
            result = {"scenario_id": case["id"], "trial": trial, "run_id": run_id,
                "harness_commit": revision,
                "dataset_sha256": DATA_SHA, "case_id": record["id"], "trace_id": record["trace_id"],
                "service_elapsed_ms": observed.get("service_elapsed_ms"),
                "harness_elapsed_ms": round((time.monotonic()-started)*1000, 3),
                "record": record, "provider_export": export,
                "semantic_inputs_match_frozen": True, "resumed_existing_case": prior["exists"]}
            write_json(dest, result)
            manifest["completed"] = sum((out / f"trial-{n}" / (c["id"] + ".json")).exists()
                for n in range(1,4) for c in dataset["scenarios"])
            write_json(manifest_file, manifest)
            print(f"trial={trial} {case['id']} native_case={record['id']} session={record['trace_id']} "
                f"route={record['routing']} agent={record.get('agent',{}).get('status')} completed={manifest['completed']}/144", flush=True)
    manifest.update(status="completed", finished_at=datetime.now(timezone.utc).isoformat())
    write_json(manifest_file, manifest)
    print("All 144 native investigations persisted; labels unchanged. Generate the report separately.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
