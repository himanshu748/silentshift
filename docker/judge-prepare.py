"""Prepare only a new Compose project's private Gateway state volume."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

STATE = Path('/silentshift-state')
ROOT = Path('/opt/silentshift')
OWNER = 51773
PASSWORD_KEYS = ('SILENTSHIFT_IRIS_PASSWORD', 'SILENTSHIFT_VIEWER_PASSWORD',
                 'SILENTSHIFT_GATEWAY_PASSWORD')


def validate(values: dict[str, str]) -> None:
    for key in PASSWORD_KEYS:
        value = values.get(key, '')
        if len(value) < 12 or any(ord(c) < 32 for c in value):
            raise ValueError(key + ' must be at least 12 characters without control characters')
    if len({values[key] for key in PASSWORD_KEYS}) != len(PASSWORD_KEYS):
        raise ValueError('Use three distinct private application passwords')
    names = [values.get(key, '') for key in
             ('SILENTSHIFT_IRIS_USERNAME', 'SILENTSHIFT_VIEWER_USERNAME')]
    if any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', name) for name in names):
        raise ValueError('Use explicit reviewer and viewer usernames')
    if names[0].lower() == names[1].lower():
        raise ValueError('Viewer and reviewer accounts must be distinct')
    if not re.fullmatch(r'silentshift-judge(?:-[a-z0-9]+)*', values.get('SILENTSHIFT_JUDGE_PROJECT', '')):
        raise ValueError('Use a dedicated silentshift-judge project name')
    if values.get('SILENTSHIFT_PROVIDER_MODE') != 'recorded-replay':
        raise ValueError('The judge Compose stack supports recorded-replay only')
    if values.get('SILENTSHIFT_API_KEY') or values.get('SILENTSHIFT_EMBED_BASE_URL'):
        raise ValueError('The judge Compose stack accepts no provider key or embedding endpoint')


def private_file(path: Path, value: str) -> None:
    if path.is_symlink():
        raise ValueError('Judge state files must not be symlinks')
    path.write_text(value)
    path.chmod(0o600)
    os.chown(path, OWNER, OWNER)


def prepare(values: dict[str, str]) -> None:
    validate(values)
    STATE.mkdir(exist_ok=True)
    if STATE.is_symlink():
        raise ValueError('Judge state must be its dedicated volume')
    fingerprint = hashlib.sha256(json.dumps({key: values[key] for key in
        (*PASSWORD_KEYS, 'SILENTSHIFT_IRIS_USERNAME', 'SILENTSHIFT_VIEWER_USERNAME',
         'SILENTSHIFT_JUDGE_PROJECT')}, sort_keys=True).encode()).hexdigest()
    marker = STATE / 'configuration.sha256'
    if marker.exists() and marker.read_text().strip() != fingerprint:
        raise ValueError('This judge volume belongs to different configuration; retain it and use a new project')
    if any(STATE.iterdir()) and not marker.exists():
        raise ValueError('Refusing an unrecognized nonempty judge state volume')
    STATE.chmod(0o700)
    os.chown(STATE, OWNER, OWNER)
    private_file(STATE / 'CSP.conf', (ROOT / 'docker/CSP.conf').read_text())
    private_file(STATE / 'CSP.ini',
        '[SYSTEM]\nSystem_Manager=127.0.0.1\nDefault_Server=IRIS\n'
        'Server_Response_Timeout=180\nQueued_Request_Timeout=180\n'
        '[SYSTEM_INDEX]\nIRIS=Enabled\n[IRIS]\nIp_Address=iris\nTCP_Port=1972\n'
        'Minimum_Server_Connections=2\nMaximum_Session_Connections=8\n'
        'Username=CSPSystem\nPassword=' + values['SILENTSHIFT_GATEWAY_PASSWORD'] + '\n'
        'Connection_Security_Level=0\n[APP_PATH_INDEX]\n/silentshift=Enabled\n'
        '/silentshift-provider=Enabled\n/csp=Enabled\n'
        '[APP_PATH:/silentshift]\nDefault_Server=IRIS\n'
        '[APP_PATH:/silentshift-provider]\nDefault_Server=IRIS\n'
        '[APP_PATH:/csp]\nDefault_Server=IRIS\n')
    private_file(marker, fingerprint + '\n')
    print('JUDGE_PRIVATE_GATEWAY_CONFIG_READY', flush=True)


if __name__ == '__main__':
    try:
        prepare(dict(os.environ))
    except (OSError, ValueError) as error:
        # Every validation error is a named invariant, never a supplied value.
        print('Judge preparation stopped: ' + str(error), flush=True)
        raise SystemExit(1) from None
