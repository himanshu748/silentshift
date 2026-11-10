#!/usr/bin/env python3
"""Install public native IPM 0.3.0 and run two keyless recorded replays.

Requires running Colima and the locally loaded official build-154U ARM64 and
Web Gateway images. Creates new isolated test containers and private local test
credentials; retains them for inspection. No image pull, fresh model inference,
publication, or existing application configuration change is performed. This
checks the published native package with its pinned compatible release harness,
not the current source branch's runtime changes or additional native tests.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.0"
RELEASE_COMMIT = "a7aa217f1fc8d96f56bac6fd3110618eec21c353"
REPOSITORY = "https://github.com/himanshu748/silentshift.git"
IMAGE = "silentshift-iris:2026.3.0AI.154.0"
GATEWAY = "containers.intersystems.com/intersystems/webgateway:2026.1"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--context", default="colima-silentshift")
    p.add_argument("--vm-profile", default="silentshift")
    p.add_argument("--image", default=IMAGE)
    p.add_argument("--gateway-image", default=GATEWAY)
    p.add_argument("--api-port", type=int, default=52843)
    p.add_argument("--container", help="New silentshift-bonus-registry-* name")
    return p


def command(argv: list[str], *, env: dict[str, str] | None = None,
            capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=ROOT, env=env, text=True,
                          capture_output=capture, check=False,
                          timeout=30 if capture else 1200)


def preflight(args: argparse.Namespace) -> None:
    if not 1024 <= args.api_port <= 65535:
        raise ValueError("Use an unprivileged --api-port between 1024 and 65535")
    if args.container and not re.fullmatch(
            r"silentshift-bonus-registry-[a-z0-9-]{1,35}", args.container):
        raise ValueError("Use a new silentshift-bonus-registry-* container name")
    if shutil.which("docker") is None:
        raise ValueError("Docker CLI is missing. Install it, then start Colima: "
                         "colima start --profile " + args.vm_profile)
    if shutil.which("git") is None:
        raise ValueError("Git CLI is missing. Install Git to fetch the pinned public release harness.")
    docker = ["docker", "--context", args.context]
    if command([*docker, "info"], capture=True).returncode:
        raise ValueError("Docker context is unavailable: " + args.context +
                         ". Start Colima: colima start --profile " + args.vm_profile)
    result = command([*docker, "image", "inspect", args.image], capture=True)
    if result.returncode:
        raise ValueError("Required local IRIS image is missing: " + args.image +
                         ". Obtain the official build-154 Community ARM64 archive "
                         "from InterSystems, load it with docker load -i <archive>, "
                         "then docker tag <loaded-image> " + args.image +
                         ". See INSTALL.md; no image download is attempted.")
    image = json.loads(result.stdout)[0]
    if ((image.get("Config", {}).get("Labels") or {}).get(
            "com.intersystems.platform-version") != "2026.3.0AI.154.0com"
            or image.get("Architecture") != "arm64"):
        raise ValueError("Use the verified official 2026.3.0AI.154.0 Community "
                         "(154U) ARM64 image; other builds/platforms are unverified")
    if command([*docker, "image", "inspect", args.gateway_image], capture=True).returncode:
        raise ValueError("Required local Web Gateway image is missing: " +
                         args.gateway_image + ". Follow INSTALL.md step 2 first.")
    if args.container and command(
            [*docker, "container", "inspect", args.container], capture=True).returncode == 0:
        raise ValueError("Container already exists; choose a new --container name. "
                         "Existing resources will not be replaced.")
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", args.api_port))
        except OSError as error:
            raise ValueError("Local API port is unavailable; choose another --api-port") from error


def child_environment() -> dict[str, str]:
    # trace_example gives process variables precedence over its env-file. Do not
    # let an existing live configuration replace these fresh replay credentials.
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith("SILENTSHIFT_")
                   and not key.endswith(("_API_KEY", "_TOKEN"))}
    # The existing verifier's first trace command also reads ROOT/.env. This
    # explicit empty value prevents an unrelated key there entering its process.
    environment["SILENTSHIFT_API_KEY"] = ""
    return environment


def private_environment(run: str) -> Path:
    base = ROOT / ".local" / "judge"
    if (ROOT / ".local").is_symlink() or base.is_symlink():
        raise ValueError("Private judge directory must not be a symlink")
    directory = base / run
    directory.mkdir(parents=True, mode=0o700, exist_ok=False)
    passwords: set[str] = set()
    while len(passwords) < 3:
        passwords.add(secrets.token_hex(24))
    reviewer, viewer, gateway = passwords
    values = {
        "SILENTSHIFT_IRIS_USERNAME": "ss-reviewer",
        "SILENTSHIFT_IRIS_PASSWORD": reviewer,
        "SILENTSHIFT_VIEWER_USERNAME": "ss-viewer",
        "SILENTSHIFT_VIEWER_PASSWORD": viewer,
        "SILENTSHIFT_GATEWAY_PASSWORD": gateway,
        "SILENTSHIFT_MODEL": "qwen3-silentshift:4b-instruct",
        "SILENTSHIFT_AGENT_WAIT_SECONDS": "120",
        "SILENTSHIFT_LLM_BASE_URL": "http://host.lima.internal:11434/v1/",
        "SILENTSHIFT_EMBED_BASE_URL": "http://host.lima.internal:11434/v1/",
        "SILENTSHIFT_EMBED_MODEL": "all-minilm:22m",
        "SILENTSHIFT_PROVIDER_MODE": "recorded-replay",
    }
    path = directory / "runtime.env"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write("".join(key + "=" + value + "\n" for key, value in values.items()))
    return path


def release_source(directory: Path, env: dict[str, str]) -> int:
    """Fetch the public release's tests/harness, never current-branch tests."""
    directory.mkdir(mode=0o700)
    git_env = {**env, "GIT_TERMINAL_PROMPT": "0",
               "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    git = ["git", "-C", str(directory)]
    for argv in (["git", "init", "--quiet", str(directory)],
                 [*git, "-c", "credential.helper=", "-c", "http.extraHeader=",
                  "fetch", "--depth", "1", REPOSITORY, RELEASE_COMMIT],
                 [*git, "checkout", "--quiet", "--detach", "FETCH_HEAD"]):
        result = command(argv, env=git_env)
        if result.returncode:
            print("Judge replay stopped while fetching the pinned release harness. "
                  "No install was attempted; retained directory: " + str(directory),
                  file=sys.stderr)
            return result.returncode
    head = command([*git, "rev-parse", "HEAD"], env=git_env, capture=True)
    if head.returncode or head.stdout.strip() != RELEASE_COMMIT:
        raise ValueError("Pinned release harness HEAD mismatch; no install was attempted")
    print("Verified release harness HEAD: " + RELEASE_COMMIT, flush=True)
    return 0


def run(args: argparse.Namespace) -> int:
    preflight(args)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    container = args.container or "silentshift-bonus-registry-judge-" + run_id
    env_file = private_environment(run_id)
    child = child_environment()
    print("Public 0.3.0 with pinned release harness; not current source runtime. "
          "Recorded replay only; no model calls. New test containers and private "
          "credentials are retained.", flush=True)
    source = env_file.parent / "source"
    print("Fetch the public release harness pinned to " + RELEASE_COMMIT + "...", flush=True)
    result = release_source(source, child)
    if result:
        return result
    installer = source / ".local/ipm/vendor/zpm-0.10.10.xml"
    stages = [
        ("Fetch the pinned official IPM installer", [sys.executable,
         str(source / "scripts/fetch_ipm.py"), "--output", str(installer)]),
        ("Install, start production, run native tests and first replay", [sys.executable,
         str(source / "scripts/verify_bonus_release.py"), "--source", "public-registry",
         "--install-latest", "--version", VERSION, "--execution-mode", "recorded-replay",
         "--container", container, "--api-port", str(args.api_port),
         "--context", args.context, "--vm-profile", args.vm_profile,
         "--image", args.image, "--gateway-image", args.gateway_image,
         "--env-file", str(env_file), "--execute"]),
        ("Repeat the API replay and print its Visual Trace URL", [sys.executable,
         str(source / "scripts/trace_example.py"), "--api",
         f"http://127.0.0.1:{args.api_port}/silentshift/api", "--context", args.context,
         "--container", container, "--env-file", str(env_file),
         "--output", str(env_file.parent / "second-replay.json")]),
    ]
    for index, (label, argv) in enumerate(stages):
        print(label + "...", flush=True)
        result = command(argv, env=child)
        if result.returncode:
            print("Judge replay stopped at: " + label +
                  ". Retained files: " + str(env_file.parent), file=sys.stderr)
            return result.returncode
        if index == 0:
            installer.chmod(0o644)
    print("Public native IPM " + VERSION + " verification finished. "
          "Keep private credentials local: " + str(env_file), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parser().parse_args(argv))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print("Judge replay stopped: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
