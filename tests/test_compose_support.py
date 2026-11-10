import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location("compose_support", Path(__file__).parents[1] / "scripts/compose_support.py")
compose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compose)


def result(code, output):
    return subprocess.CompletedProcess([], code, stdout=output, stderr="")


def test_prefers_working_plugin(monkeypatch):
    run = Mock(return_value=result(0, "2.40.0\n"))
    monkeypatch.setattr(compose.subprocess, "run", run)
    assert compose.compose_command() == ["docker", "compose"]
    assert run.call_count == 1


def test_uses_installed_standalone_when_plugin_missing(monkeypatch):
    run = Mock(side_effect=[result(1, ""), result(0, "5.6.1\n")])
    monkeypatch.setattr(compose.subprocess, "run", run)
    assert compose.compose_command() == ["docker-compose"]
    assert run.call_args_list[1].args[0] == ["docker-compose", "version", "--short"]


def test_rejects_legacy_standalone_or_failed_version(monkeypatch):
    monkeypatch.setattr(compose.subprocess, "run", Mock(side_effect=[result(1, ""), result(0, "1.29.2")]))
    assert compose.compose_command() is None


def test_missing_or_timed_out_cli_does_not_claim_ready(monkeypatch):
    monkeypatch.setattr(compose.subprocess, "run", Mock(side_effect=[subprocess.TimeoutExpired([], 10), FileNotFoundError()]))
    assert compose.compose_command() is None
