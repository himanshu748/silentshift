"""No Docker or provider access is needed to reject unsafe verifier options."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "options,reason",
    [
        (["--execution-mode", "live"], "requires --allow-model-calls"),
        (["--install-latest"], "requires --source public-registry"),
    ],
)
def test_invalid_verification_options_stop_before_external_commands(options, reason):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_bonus_release.py"),
         "--source", "load", "--container", "silentshift-bonus-load-unused", *options],
        cwd=ROOT, env={**os.environ, "PATH": ""}, text=True,
        capture_output=True, timeout=10, check=False,
    )
    assert result.returncode == 1
    assert reason in result.stderr
    assert "Creating fresh" not in result.stdout
