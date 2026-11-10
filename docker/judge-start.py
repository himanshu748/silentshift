"""Bootstrap this dedicated native judge instance after iris-main starts IRIS.

Installs source and test inspection helpers only. Never submits an order or
invokes a model. The host launcher later uses the real authenticated REST path.
"""
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
from pathlib import Path

ROOT = Path('/opt/silentshift')
STATE = Path('/silentshift-state')


def command(argv: list[str], label: str, data: str | None = None) -> str:
    result = subprocess.run(argv, input=data, text=True, capture_output=True,
                            timeout=300, check=False)
    log = STATE / (label + '.log')
    log.write_text(result.stdout + result.stderr)
    log.chmod(0o600)
    if result.returncode:
        raise ValueError('Native command failed at ' + label)
    return result.stdout


def session(namespace: str, text: str, label: str, marker: str) -> str:
    output = command(['iris', 'session', 'IRIS', '-U', namespace], label, text + '\nhalt\n')
    if marker not in output.splitlines():
        raise ValueError('Native marker missing at ' + label)
    return output


def bootstrap(values: dict[str, str]) -> None:
    if platform.machine() not in {'aarch64', 'arm64'}:
        raise ValueError('Only the tested ARM64 build-154 image is accepted')
    project = values.get('SILENTSHIFT_JUDGE_PROJECT', '')
    if not re.fullmatch(r'silentshift-judge(?:-[a-z0-9]+)*', project):
        raise ValueError('A dedicated judge project is required')
    if (values.get('SILENTSHIFT_PROVIDER_MODE') != 'recorded-replay'
            or values.get('SILENTSHIFT_API_KEY') or values.get('SILENTSHIFT_EMBED_BASE_URL')):
        raise ValueError('Judge bootstrap requires keyless replay without embeddings')
    ready = STATE / 'bootstrap.ok'
    if ready.exists():
        ready.unlink()  # This profile's disposable readiness marker, never database data.
    probe = session('%SYS',
        'write "JUDGE_VERSION=",$zversion,!\n'
        'write "JUDGE_NAMESPACE=",##class(Config.Namespaces).Exists("SILENTSHIFT"),!\n'
        'write "JUDGE_PROBE_OK",!', '01-probe', 'JUDGE_PROBE_OK')
    version = next((line.split('=', 1)[1] for line in probe.splitlines()
                    if line.startswith('JUDGE_VERSION=')), '')
    if '2026.3.0AI (Build 154U)' not in version or 'ARM64' not in version:
        raise ValueError('The running image is not the verified 154U ARM64 runtime')
    exists = 'JUDGE_NAMESPACE=1' in probe.splitlines()
    if exists:
        session('SILENTSHIFT',
            'if $get(^SilentShift.Config("JudgeComposeOwner"))\'=$system.Util.GetEnviron("SILENTSHIFT_JUDGE_PROJECT") halt\n'
            'write "JUDGE_OWNED_NAMESPACE_OK",!', '02-owner', 'JUDGE_OWNED_NAMESPACE_OK')
    else:
        command(['iris', 'merge', 'IRIS', str(ROOT / 'docker/merge.cpf')], '02-namespace')
        session('SILENTSHIFT',
            'set ^SilentShift.Config("JudgeComposeOwner")=$system.Util.GetEnviron("SILENTSHIFT_JUDGE_PROJECT")\n'
            'write "JUDGE_OWNED_NAMESPACE_OK",!', '02-owner', 'JUDGE_OWNED_NAMESPACE_OK')
    session('%SYS',
        'set properties("Enabled")=1\n'
        'set sc=##class(Security.Services).Modify("%Service_CallIn",.properties)\n'
        'if $system.Status.IsError(sc) halt\nwrite "JUDGE_PYTHON_OK",!',
        '03-python', 'JUDGE_PYTHON_OK')
    session('%SYS', (ROOT / 'docker/bootstrap.script').read_text(),
            '04-source', 'SILENTSHIFT_BOOTSTRAP_OK')
    session('SILENTSHIFT',
        'set sc=$system.OBJ.Load("/opt/silentshift/tests/iris/ProviderChecks.cls","ck")\n'
        'if $system.Status.IsError(sc) halt\n'
        'write "JUDGE_TRACE_INSPECTOR_OK",!', '05-inspector', 'JUDGE_TRACE_INSPECTOR_OK')
    ready.write_text(json.dumps({'project': project, 'runtime': version,
        'execution_mode': 'recorded-replay', 'fresh_inference': False,
        'source_installed': True, 'order_submitted': False}) + '\n')
    ready.chmod(0o600)
    print('JUDGE_NATIVE_SOURCE_READY: recorded-replay; no order or model call requested', flush=True)


if __name__ == '__main__':
    try:
        bootstrap(dict(os.environ))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print('Judge source bootstrap stopped: ' + str(error) +
              '; inspect this project’s private judge-state logs', flush=True)
        raise SystemExit(1) from None
