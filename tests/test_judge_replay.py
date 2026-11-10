"""Exercise judge harness boundaries without Docker, network or model calls."""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/judge_replay.py"
spec = importlib.util.spec_from_file_location("judge_replay", SCRIPT)
judge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(judge)


@pytest.fixture
def harness(monkeypatch, tmp_path):
    monkeypatch.setattr(judge, "ROOT", tmp_path)
    monkeypatch.setattr(judge.shutil, "which", lambda _: "/synthetic/docker")
    calls = []
    image = {"Architecture": "arm64", "Config": {"Labels": {
        "com.intersystems.platform-version": "2026.3.0AI.154.0com"}}}

    def command(argv, *, env=None, capture=False):
        calls.append((argv, env))
        if "image" in argv:
            return subprocess.CompletedProcess(argv, 0, json.dumps([image]), "")
        if "rev-parse" in argv:
            return subprocess.CompletedProcess(argv, 0, judge.RELEASE_COMMIT + "\n", "")
        if any(Path(arg).name == "fetch_ipm.py" for arg in argv):
            installer = Path(argv[argv.index("--output") + 1])
            installer.parent.mkdir(parents=True)
            installer.write_text("synthetic installer")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(judge, "command", command)
    class FreePort:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def bind(self, _): pass
    monkeypatch.setattr(judge.socket, "socket", FreePort)
    return tmp_path, calls, image


def test_missing_docker_is_clear_and_creates_no_files(harness, monkeypatch, capsys):
    root, calls, _ = harness
    monkeypatch.setattr(judge.shutil, "which", lambda _: None)
    assert judge.main([]) == 1
    assert "Docker CLI is missing" in capsys.readouterr().err
    assert calls == [] and list(root.iterdir()) == []


def test_missing_git_stops_before_files_or_external_commands(harness, monkeypatch, capsys):
    root, calls, _ = harness
    monkeypatch.setattr(judge.shutil, "which", lambda name: None if name == "git" else "/synthetic/docker")
    assert judge.main([]) == 1
    assert "Git CLI is missing" in capsys.readouterr().err
    assert calls == [] and list(root.iterdir()) == []


def test_missing_image_stops_before_credentials_or_downloads(harness, monkeypatch, capsys):
    root, calls, _ = harness

    def missing(argv, **kwargs):
        calls.append((argv, None))
        return subprocess.CompletedProcess(argv, 1 if "image" in argv else 0, "", "")

    monkeypatch.setattr(judge, "command", missing)
    assert judge.main([]) == 1
    message = capsys.readouterr().err
    assert judge.IMAGE in message and "docker load -i <archive>" in message
    assert "no image download" in message
    assert list(root.iterdir()) == []
    assert all("fetch_ipm.py" not in " ".join(a) for a, _ in calls)


@pytest.mark.parametrize("change", ["build", "architecture"])
def test_unverified_build_or_architecture_is_rejected(harness, capsys, change):
    root, _, image = harness
    if change == "build":
        image["Config"]["Labels"]["com.intersystems.platform-version"] = "2027.1.0AI.109.0com"
    else:
        image["Architecture"] = "amd64"
    assert judge.main([]) == 1
    assert "154U) ARM64" in capsys.readouterr().err
    assert list(root.iterdir()) == []


