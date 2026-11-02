"""Find a working modern Compose CLI without installing or changing Docker."""
from __future__ import annotations

import re
import subprocess


def compose_command(env: dict[str, str] | None = None) -> list[str] | None:
    for command in (["docker", "compose"], ["docker-compose"]):
        try:
            result = subprocess.run(command + ["version", "--short"], env=env,
                                    capture_output=True, text=True, timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        version = re.match(r"^v?(\d+)(?:\.|\s|$)", result.stdout.strip())
        if result.returncode == 0 and version and int(version.group(1)) >= 2:
            return command
    return None
