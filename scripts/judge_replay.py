#!/usr/bin/env python3
"""Install public native IPM 0.3.0 and run two keyless recorded replays.

Requires running Colima and the official build-154U ARM64 and Web Gateway
images. An explicitly supplied local IRIS archive can be loaded and retagged.
Creates new isolated test containers and private local test
credentials; retains them for inspection. No image pull, fresh model inference,
publication, or existing application configuration change is performed. This
checks the published native package with pinned compatible release tests/replay
assertions and the current checkout's install orchestration, not current-source
runtime changes or additional native tests. It uses Docker, not Compose.
By default it selects a Docker-IPAM-disjoint /28 inside 10.253.0.0/16.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

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
    p.add_argument("--network-subnet", help="Explicit unused RFC1918 IPv4 /24../28; default selects a disjoint /28 inside 10.253.0.0/16")
    p.add_argument("--image", default=IMAGE)
    p.add_argument("--image-archive", type=Path,
                   help="Load and verify this local official archive if --image is absent; never downloads an image")
    p.add_argument("--gateway-image", default=GATEWAY)
    p.add_argument("--api-port", type=int, default=52843)
    p.add_argument("--container", help="New silentshift-bonus-registry-* name")
    return p


def command(argv: list[str], *, env: dict[str, str] | None = None,
            capture: bool = False, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=ROOT, env=env, text=True,
                          capture_output=capture, check=False,
                          timeout=timeout if timeout is not None else (30 if capture else 1200))


def verified_image(text: str) -> dict:
    records = json.loads(text)
    if not isinstance(records, list) or len(records) != 1 or not isinstance(records[0], dict):
        raise ValueError("Cannot identify the loaded IRIS image; no runtime was started")
    image = records[0]
    if ((image.get("Config", {}).get("Labels") or {}).get(
            "com.intersystems.platform-version") != "2026.3.0AI.154.0com"
            or image.get("Architecture") != "arm64"):
        raise ValueError("Use the verified official 2026.3.0AI.154.0 Community "
                         "(154U) ARM64 image; other builds/platforms are unverified")
    return image


def load_local_archive(docker: list[str], archive: Path, tag: str) -> None:
    print("Load the supplied local archive and verify build/architecture before retagging...", flush=True)
    loaded = command([*docker, "load", "--input", str(archive.resolve())],
                     capture=True, timeout=1200)
    if loaded.returncode:
        raise ValueError("Could not load the supplied local IRIS archive; no runtime was started")
    matches: dict[str, str] = {}
    for reference in re.findall(r"^Loaded image(?: ID)?: (.+)$", loaded.stdout, re.MULTILINE):
        result = command([*docker, "image", "inspect", reference.strip()], capture=True)
        if result.returncode:
            continue
        try:
            image = verified_image(result.stdout)
        except ValueError:
            continue
        matches[image.get("Id", reference)] = reference.strip()
    if len(matches) != 1:
        raise ValueError("The archive did not identify exactly one verified build-154 Community "
                         "ARM64 image. Tag the intended image explicitly; no runtime was started.")
    result = command([*docker, "image", "tag", next(iter(matches.values())), tag], capture=True)
    if result.returncode:
        raise ValueError("Could not retag the verified image as " + tag)


def unused_network_subnet(docker: list[str]) -> str:
    """Select from one read-only IPAM snapshot; never try network mutations."""
    listing = command([*docker, "network", "ls", "--quiet"], capture=True)
    if listing.returncode:
        raise ValueError("Cannot list Docker networks for test subnet selection; no network was created")
    identifiers = listing.stdout.split()
    occupied = []
    if identifiers:
        inspected = command([*docker, "network", "inspect", *identifiers], capture=True)
        if inspected.returncode:
            raise ValueError("Cannot inspect Docker IPAM for test subnet selection; no network was created")
        try:
            networks = json.loads(inspected.stdout)
            if not isinstance(networks, list):
                raise ValueError("Expected network list")
            for network in networks:
                if not isinstance(network, dict) or "IPAM" not in network:
                    raise ValueError("Expected Docker IPAM metadata")
                for config in ((network.get("IPAM") or {}).get("Config") or []):
                    if config.get("Subnet"):
                        subnet = ipaddress.ip_network(config["Subnet"], strict=False)
                        if subnet.version == 4:
                            occupied.append(subnet)
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError("Cannot read Docker IPAM snapshot for test subnet selection; "
                             "no network was created") from error
    pool = ipaddress.ip_network("10.253.0.0/16")
    for candidate in pool.subnets(new_prefix=28):
        if not any(candidate.overlaps(existing) for existing in occupied):
            return str(candidate)
    raise ValueError("No unused /28 remains in 10.253.0.0/16. Supply an inspected, "
                     "nonoverlapping --network-subnet; no network was created")


def preflight(args: argparse.Namespace) -> None:
    if args.network_subnet is not None:
        try:
            network = ipaddress.ip_network(args.network_subnet, strict=True)
            private = [ipaddress.ip_network(block) for block in
                       ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
            valid = (network.version == 4 and 24 <= network.prefixlen <= 28
                     and any(network.subnet_of(block) for block in private))
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("--network-subnet requires a canonical RFC1918 IPv4 /24../28")
    if not 1024 <= args.api_port <= 65535:
        raise ValueError("Use an unprivileged --api-port between 1024 and 65535")
    if args.container and not re.fullmatch(
            r"silentshift-bonus-registry-[a-z0-9-]{1,35}", args.container):
        raise ValueError("Use a new silentshift-bonus-registry-* container name")
    if args.image_archive is not None and not args.image_archive.is_file():
        raise ValueError("Local --image-archive file was not found; obtain the official archive yourself")
    if shutil.which("docker") is None:
        raise ValueError("Docker CLI is missing. Install it, then start Colima: "
                         "colima start --profile " + args.vm_profile)
    if shutil.which("git") is None:
        raise ValueError("Git CLI is missing. Install Git to fetch the pinned public release harness.")
    docker = ["docker", "--context", args.context]
    if command([*docker, "info"], capture=True).returncode:
        raise ValueError("Docker context is unavailable: " + args.context +
                         ". Start Colima: colima start --profile " + args.vm_profile)
    if args.network_subnet is None:
        args.network_subnet = unused_network_subnet(docker)
        print("Selected private test subnet: " + args.network_subnet +
              " (read-only Docker IPAM snapshot; no network created yet)", flush=True)
    result = command([*docker, "image", "inspect", args.image], capture=True)
    if result.returncode and args.image_archive is not None:
        load_local_archive(docker, args.image_archive, args.image)
        result = command([*docker, "image", "inspect", args.image], capture=True)
    if result.returncode:
        raise ValueError("Required local IRIS image is missing: " + args.image +
                         ". Obtain the official build-154 Community ARM64 archive "
                         "from InterSystems, load it with docker load -i <archive>, "
                         "then docker tag <loaded-image> " + args.image +
                         ". See INSTALL.md; no image download is attempted.")
    verified_image(result.stdout)
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
    """Fetch the public release's native tests/replay, never branch assertions."""
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
    print("Public 0.3.0 with pinned release tests/replay and current install orchestration; "
          "not current source runtime. "
          "Recorded replay only; no model calls. New test containers and private "
          "credentials are retained.", flush=True)
    source = env_file.parent / "source"
    print("Fetch the public release harness pinned to " + RELEASE_COMMIT + "...", flush=True)
    result = release_source(source, child)
    if result:
        return result
    installer = ROOT / ".local/ipm/vendor/zpm-0.10.10.xml"
    stages = [
        ("Fetch the pinned official IPM installer", [sys.executable,
         str(ROOT / "scripts/fetch_ipm.py"), "--output", str(installer)]),
        ("Install, start production, run native tests and first replay", [sys.executable,
         str(ROOT / "scripts/verify_bonus_release.py"), "--source", "public-registry",
         "--verification-source", str(source),
         "--install-latest", "--version", VERSION, "--execution-mode", "recorded-replay",
         "--container", container, "--api-port", str(args.api_port),
         "--context", args.context, "--vm-profile", args.vm_profile,
         "--image", args.image, "--gateway-image", args.gateway_image,
         "--env-file", str(env_file), "--execute",
         *(["--network-subnet", args.network_subnet] if args.network_subnet else [])]),
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
