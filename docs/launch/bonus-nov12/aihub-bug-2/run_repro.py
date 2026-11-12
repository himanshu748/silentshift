#!/usr/bin/env python3
"""Run the standalone stream-codec repro in fresh, network-isolated IRIS containers.

Uses only an already-loaded image. Never pulls, publishes, removes containers,
mounts application source, exposes ports, or sends provider/model requests.
Stopped test containers remain available for inspection.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = "docker.iscinternal.com/docker-intersystems/intersystems/iris-community:2026.3.0AI.154.0"
EXPECTED_ID = "sha256:8fa0ae85777d11ef113ec25a7ac2d1548edfa321a31bcbfa3e0a01ea7dbd8713"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", default="colima-silentshift")
    parser.add_argument("--runs", type=int, choices=range(1, 4), default=3)
    parser.add_argument("--prefix", default="aihub-stream-repro-nov12")
    args = parser.parse_args()
    docker = ["docker", "--context", args.context]
    out = HERE / "outputs"
    out.mkdir(exist_ok=True)
    commands: list[dict] = []

    def command(tail: list[str], *, stdin: bytes | None = None, timeout: int = 120) -> bytes:
        full = docker + tail
        run = subprocess.run(full, input=stdin, capture_output=True, timeout=timeout, check=False)
        commands.append({"argv": full, "exit_code": run.returncode,
                         "stdout": run.stdout.decode("utf-8", errors="replace"),
                         "stderr": run.stderr.decode("utf-8", errors="replace")})
        if run.returncode:
            raise RuntimeError(f"Command failed: {full!r}\n{run.stderr.decode(errors='replace')}")
        return run.stdout

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    image_info = json.loads(command(["image", "inspect", IMAGE]))[0]
    if image_info["Id"] != EXPECTED_ID or image_info["Architecture"] != "arm64":
        raise RuntimeError("Loaded image is not the intended 154U ARM64 image; refusing to run.")
    results: list[dict] = []
    try:
        for index in range(1, args.runs + 1):
            name = f"{args.prefix}-{index}"
            cid = command(["run", "--pull=never", "-d", "--name", name,
                           "--network", "none", "--memory", "2g", "--cpus", "2",
                           "--shm-size", "256m", IMAGE, "--check-caps", "false"]).decode().strip()
            try:
                for _ in range(90):
                    logs = command(["logs", name])
                    if b"...started InterSystems IRIS instance IRIS" in logs:
                        break
                    time.sleep(1)
                else:
                    raise RuntimeError(f"IRIS did not start in {name}")
                command(["cp", str(HERE / "StreamTools.cls"), name + ":/tmp/StreamTools.cls"])
                stdout = command(["exec", "-i", name, "iris", "session", "IRIS", "-U", "USER"],
                                 stdin=(HERE / "repro.in").read_bytes())
                (out / f"fresh-{index}.txt").write_bytes(stdout)
                text = stdout.decode("utf-8", errors="replace")
                flags = {
                    "fresh_class_absent": "CLASS_PRESENT_BEFORE_LOAD=0" in text,
                    "compile_ok": "COMPILE_OK=1" in text,
                    "register_ok": "REGISTER_OK=1" in text,
                    "direct_stream_ok": "DIRECT_STREAM_TEXT=Approved amendment: 1 CASE = 12 EA." in text,
                    "direct_read_ok": "DIRECT_READ_TEXT=Approved amendment: 1 CASE = 12 EA." in text,
                    "wrong_result_type": "STREAM_VALUE_TYPE=object" in text,
                    "payload_missing": "STREAM_PAYLOAD_MATCH=0" in text,
                    "inbound_stream_error": "READ_STREAM_ERROR=ERROR <%AICore>ToolExecutionFailed:" in text,
                    "control_after_error_ok": '"value":"Approved amendment: 1 CASE = 12 EA."' in text.split("CONTROL_AFTER_ERROR=", 1)[-1],
                }
                results.append({"run": index, "container": name, "container_id": cid,
                                "output": f"outputs/fresh-{index}.txt",
                                "output_sha256": hashlib.sha256(stdout).hexdigest(),
                                "observations": flags, "reproduced": all(flags.values())})
                print(json.dumps(results[-1]), flush=True)
                if not all(flags.values()):
                    raise RuntimeError("Repro observations differ; stop and inspect retained output.")
            finally:
                command(["stop", name])
    finally:
        summary = {"started_at_utc": started,
                   "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "image": IMAGE, "image_id": image_info["Id"], "architecture": "arm64",
                   "network": "none", "ports_published": False, "source_mounts": [],
                   "provider_requests": 0, "paid_calls": 0,
                   "results": results, "commands": commands}
        (out / "fresh-reproduction.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