def test_private_credentials_and_recorded_commands_do_not_leak_live_environment(harness, monkeypatch, capsys):
    root, calls, _ = harness
    monkeypatch.setenv("SILENTSHIFT_API_KEY", "synthetic-private-provider-key")
    monkeypatch.setenv("SILENTSHIFT_IRIS_PASSWORD", "synthetic-existing-password")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-external-key")
    monkeypatch.setenv("GH_TOKEN", "synthetic-github-token")
    monkeypatch.setattr(judge, "preflight", lambda _: None)
    assert judge.main(["--api-port", "52999"]) == 0
    files = list((root / ".local/judge").glob("*/runtime.env"))
    assert len(files) == 1
    env_file = files[0]
    assert env_file.stat().st_mode & 0o777 == 0o600
    assert env_file.parent.stat().st_mode & 0o777 == 0o700
    values = dict(line.split("=", 1) for line in env_file.read_text().splitlines())
    passwords = [value for key, value in values.items() if key.endswith("PASSWORD")]
    assert len(passwords) == len(set(passwords)) == 3
    assert all(len(value) >= 12 for value in passwords)
    assert values["SILENTSHIFT_PROVIDER_MODE"] == "recorded-replay"
    assert not (root / ".env").exists()
    output = capsys.readouterr()
    for secret in [*passwords, "synthetic-private-provider-key", "synthetic-existing-password",
                   "synthetic-external-key", "synthetic-github-token"]:
        assert secret not in output.out + output.err
        assert all(secret not in json.dumps(env) for _, env in calls)
    source = env_file.parent / "source"
    installer = source / ".local/ipm/vendor/zpm-0.10.10.xml"
    install = next(argv for argv, _ in calls if any(Path(arg).name == "verify_bonus_release.py" for arg in argv))
    repeat = next(argv for argv, _ in calls if any(Path(arg).name == "trace_example.py" for arg in argv))
    assert install[1] == str(source / "scripts/verify_bonus_release.py")
    assert repeat[1] == str(source / "scripts/trace_example.py")
    fetch = next(argv for argv, _ in calls if argv[0] == "git" and "fetch" in argv)
    assert fetch[-4:] == ["--depth", "1", judge.REPOSITORY, judge.RELEASE_COMMIT]
    assert any(argv[-2:] == ["rev-parse", "HEAD"] for argv, _ in calls)
    assert "pinned release harness; not current source runtime" in output.out
    assert install[install.index("--version") + 1] == "0.3.0"
    assert install[install.index("--execution-mode") + 1] == "recorded-replay"
    assert "--install-latest" in install and "--allow-model-calls" not in install
    assert "--live" not in repeat
    assert install[install.index("--env-file") + 1] == repeat[repeat.index("--env-file") + 1] == str(env_file)
    assert all("pull" not in argv for argv, _ in calls)
    assert all(env["SILENTSHIFT_API_KEY"] == "" for _, env in calls)
    assert installer.stat().st_mode & 0o777 == 0o644


@pytest.mark.parametrize("failed_stage", ["fetch-release", "fetch-ipm", "install"])
def test_failed_stage_stops_before_later_commands(harness, monkeypatch, capsys, failed_stage):
    root, calls, _ = harness
    monkeypatch.setattr(judge, "preflight", lambda _: None)
    success = judge.command

    def command(argv, **kwargs):
        result = success(argv, **kwargs)
        is_target = ((failed_stage == "fetch-release" and argv[0] == "git" and "fetch" in argv)
                     or (failed_stage == "fetch-ipm" and any(Path(arg).name == "fetch_ipm.py" for arg in argv))
                     or (failed_stage == "install" and any(Path(arg).name == "verify_bonus_release.py" for arg in argv)))
        return subprocess.CompletedProcess(argv, 7, "", "") if is_target else result

    monkeypatch.setattr(judge, "command", command)
    assert judge.main([]) == 7
    assert all("trace_example.py" not in " ".join(argv) for argv, _ in calls)
    if failed_stage == "fetch-release":
        assert all(".py" not in " ".join(argv) for argv, _ in calls)
    elif failed_stage == "fetch-ipm":
        assert all("verify_bonus_release.py" not in " ".join(argv) for argv, _ in calls)
    assert "Judge replay stopped" in capsys.readouterr().err


def test_wrong_release_head_stops_before_ipm_or_install(harness, monkeypatch, capsys):
    _, calls, _ = harness
    monkeypatch.setattr(judge, "preflight", lambda _: None)
    success = judge.command

    def wrong_head(argv, **kwargs):
        result = success(argv, **kwargs)
        if "rev-parse" in argv:
            return subprocess.CompletedProcess(argv, 0, "synthetic-wrong-head\n", "")
        return result

    monkeypatch.setattr(judge, "command", wrong_head)
    assert judge.main([]) == 1
    assert "HEAD mismatch" in capsys.readouterr().err
    assert all(".py" not in " ".join(argv) for argv, _ in calls)


def test_existing_container_is_not_replaced(harness, capsys):
    root, _, _ = harness
    assert judge.main(["--container", "silentshift-bonus-registry-existing"]) == 1
    assert "already exists" in capsys.readouterr().err
    assert list(root.iterdir()) == []


def test_busy_port_stops_before_files(harness, monkeypatch, capsys):
    root, _, _ = harness
    class Busy:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def bind(self, _): raise OSError("synthetic occupied port")
    monkeypatch.setattr(judge.socket, "socket", Busy)
    assert judge.main([]) == 1
    assert "--api-port" in capsys.readouterr().err
    assert list(root.iterdir()) == []
