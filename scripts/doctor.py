#!/usr/bin/env python3
"""Read-only readiness audit. Never prints credential values or pulls images."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

from compose_support import compose_command


def command(args: list[str]) -> dict:
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=15, check=False)
        return {"ok": completed.returncode == 0, "output": completed.stdout.strip()[:1800],
                "error": completed.stderr.strip()[:500] if completed.returncode else None}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": type(exc).__name__}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    free = shutil.disk_usage(root).free / 1024**3
    compose_cli = compose_command()
    compose = command(compose_cli + ["version", "--short"]) if compose_cli else {"ok": False, "error": "Modern Docker Compose not found"}
    compose["command"] = compose_cli
    report = {
        "architecture": platform.machine(), "python": platform.python_version(),
        "free_disk_gib": round(free, 2),
        "credentials_present": {name: bool(os.environ.get(name)) for name in (
            "SILENTSHIFT_LLM_API_KEY", "OPENAI_API_KEY", "SILENTSHIFT_IRIS_USERNAME", "SILENTSHIFT_IRIS_PASSWORD")},
        "docker": command(["docker", "version", "--format", "{{json .Server.Version}}"]),
        "compose": compose,
        "local_images": command(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"]),
        "node": command(["node", "--version"]),
        "notes": ["Credential presence does not prove provider authorization or credits.",
                  "Download the official architecture-specific Community AI Hub 2026.3.0AI.154.0 kit; no guessed public pull.",
                  "Disk needs depend on the downloaded kit and Docker host; this audit never deletes files.",
                  "A remote Docker context can avoid local runtime storage; do not publish the restricted image."]}
    print(json.dumps(report, indent=2))
    return 0 if report["docker"]["ok"] and report["compose"]["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
