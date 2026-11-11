"""Exercise judge harness boundaries without Docker, network or model calls."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

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

    def command(argv, *, env=None, capture=False, timeout=None):
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


def test_missing_archive_stops_without_docker_or_private_files(harness, capsys):
    root, calls, _ = harness
    assert judge.main(["--image-archive", str(root / "absent.tar.gz")]) == 1
    assert "--image-archive file was not found" in capsys.readouterr().err
    assert calls == [] and list(root.iterdir()) == []


def test_supplied_archive_loads_then_verifies_before_retagging(harness, monkeypatch):
    root, calls, image = harness
    archive = root / "official.tar.gz"
    archive.write_bytes(b"synthetic archive, never sent to Docker")
    target_exists = False

    def loaded(argv, **kwargs):
        nonlocal target_exists
        calls.append((argv, None))
        if argv[-2:] == ["ls", "--quiet"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "load" in argv:
            assert kwargs["timeout"] == 1200
            return subprocess.CompletedProcess(argv, 0, "Loaded image: vendor:154\n", "")
        if "tag" in argv:
            assert argv[-2:] == ["vendor:154", judge.IMAGE]
            target_exists = True
        if "inspect" in argv and argv[-1] == judge.IMAGE and not target_exists:
            return subprocess.CompletedProcess(argv, 1, "", "")
        return subprocess.CompletedProcess(argv, 0, json.dumps([image]), "")

    monkeypatch.setattr(judge, "command", loaded)
    judge.preflight(judge.parser().parse_args(["--image-archive", str(archive)]))
    assert target_exists
    kinds = ["load" if "load" in argv else "tag" if "tag" in argv
             else "inspect" if "inspect" in argv else "other" for argv, _ in calls]
    assert kinds.index("load") < kinds.index("tag")
    assert not (root / ".local").exists()


def test_wrong_archive_build_is_never_retagged(harness, monkeypatch, capsys):
    root, calls, image = harness
    archive = root / "wrong.tar.gz"
    archive.write_bytes(b"synthetic archive")
    image["Architecture"] = "amd64"

    def wrong(argv, **kwargs):
        calls.append((argv, None))
        if argv[-2:] == ["ls", "--quiet"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "load" in argv:
            return subprocess.CompletedProcess(argv, 0, "Loaded image: vendor:x64\n", "")
        if "inspect" in argv and argv[-1] == judge.IMAGE:
            return subprocess.CompletedProcess(argv, 1, "", "")
        return subprocess.CompletedProcess(argv, 0, json.dumps([image]), "")

    monkeypatch.setattr(judge, "command", wrong)
    assert judge.main(["--image-archive", str(archive)]) == 1
    assert "exactly one verified" in capsys.readouterr().err
    assert all("tag" not in argv for argv, _ in calls)
    assert not (root / ".local").exists()


def test_loaded_image_is_reused_without_loading_supplied_archive(harness):
    root, calls, _ = harness
    archive = root / "official.tar.gz"
    archive.write_bytes(b"synthetic archive")
    judge.preflight(judge.parser().parse_args(["--image-archive", str(archive)]))
    assert all("load" not in argv and "tag" not in argv for argv, _ in calls)


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
    assert judge.main(["--api-port", "52999", "--network-subnet", "10.243.8.0/24"]) == 0
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
    installer = root / ".local/ipm/vendor/zpm-0.10.10.xml"
    install = next(argv for argv, _ in calls if any(Path(arg).name == "verify_bonus_release.py" for arg in argv))
    repeat = next(argv for argv, _ in calls if any(Path(arg).name == "trace_example.py" for arg in argv))
    assert install[1] == str(root / "scripts/verify_bonus_release.py")
    assert install[install.index("--verification-source") + 1] == str(source)
    assert install[install.index("--network-subnet") + 1] == "10.243.8.0/24"
    assert repeat[1] == str(source / "scripts/trace_example.py")
    fetch = next(argv for argv, _ in calls if argv[0] == "git" and "fetch" in argv)
    assert fetch[-4:] == ["--depth", "1", judge.REPOSITORY, judge.RELEASE_COMMIT]
    assert any(argv[-2:] == ["rev-parse", "HEAD"] for argv, _ in calls)
    assert "pinned release tests/replay and current install orchestration" in output.out
    assert install[install.index("--version") + 1] == "0.3.2"
    assert install[install.index("--execution-mode") + 1] == "recorded-replay"
    assert "--install-latest" in install and "--allow-model-calls" not in install
    assert "--live" not in repeat
    assert install[install.index("--env-file") + 1] == repeat[repeat.index("--env-file") + 1] == str(env_file)
    assert all("pull" not in argv for argv, _ in calls)
    assert all(env["SILENTSHIFT_API_KEY"] == "" for _, env in calls)
    assert installer.stat().st_mode & 0o777 == 0o644


@pytest.mark.parametrize("failed_stage", ["fetch-release", "fetch-ipm", "install"])
def test_failed_stage_stops_before_later_commands(harness, monkeypatch, capsys, failed_stage):
    _root, calls, _ = harness
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


@pytest.mark.parametrize("value", ["8.8.8.0/24", "10.0.0.1/24", "10.0.0.0/29", "fd00::/24"])
def test_invalid_network_subnet_stops_before_docker_or_files(harness, capsys, value):
    root, calls, _ = harness
    assert judge.main(["--network-subnet", value]) == 1
    assert "RFC1918" in capsys.readouterr().err
    assert calls == [] and list(root.iterdir()) == []


def test_automatic_subnet_skips_occupied_blocks_from_one_read_only_snapshot(harness, monkeypatch):
    _, calls, _ = harness
    def snapshot(argv, **kwargs):
        calls.append((argv, None))
        if argv[-2:] == ["ls", "--quiet"]:
            return subprocess.CompletedProcess(argv, 0, "first second", "")
        return subprocess.CompletedProcess(argv, 0, json.dumps([
            {"IPAM": {"Config": [{"Subnet": "10.253.0.0/28"}, {"Subnet": "fd00::/64"}]}},
            {"IPAM": {"Config": [{"Subnet": "10.253.0.16/29"}]}}
        ]), "")
    monkeypatch.setattr(judge, "command", snapshot)
    assert judge.unused_network_subnet(["docker"]) == "10.253.0.32/28"
    assert [argv for argv, _ in calls] == [["docker", "network", "ls", "--quiet"],
                                         ["docker", "network", "inspect", "first", "second"]]


def test_default_wrapper_forwards_selected_explicit_subnet(harness):
    _, calls, _ = harness
    assert judge.main([]) == 0
    install = next(argv for argv, _ in calls if any(Path(arg).name == "verify_bonus_release.py" for arg in argv))
    assert install[install.index("--network-subnet") + 1] == "10.253.0.0/28"
    assert len([argv for argv, _ in calls if argv[-2:] == ["ls", "--quiet"]]) == 1


def test_explicit_subnet_does_not_trigger_automatic_snapshot(harness):
    _, calls, _ = harness
    args = judge.parser().parse_args(["--network-subnet", "192.168.240.0/28"])
    judge.preflight(args)
    assert args.network_subnet == "192.168.240.0/28"
    assert all("network" not in argv for argv, _ in calls)


def test_automatic_subnet_exhaustion_does_not_try_creating_networks(harness, monkeypatch):
    root, calls, _ = harness
    def occupied(argv, **kwargs):
        calls.append((argv, None))
        payload = "existing" if argv[-2:] == ["ls", "--quiet"] else json.dumps([
            {"IPAM": {"Config": [{"Subnet": "10.0.0.0/8"}]}}
        ])
        return subprocess.CompletedProcess(argv, 0, payload, "")
    monkeypatch.setattr(judge, "command", occupied)
    with pytest.raises(ValueError, match="No unused /28 remains"):
        judge.unused_network_subnet(["docker"])
    assert len(calls) == 2 and list(root.iterdir()) == []
    assert all("create" not in argv and "prune" not in argv for argv, _ in calls)


@pytest.mark.parametrize("failure", ["list", "inspect", "malformed"])
def test_failed_subnet_inspection_stops_before_private_files(harness, monkeypatch, capsys, failure):
    root, calls, _ = harness
    def unavailable(argv, **kwargs):
        calls.append((argv, None))
        if "info" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[-2:] == ["ls", "--quiet"]:
            return subprocess.CompletedProcess(argv, 1 if failure == "list" else 0, "existing", "")
        return subprocess.CompletedProcess(argv, 1 if failure == "inspect" else 0, "not JSON", "")
    monkeypatch.setattr(judge, "command", unavailable)
    assert judge.main([]) == 1
    assert "test subnet selection" in capsys.readouterr().err
    assert list(root.iterdir()) == []
    assert all("create" not in argv and "prune" not in argv for argv, _ in calls)


def test_shell_entry_reports_missing_uv_without_running_docker(tmp_path):
    result = subprocess.run(["/bin/sh", str(SCRIPT.with_name("judge-replay.sh"))],
                            env={"PATH": ""}, cwd=tmp_path, text=True,
                            capture_output=True, timeout=10, check=False)
    assert result.returncode == 1
    assert "uv is required" in result.stderr


def test_shell_entry_forwards_arguments_from_another_directory(tmp_path):
    bin_path = tmp_path / "bin"
    bin_path.mkdir()
    uv = bin_path / "uv"
    uv.write_text("#!" + sys.executable + "\nimport json,os,sys\n"
                  "print(json.dumps({'cwd':os.getcwd(),'args':sys.argv[1:]}))\n")
    uv.chmod(0o755)
    result = subprocess.run(["/bin/sh", str(SCRIPT.with_name("judge-replay.sh")),
                             "--api-port", "52999", "--image-archive", "archive with spaces.tar.gz"],
                            env={**os.environ, "PATH": str(bin_path) + os.pathsep + os.environ["PATH"]},
                            cwd=tmp_path, text=True, capture_output=True,
                            timeout=10, check=False)
    assert result.returncode == 0
    observed = json.loads(result.stdout)
    assert observed["cwd"] == str(SCRIPT.parents[1])
    assert observed["args"] == ["run", "python", "scripts/judge_replay.py",
                                "--api-port", "52999", "--image-archive", "archive with spaces.tar.gz"]
