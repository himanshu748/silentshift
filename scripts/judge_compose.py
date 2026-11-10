#!/usr/bin/env python3
"""Start an isolated source Compose workbench and prove its keyless replay.

Only already-loaded images are used. The official IRIS EAP image is never
downloaded, built or uploaded. This checks current source, not public IPM.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from compose_support import compose_command
from judge_replay import (
    GATEWAY,
    IMAGE,
    child_environment,
    load_local_archive,
    unused_network_subnet,
    verified_image,
)
from verify_ipm_clean import available_network_subnet, space
from verify_native import Client

ROOT = Path(__file__).resolve().parents[1]
NODE = 'node:24-alpine'


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument('--context', default='colima-silentshift')
    value.add_argument('--vm-profile', default='silentshift')
    value.add_argument('--image', default=IMAGE)
    value.add_argument('--image-archive', type=Path)
    value.add_argument('--gateway-image', default=GATEWAY)
    value.add_argument('--node-image', default=NODE)
    value.add_argument('--project', help='New silentshift-judge-* project; default is unique')
    value.add_argument('--api-port', type=int, default=53033)
    value.add_argument('--web-port', type=int, default=5193)
    value.add_argument('--network-subnet', help='Unused RFC1918 IPv4 /24../28; otherwise inspect Docker IPAM')
    value.add_argument('--min-host-free-gib', type=float, default=1.8)
    value.add_argument('--min-vm-free-gib', type=float, default=3)
    return value


def command(argv: list[str], *, env: dict[str, str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True,
                          timeout=timeout, check=False)


def private_write(path: Path, value: str) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError('Private judge state already exists; no file was replaced')
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        stream.write(value)


def preflight(args: argparse.Namespace, env: dict[str, str]) -> tuple[list[str], list[str]]:
    if not re.fullmatch(r'silentshift-judge(?:-[a-z0-9]+)+', args.project):
        raise ValueError('Use a new project named silentshift-judge-<lowercase-suffix>')
    if not all(1024 <= port <= 65535 for port in (args.api_port, args.web_port)) or args.api_port == args.web_port:
        raise ValueError('Use two distinct unprivileged API and web ports')
    if (not all(math.isfinite(value) for value in (args.min_host_free_gib, args.min_vm_free_gib))
            or args.min_host_free_gib < 1.8 or args.min_vm_free_gib < 3):
        raise ValueError('Do not lower the 1.8 GiB host / 3 GiB VM safety floors')
    if shutil.which('docker') is None:
        raise ValueError('Docker CLI is missing; follow INSTALL.md before starting Compose')
    if shutil.which('git') is None:
        raise ValueError('Git CLI is missing; use the documented source checkout')
    cli = compose_command(env)
    if cli is None:
        raise ValueError('Modern Docker Compose is missing; install Compose 2.24+ first')
    version = command([*cli, 'version', '--short'], env=env)
    match = re.match(r'^v?(\d+)\.(\d+)', version.stdout.strip())
    if version.returncode or match is None or tuple(map(int, match.groups())) < (2, 24):
        raise ValueError('Use Docker Compose 2.24+ for bounded --wait startup')
    docker = ['docker', '--context', args.context]
    if command([*docker, 'info'], env=env).returncode:
        raise ValueError('Docker context is unavailable; start the documented Colima profile')
    if command([*docker, 'ps', '-aq', '--filter', 'label=com.docker.compose.project=' + args.project], env=env).stdout.strip():
        raise ValueError('This Compose project already exists; retain it and choose a new --project')
    present = command([*docker, 'image', 'inspect', args.image], env=env)
    if present.returncode and args.image_archive is not None:
        if not args.image_archive.is_file():
            raise ValueError('The supplied local official image archive was not found')
        load_local_archive(docker, args.image_archive, args.image)
        present = command([*docker, 'image', 'inspect', args.image], env=env)
    if present.returncode:
        raise ValueError('Official 154U ARM64 IRIS image is missing. Obtain it from InterSystems, '
                         'docker load -i <archive>, then tag it ' + IMAGE + '; no image is downloaded')
    verified_image(present.stdout)
    for image, description in ((args.gateway_image, 'Web Gateway'), (args.node_image, 'Node workbench')):
        if command([*docker, 'image', 'inspect', image], env=env).returncode:
            raise ValueError(description + ' image is missing; load/pull its documented public image first: ' + image)
    args.network_subnet = available_network_subnet(
        args.network_subnet or unused_network_subnet(docker), docker)
    space(args)  # Read-only Colima/host capacity guard; never prunes resources.
    for port in (args.api_port, args.web_port):
        with socket.socket() as probe:
            try:
                probe.bind(('127.0.0.1', port))
            except OSError as error:
                raise ValueError('Requested local judge port is in use; choose another port') from error
    return docker, cli


def private_environment(args: argparse.Namespace) -> tuple[Path, dict[str, str]]:
    base = ROOT / '.local' / 'judge-compose'
    if (ROOT / '.local').is_symlink() or base.is_symlink():
        raise ValueError('Private judge directory must not be a symlink')
    directory = base / args.project
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    passwords = [secrets.token_hex(24) for _ in range(3)]
    if len(set(passwords)) != 3:
        raise ValueError('Could not generate distinct private passwords')
    values = {
        'COMPOSE_PROJECT_NAME': args.project,
        'IRIS_IMAGE': args.image,
        'WEBGATEWAY_IMAGE': args.gateway_image,
        'NODE_IMAGE': args.node_image,
        'SILENTSHIFT_IRIS_USERNAME': 'ss-reviewer',
        'SILENTSHIFT_IRIS_PASSWORD': passwords[0],
        'SILENTSHIFT_VIEWER_USERNAME': 'ss-viewer',
        'SILENTSHIFT_VIEWER_PASSWORD': passwords[1],
        'SILENTSHIFT_GATEWAY_PASSWORD': passwords[2],
        'SILENTSHIFT_PROVIDER_MODE': 'recorded-replay',
        'SILENTSHIFT_PROVIDER': 'ollama',
        'SILENTSHIFT_API_KEY': '',
        'SILENTSHIFT_MODEL': 'qwen3-silentshift:4b-instruct',
        'SILENTSHIFT_AGENT_WAIT_SECONDS': '120',
        'SILENTSHIFT_LLM_BASE_URL': 'http://host.lima.internal:11434/v1/',
        'SILENTSHIFT_EMBED_BASE_URL': '',
        'SILENTSHIFT_EMBED_MODEL': 'all-minilm:22m',
        'SILENTSHIFT_JUDGE_API_PORT': str(args.api_port),
        'SILENTSHIFT_JUDGE_WEB_PORT': str(args.web_port),
        'SILENTSHIFT_JUDGE_SUBNET': args.network_subnet,
    }
    path = directory / 'runtime.env'
    private_write(path, '\n'.join(key + '=' + value for key, value in values.items()) + '\n')
    return path, values


def wait_for_api(api: str, values: dict[str, str]) -> dict:
    client = Client(api, values['SILENTSHIFT_IRIS_USERNAME'], values['SILENTSHIFT_IRIS_PASSWORD'])
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            request = Request(api + '/health', headers={'Accept': 'application/json', 'Authorization': client.auth})
            with client.opener.open(request, timeout=5) as response:
                raw = response.read(131073)
                if len(raw) > 131072:
                    raise ValueError('Native health response exceeded its bound')
                result = json.loads(raw)
                if response.status == 200 and isinstance(result, dict) and result.get('production', {}).get('running') is True:
                    return result
        except (OSError, ValueError):
            pass
        time.sleep(1)
    raise ValueError('The actual authenticated native API did not become ready')


def run(args: argparse.Namespace) -> int:
    env = child_environment()
    env['DOCKER_CONTEXT'] = args.context
    args.project = args.project or ('silentshift-judge-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
                                    + '-' + secrets.token_hex(3))
    docker, cli = preflight(args, env)
    env_file, values = private_environment(args)
    directory = env_file.parent
    child = {**env, **values}
    compose = [*cli, '--project-name', args.project, '--env-file', str(env_file),
               '-f', str(ROOT / 'compose.judge.yaml')]
    receipt = {'project': args.project, 'source': 'current checkout via read-only source mounts',
               'execution_mode': 'recorded-replay', 'fresh_inference': False,
               'published_package_install': False, 'passed': False,
               'resources_retained': True, 'automatic_cleanup': False}
    started = time.monotonic()

    def stage(argv: list[str], label: str, timeout: int = 300) -> subprocess.CompletedProcess:
        outcome = command(argv, env=child, timeout=timeout)
        private_write(directory / (label + '.log'), outcome.stdout + outcome.stderr)
        if outcome.returncode:
            raise ValueError('Judge command failed at ' + label + '; inspect its private log')
        return outcome

    try:
        head = stage(['git', 'rev-parse', 'HEAD'], '00-source-head').stdout.strip()
        if not re.fullmatch(r'[a-f0-9]{40}', head):
            raise ValueError('Could not identify the source checkout commit')
        receipt['source_commit'] = head
        # Quiet validation avoids resolved configuration (including secrets).
        stage([*compose, 'config', '--quiet'], '01-config')
        print('Starting the source Compose judge stack; recorded replay only...', flush=True)
        stage([*compose, 'up', '--detach', '--wait', '--wait-timeout', '300'], '02-up', 600)
        api = f'http://127.0.0.1:{args.api_port}/silentshift/api'
        health = wait_for_api(api, values)
        receipt['runtime'] = health.get('build')
        with urlopen(f'http://127.0.0.1:{args.web_port}/', timeout=15) as page:
            if page.status != 200:
                raise ValueError('The real workbench did not return HTTP 200')
        container = stage([*compose, 'ps', '-q', 'iris'], '03-container').stdout.strip()
        if not re.fullmatch(r'[a-f0-9]{12,64}', container):
            raise ValueError('Could not identify this project’s IRIS container')
        replay = directory / 'replay.json'
        outcome = stage([sys.executable, str(ROOT / 'scripts/trace_example.py'),
            '--api', api, '--env-file', str(env_file), '--context', args.context,
            '--container', container, '--output', str(replay)], '04-replay', 300)
        actual = json.loads(replay.read_text())
        if actual.get('passed') is not True or len(actual.get('checks', {})) != 12:
            raise ValueError('The unchanged native replay assertions did not all pass')
        receipt.update({'passed': True, 'container': container, 'api_url': api,
            'workbench_url': f'http://127.0.0.1:{args.web_port}/',
            'session_id': actual['session_id'], 'visual_trace_url': actual['visual_trace_url'],
            'checks_passed': sum(actual['checks'].values()), 'checks_total': len(actual['checks']),
            'replay_receipt': str(replay.relative_to(ROOT)),
            'image_ids': {name: json.loads(stage([*docker, 'image', 'inspect', image], '05-image-' + name).stdout)[0]['Id']
                          for name, image in [('iris', args.image), ('gateway', args.gateway_image), ('web', args.node_image)]}})
        print(outcome.stdout.rstrip(), flush=True)
        print('Workbench: ' + receipt['workbench_url'], flush=True)
        print('Private login/config file (values are not printed): ' + str(env_file), flush=True)
        print('Retained Compose project: ' + args.project + '; no automatic cleanup', flush=True)
        return 0
    finally:
        receipt['elapsed_seconds'] = round(time.monotonic() - started, 3)
        private_write(directory / 'receipt.json', json.dumps(receipt, indent=2) + '\n')


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return run(args)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print('Compose judge path stopped: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
