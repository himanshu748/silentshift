#!/usr/bin/env python3
"""Install the native source using a locally loaded EAP image. No model calls."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from compose_support import compose_command

ROOT = Path(__file__).resolve().parents[1]


def read_env(path: Path) -> dict[str, str]:
    """Read literal KEY=value entries; never source or execute an env file."""
    values = dict(os.environ)
    if path.exists():
        for number, raw in enumerate(path.read_text().splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            key, sep, value = line.partition('=')
            if not sep or not re.fullmatch(r'[A-Z][A-Z0-9_]*', key):
                raise ValueError(f'Invalid environment entry on line {number}')
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in '\"\'':
                value = value[1:-1]
            values.setdefault(key, value)
    return values


def main() -> int:
    if sys.version_info < (3, 10):
        print("Use Python 3.10+ or uv run python scripts/bootstrap.py", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image-archive', type=Path, help='Official architecture-specific EAP archive to docker load locally')
    args = parser.parse_args()
    env = read_env(ROOT / '.env')
    required = ('IRIS_IMAGE', 'SILENTSHIFT_IRIS_USERNAME', 'SILENTSHIFT_IRIS_PASSWORD',
                'SILENTSHIFT_VIEWER_USERNAME', 'SILENTSHIFT_VIEWER_PASSWORD', 'SILENTSHIFT_GATEWAY_PASSWORD')
    missing = [name for name in required if not env.get(name)]
    if missing:
        print('Missing configuration: ' + ', '.join(missing), file=sys.stderr)
        return 2
    for name in ('SILENTSHIFT_IRIS_PASSWORD', 'SILENTSHIFT_VIEWER_PASSWORD', 'SILENTSHIFT_GATEWAY_PASSWORD'):
        if len(env[name]) < 12 or any(ord(char) < 32 for char in env[name]):
            print(f'{name} must be at least 12 characters without control characters', file=sys.stderr)
            return 2
    if env['SILENTSHIFT_IRIS_USERNAME'].lower() == env['SILENTSHIFT_VIEWER_USERNAME'].lower():
        print('Viewer and reviewer accounts must be distinct', file=sys.stderr)
        return 2
    if '2026.3.0AI.154.0' not in env['IRIS_IMAGE']:
        print('IRIS_IMAGE must identify the required 2026.3.0AI.154.0 build', file=sys.stderr)
        return 2
    if not (ROOT / '.env').exists():
        print('Create .env from .env.example first; Compose uses the same file', file=sys.stderr)
        return 2
    wait = env.get('SILENTSHIFT_AGENT_WAIT_SECONDS', '60')
    if not re.fullmatch(r'[0-9]{1,3}', wait) or not 10 <= int(wait) <= 120:
        print('SILENTSHIFT_AGENT_WAIT_SECONDS must be an integer from10 to120', file=sys.stderr)
        return 2

    def run(arguments: list[str], *, data: str | None = None, quiet: bool = False, check: bool = True) -> subprocess.CompletedProcess:
        # Captured failures are deliberately not echoed: container diagnostics
        # and environment expansion can reveal secrets. Named stage is printed.
        return subprocess.run(arguments, cwd=ROOT, env=env, input=data, text=True,
                              capture_output=quiet, check=check)

    if shutil.which('docker') is None:
        print('Docker CLI is unavailable. Install/start Docker or Colima before native bootstrap.', file=sys.stderr)
        return 2
    compose_cli = compose_command(env)
    if compose_cli is None:
        print('Modern Docker Compose is unavailable. Configure docker compose or docker-compose (version 2+) before bootstrap.', file=sys.stderr)
        return 2
    daemon_available = run(['docker', 'info', '--format', '{{.ServerVersion}}'], quiet=True, check=False)
    if daemon_available.returncode:
        print('Docker daemon is unavailable. Start Docker or Colima, then rerun bootstrap.', file=sys.stderr)
        return 2
    if args.image_archive:
        if not args.image_archive.is_file():
            print('The specified EAP archive does not exist', file=sys.stderr)
            return 2
        run(['docker', 'load', '-i', str(args.image_archive.resolve())], quiet=True)
    loaded = run(['docker', 'image', 'inspect', env['IRIS_IMAGE']], quiet=True, check=False)
    if loaded.returncode:
        print('Required IRIS image is not loaded. Download the official EAP kit, then use --image-archive.', file=sys.stderr)
        return 2
    compose = compose_cli + ['--env-file', '.env']
    run(compose + ['config', '--quiet'], quiet=True)
    local = ROOT / '.local' / 'gateway'
    local.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Separate writable hand-off directory; the rest of the checkout remains
    # read-only in IRIS. Bootstrap does not create any incoming partner files.
    (ROOT / '.local' / 'partner-inbox').mkdir(parents=True, exist_ok=True, mode=0o700)
    ini = local / 'CSP.ini'
    password = env['SILENTSHIFT_GATEWAY_PASSWORD']
    ini.write_text('[SYSTEM]\nSystem_Manager=127.0.0.1\nDefault_Server=IRIS\n'
                   'Server_Response_Timeout=180\nQueued_Request_Timeout=180\n'
                   '[SYSTEM_INDEX]\nIRIS=Enabled\n[IRIS]\nIp_Address=iris\nTCP_Port=1972\n'
                   'Minimum_Server_Connections=2\nMaximum_Session_Connections=8\n'
                   'Username=CSPSystem\nPassword=' + password + '\nConnection_Security_Level=0\n'
                   '[APP_PATH_INDEX]\n/silentshift=Enabled\n/silentshift-provider=Enabled\n/csp=Enabled\n'
                   '[APP_PATH:/silentshift]\nDefault_Server=IRIS\n'
                   '[APP_PATH:/silentshift-provider]\nDefault_Server=IRIS\n'
                   '[APP_PATH:/csp]\nDefault_Server=IRIS\n')
    ini.chmod(0o600)
    print('Starting locally loaded IRIS runtime...')
    run(compose + ['up', '-d', 'iris'], quiet=True)
    session = compose + ['exec', '-T', 'iris', 'iris', 'session', 'IRIS', '-U', '%SYS']
    for _ in range(60):
        ready = run(session, data='write "SILENTSHIFT_READY",! halt\n', quiet=True, check=False)
        if ready.returncode == 0 and 'SILENTSHIFT_READY' in ready.stdout:
            break
        time.sleep(2)
    else:
        print('IRIS startup did not become ready. Inspect the local container status.', file=sys.stderr)
        return 1
    probe = run(session, data='write "SILENTSHIFT_NAMESPACE=",##class(Config.Namespaces).Exists("SILENTSHIFT"),! halt\n', quiet=True)
    if 'SILENTSHIFT_NAMESPACE=1' not in probe.stdout:
        print('Creating the interoperability namespace...')
        run(compose + ['exec', '-T', 'iris', 'iris', 'merge', 'IRIS', '/opt/silentshift/docker/merge.cpf'], quiet=True)
    print('Loading, compiling and installing native classes (no model invocation)...')
    result = run(session, data=(ROOT / 'docker' / 'bootstrap.script').read_text(), quiet=True, check=False)
    if result.returncode or 'SILENTSHIFT_BOOTSTRAP_OK' not in result.stdout:
        # Source compilation has no environment values. Save diagnostics to an
        # ignored local file for operator inspection without leaking into chat.
        log = ROOT / '.local' / 'bootstrap.log'
        log.write_text(result.stdout + result.stderr)
        log.chmod(0o600)
        print('Native bootstrap failed. Inspect .local/bootstrap.log locally; do not publish it.', file=sys.stderr)
        return 1
    print('Starting the separate Web Gateway...')
    run(compose + ['up', '-d', 'gateway'], quiet=True)
    print('Native installation command completed. Verify authenticated health and run scripts/verify_native.py before claiming native readiness.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError):
        print('Bootstrap failed at a local configuration/container command; inspect configuration and Docker status. No model invocation was requested.', file=sys.stderr)
        raise SystemExit(1)
