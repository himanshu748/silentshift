#!/usr/bin/env python3
"""Plan, or explicitly execute, a clean offline IPM install on a fresh local IRIS.

Default mode is read-only. --execute creates new uniquely named resources only;
it never changes, stops or removes an existing container, network or volume.
The official image and pinned IPM installer must already be available locally.
No publishing, registry server, image download or model call is implicit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from bootstrap import read_env
from fetch_ipm import SHA256, SIZE, VERSION
from inspect_ipm import inspect
from package_ipm import ROOT
from verify_ipm_native import TABLES, literal

GIB = 1024 ** 3
RELEASE = '/home/irisowner/silentshift-ipm-release'
RUNTIME_KEYS = ('SILENTSHIFT_IRIS_USERNAME', 'SILENTSHIFT_IRIS_PASSWORD',
    'SILENTSHIFT_VIEWER_USERNAME', 'SILENTSHIFT_VIEWER_PASSWORD', 'SILENTSHIFT_GATEWAY_PASSWORD',
    'SILENTSHIFT_MODEL', 'SILENTSHIFT_AGENT_WAIT_SECONDS', 'SILENTSHIFT_LLM_BASE_URL',
    'SILENTSHIFT_EMBED_BASE_URL', 'SILENTSHIFT_EMBED_MODEL')


def private_write(path: Path, text: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(text)


def command(arguments: list[str], log: Path | None = None, *, data: str | None = None,
        timeout: int = 900, env: dict | None = None, check: bool = True):
    result = subprocess.run(arguments, input=data, text=True, capture_output=True,
        timeout=timeout, env=env, cwd=ROOT, umask=0o077)
    if log:
        private_write(log, result.stdout + result.stderr)
    if check and result.returncode:
        raise RuntimeError('Command failed' + (f'; inspect private {log.name}' if log else ' during preflight'))
    return result


def space(args, *, enforce=True) -> dict:
    # df reports blocks inside the VM; host APFS space is a separate constraint.
    result = command(['colima', 'ssh', '--profile', args.vm_profile, '--',
        'df', '-Pk', '/var/lib/docker'], timeout=30)
    rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
    vm_free = int(rows[-1][3]) * 1024
    host_free = shutil.disk_usage(ROOT).free
    if enforce and (host_free < args.min_host_free_gib * GIB or vm_free < args.min_vm_free_gib * GIB):
        raise ValueError('Insufficient free space; retain existing files/volumes and arrange space before retrying')
    return {'host_free_bytes': host_free, 'vm_docker_free_bytes': vm_free,
        'host_floor_gib': args.min_host_free_gib, 'vm_floor_gib': args.min_vm_free_gib}


def runtime_environment(args) -> dict:
    values = read_env(args.env_file)
    missing = [name for name in RUNTIME_KEYS[:5] if not values.get(name)]
    if missing:
        raise ValueError('Missing runtime environment variables: ' + ', '.join(missing))
    for name in RUNTIME_KEYS:
        value = values.get(name, '')
        if any(ord(char) < 32 for char in value) or '\\' in value or value.startswith(('"', "'")):
            raise ValueError('Runtime environment requires literal, single-line values: ' + name)
    for name in RUNTIME_KEYS[:5]:
        if name.endswith('PASSWORD') and len(values[name]) < 12:
            raise ValueError('Runtime password must have at least 12 characters: ' + name)
    if values[RUNTIME_KEYS[0]].lower() == values[RUNTIME_KEYS[2]].lower():
        raise ValueError('Runtime viewer and reviewer identities must be distinct')
    for name, expected in {'SILENTSHIFT_MODEL': 'qwen3-silentshift:4b-instruct',
            'SILENTSHIFT_EMBED_MODEL': 'all-minilm:22m',
            'SILENTSHIFT_AGENT_WAIT_SECONDS': '120'}.items():
        if values.get(name) != expected:
            raise ValueError('Use the tested local runtime configuration: ' + name + '=' + expected)
    # This driver is local only. Missing/remote endpoints must not fall through
    # to a provider default when setup or the optional native verifier runs.
    for name in ('SILENTSHIFT_LLM_BASE_URL', 'SILENTSHIFT_EMBED_BASE_URL'):
        endpoint = values.get(name, '')
        parsed = urlparse(endpoint)
        if (parsed.scheme != 'http' or parsed.hostname not in {'host.lima.internal',
                'host.docker.internal', 'ollama', 'localhost', '127.0.0.1'}
                or parsed.port != 11434 or parsed.username or parsed.password
                or parsed.query or parsed.fragment):
            raise ValueError('Configure an explicit local Ollama endpoint: ' + name)
    return {key: values[key] for key in RUNTIME_KEYS if values.get(key)}


def preflight(args) -> dict:
    if not re.fullmatch(r'silentshift-ipm-clean-[a-z0-9][a-z0-9_.-]{0,60}', args.container):
        raise ValueError('Choose a new container name beginning silentshift-ipm-clean-')
    if args.allow_model_calls and not args.activate_runtime:
        raise ValueError('--allow-model-calls requires --activate-runtime')
    if not 1024 <= args.api_port <= 65535:
        raise ValueError('Use an unprivileged localhost API port')
    if (not all(math.isfinite(value) for value in (args.min_host_free_gib, args.min_vm_free_gib))
            or args.min_host_free_gib < 1.8 or args.min_vm_free_gib < 3):
        raise ValueError('Do not lower the 1.8 GiB host / 3 GiB VM safety floors')
    boundary = inspect(args.archive, args.source)
    vendor = args.vendor
    if (not vendor.is_file() or vendor.is_symlink() or vendor.stat().st_size != SIZE
            or hashlib.sha256(vendor.read_bytes()).hexdigest() != SHA256):
        raise ValueError('Pinned IPM installer is absent or mismatched; no download is attempted')
    docker = ['docker', '--context', args.context]
    image = json.loads(command([*docker, 'image', 'inspect', args.image], timeout=30).stdout)[0]
    labels = image.get('Config', {}).get('Labels') or {}
    if labels.get('com.intersystems.platform-version') != '2026.3.0AI.154.0com':
        raise ValueError('Loaded image is not the expected official Community build154')
    for name in (args.container, args.container + '-gateway'):
        existing = command([*docker, 'container', 'inspect', name], timeout=30, check=False)
        if existing.returncode == 0 and not (args.resume_pristine and name == args.container):
            raise ValueError('A target container already exists; choose a fresh name')
        if args.resume_pristine and name == args.container:
            if existing.returncode:
                raise ValueError('The pristine container to resume does not exist')
            prior = ROOT / '.local/ipm/clean-runs' / args.container
            original = json.loads((prior / 'plan.json').read_text())
            identity = json.loads(existing.stdout)[0]
            created_id = (prior / '01-create.log').read_text().strip()
            if (identity.get('Id') != created_id or identity.get('Image') != image['Id']
                    or identity.get('Config', {}).get('Labels', {}).get('silentshift.scope') != 'clean-ipm-verification'
                    or original.get('archive', {}).get('artifact_sha256') != boundary['artifact_sha256']
                    or 'SS_PRISTINE_OK' not in (prior / '05-pristine.log').read_text().splitlines()):
                raise ValueError('Existing container does not match the original pristine verification attempt')
    if command([*docker, 'network', 'inspect', args.container], timeout=30, check=False).returncode == 0:
        raise ValueError('A target network already exists; choose a fresh name')
    if args.activate_runtime:
        runtime_environment(args)
        command([*docker, 'image', 'inspect', args.gateway_image], timeout=30)
    return {'kind': 'clean-local-filesystem-ipm-install-plan',
        'archive': boundary, 'image_id': image['Id'], 'architecture': image['Architecture'],
        'image_version': labels['com.intersystems.platform-version'], 'namespace': 'SILENTSHIFT',
        'container': args.container, 'space': space(args),
        'install_command': 'install LocalArchive/silentshift ' + boundary['version'] + ' -synchronous',
        'new_persistent_volumes': 0, 'source_mounts': 0, 'network_during_install': 'none',
        'estimated_extra_disk_gib': '0.8-1.3; estimate, not a measured bound',
        'activate_runtime': args.activate_runtime, 'native_five_requested': args.allow_model_calls,
        'resume_pristine': args.resume_pristine,
        'executed': False, 'clean_install_verified': False, 'registry_published': False}


def unpack(archive: Path, destination: Path) -> None:
    # inspect() must have succeeded first: bounded regular files, canonical name
    # uniqueness, exact allowlist and metadata, no traversal or links/devices.
    with tarfile.open(archive, 'r:gz') as package:
        members = [member for member in package if member.isfile()]
        manifest = next(member for member in members if PurePosixPath(member.name).name == 'module.xml')
        prefix = PurePosixPath(manifest.name).parent
        for member in members:
            relative = PurePosixPath(member.name).relative_to(prefix)
            target = destination.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = package.extractfile(member)
            assert stream is not None
            with target.open('xb') as output:
                shutil.copyfileobj(stream, output)
            target.chmod(0o644)


def execute(args, plan: dict) -> dict:
    output = ROOT / '.local/ipm/clean-runs' / args.container
    if args.resume_pristine:
        output = output / ('resume-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    output.mkdir(parents=True, mode=0o700)
    output.chmod(0o700)
    private_write(output / 'plan.json', json.dumps(plan, indent=2) + '\n')
    docker = ['docker', '--context', args.context]
    container = args.container
    phase = 'preparing input'
    private_write(output / 'resource-state.json', json.dumps({
        'container': container, 'gateway': container + '-gateway', 'network': container,
        'automatic_cleanup': False, 'existing_runtime_modified': False}, indent=2) + '\n')

    def run(arguments, label, **kwargs):
        return command(arguments, output / (label + '.log'), **kwargs).stdout

    def session(script, label, namespace='SILENTSHIFT', marker=None):
        text = run([*docker, 'exec', '-i', container, 'iris', 'session', 'IRIS', '-U', namespace],
            label, data=script + '\nhalt\n')
        if marker and marker not in text.splitlines():
            raise RuntimeError(f'Expected status marker missing; inspect private {label}.log')
        return text

    try:
        repository = output / 'repository/package'
        if hashlib.sha256(args.archive.read_bytes()).hexdigest() != plan['archive']['artifact_sha256']:
            raise ValueError('Archive changed after preflight')
        unpack(args.archive, repository)
        if hashlib.sha256(args.archive.read_bytes()).hexdigest() != plan['archive']['artifact_sha256']:
            raise ValueError('Archive changed during preparation')
        private_write(output / 'namespace.cpf',
            '[Actions]\nCreateResource:Name=%DB_SILENTSHIFT,Description="SilentShift isolated IPM test"\n'
            'CreateDatabase:Name=SILENTSHIFT,Directory=/usr/irissys/mgr/SILENTSHIFT,Resource=%DB_SILENTSHIFT\n'
            'CreateNamespace:Name=SILENTSHIFT,Globals=SILENTSHIFT,Routines=SILENTSHIFT,Interop=1\n')
        runtime = runtime_environment(args) if args.activate_runtime else {}
        if runtime:
            private_write(output / 'runtime.env', ''.join(key + '=' + value + '\n' for key, value in runtime.items()))
        # Recheck immediately before the first daemon mutation; never free space
        # by deleting someone else's resources or pulling an alternative image.
        space(args)
        phase = 'creating a fresh isolated container'
        arguments = [*docker, 'run', '-d', '--pull', 'never', '--init', '--name', container,
            '--hostname', container, '--label', 'silentshift.scope=clean-ipm-verification',
            '--network', 'none', '--memory', '3g', '--cpus', '2', '--shm-size', '256m',
            '--tmpfs', '/tmp:rw,size=192m,mode=1777', '--log-opt', 'max-size=10m', '--log-opt', 'max-file=2']
        if runtime:
            arguments += ['--env-file', str(output / 'runtime.env')]
        arguments.append(plan['image_id'])
        if not args.resume_pristine:
            run(arguments, '01-create')
        else:
            run([*docker, 'inspect', '--format', '{{.Id}}', container], '01-resumed-container')
        for attempt in range(60):
            ready = command([*docker, 'exec', '-i', container, 'iris', 'session', 'IRIS', '-U', '%SYS'],
                data='write "SS_READY",!\nhalt\n', timeout=20, check=False)
            private_write(output / f'02-ready-{attempt:02}.log', ready.stdout + ready.stderr)
            if ready.returncode == 0 and 'SS_READY' in ready.stdout.splitlines():
                break
            time.sleep(1)
        else:
            raise RuntimeError('Fresh IRIS did not become ready within the bounded startup window')
        mounts = json.loads(run([*docker, 'inspect', '--format', '{{json .Mounts}}', container], '03-mounts'))
        if any(mount.get('Type') != 'tmpfs' for mount in mounts):
            raise RuntimeError('Fresh IRIS unexpectedly has a persistent volume or source mount')
        run([*docker, 'exec', container, 'test', '!', '-e', '/opt/silentshift'], '04-no-source-tree')
        before = session('write "SS_RUNTIME=",$zversion,!\n'
            'if ##class(Config.Namespaces).Exists("SILENTSHIFT") halt\n'
            'if ##class(%Dictionary.CompiledClass).%ExistsId("SilentShift.Setup") halt\n'
            'write "SS_PRISTINE_OK",!', '05-pristine', '%SYS', 'SS_PRISTINE_OK')
        run([*docker, 'exec', container, 'mkdir', '-p', RELEASE + '/repository'], '06-release-directory')
        run([*docker, 'cp', str(output / 'namespace.cpf'), container + ':' + RELEASE + '/namespace.cpf'], '06-copy-namespace')
        run([*docker, 'exec', '--user', '0', container, 'chown', '51773:51773',
            RELEASE + '/namespace.cpf'], '06-namespace-permissions')
        run([*docker, 'exec', container, 'iris', 'merge', 'IRIS', RELEASE + '/namespace.cpf'], '07-namespace')
        # Explicit administrator prerequisite on the new instance only. This is
        # distinct from module activation and preserves service authentication.
        session('set properties("Enabled")=1\n'
            'set sc=##class(Security.Services).Modify("%Service_CallIn",.properties)\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'write "SS_PYTHON_PREREQUISITE_OK",!', '08-python-prerequisite', '%SYS', 'SS_PYTHON_PREREQUISITE_OK')
        run([*docker, 'cp', str(args.vendor), container + ':' + RELEASE + '/zpm.xml'], '10-copy-client')
        run([*docker, 'cp', str(repository), container + ':' + RELEASE + '/repository/package'], '11-copy-repository')
        phase = 'installing the pinned client and local filesystem package'
        session('set sc=$system.OBJ.Load(' + literal(RELEASE + '/zpm.xml') + ',"ck")\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'set module=##class(%IPM.Storage.Module).NameOpen("zpm")\n'
            'if \'$isobject(module) halt\n'
            'if module.VersionString\'="' + VERSION + '" halt\n'
            'write "SS_CLIENT_OK",!', '12-client', marker='SS_CLIENT_OK')
        for label, cli in (('13-disable-analytics', 'config set analytics 0'),
                ('14-filesystem-repo', 'repo -name LocalArchive -fs -depth 2 -path ' + RELEASE + '/repository/'),
                ('15-install', plan['install_command'])):
            session('set sc=##class(%IPM.Main).Shell(' + literal(cli) + ')\n'
                'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
                'write "SS_COMMAND_OK",!', label, marker='SS_COMMAND_OK')
        phase = 'verifying installed assets and an empty stopped application'
        run([*docker, 'cp', str(ROOT / 'tests/iris/IPMChecks.cls'), container + ':' + RELEASE + '/IPMChecks.cls'], '16-copy-checks')
        script = ('set sc=##class(SilentShift.IPM).RequireStopped()\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'set sc=$system.OBJ.Load(' + literal(RELEASE + '/IPMChecks.cls') + ',"ck")\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'set sc=##class(SilentShift.Test.IPMChecks).Run()\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n')
        for table in TABLES:
            script += ('set query=##class(%SQL.Statement).%New()\n'
                'set sc=query.%Prepare(' + literal('SELECT COUNT(*) AS N FROM ' + table) + ')\n'
                'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
                'set rows=query.%Execute()\n'
                'if rows.%SQLCODE<0 halt\n'
                'if \'rows.%Next() halt\n'
                'if rows.%Get("N")\'=0 halt\n'
                'write "SS_EMPTY=' + table + '",!\n')
        script += 'write "SS_CLEAN_INSTALL_OK",!'
        checked = session(script, '17-installed-checks', marker='SS_CLEAN_INSTALL_OK')
        if ('SILENTSHIFT_IPM_CHECKS_OK path_rejections=10 deterministic_cases=5 module_origins=4 ai_runs=0'
                not in checked.splitlines() or checked.count('SS_EMPTY=') != len(TABLES)):
            raise RuntimeError('Installed checks or empty-state evidence was incomplete')
        root_match = re.search(r'^SILENTSHIFT_IPM_ASSET_ROOT=(.+)$', checked, re.MULTILINE)
        if root_match is None:
            raise RuntimeError('Installed asset-root evidence was missing')
        asset_root = root_match.group(1).strip()
        receipt = {**plan, 'kind': 'clean-local-filesystem-ipm-install', 'executed': True,
            'runtime': re.search(r'^SS_RUNTIME=(.+)$', before, re.MULTILINE).group(1).strip(),
            'ipm_client': {'version': VERSION, 'installer_sha256': SHA256},
            'pristine_namespace_verified': True, 'python_callin_prerequisite_enabled_by_driver': True,
            'clean_install_verified': True, 'install_source': 'local-filesystem-repository-derived-from-archive',
            'public_registry_install_verified': False, 'installed_asset_root': asset_root,
            'installed_deterministic_cases': 5, 'invalid_path_rejections': 10,
            'installed_python_module_origins': 4, 'application_tables_empty_after_install': len(TABLES),
            'package_activation_left_production_stopped': True, 'runtime_setup_executed': False,
            'clean_api_native_verified': False, 'model_investigations_requested': 0,
            'sdk_diagnostic_count': 0, 'sdk_diagnostic_scope': 'separate from native-five evaluation',
            'retained_resources': {'container': container}, 'automatic_cleanup': False}
        private_write(output / 'install-receipt.json', json.dumps(receipt, indent=2) + '\n')
        if args.activate_runtime:
            phase = 'explicit isolated runtime setup'
            activate(args, output, runtime, docker, session, run)
            receipt['runtime_setup_executed'] = True
            receipt['retained_resources'].update({'gateway': container + '-gateway', 'network': container})
            if args.allow_model_calls:
                phase = 'explicit local amendment embedding and SDK warmup'
                receipt.update(prepare_native(output, container, docker, session, run))
                phase = 'five explicitly authorized local model investigations'
                child_env = {**os.environ, **runtime}
                run([sys.executable, str(ROOT / 'scripts/verify_native.py'), '--api',
                    f'http://127.0.0.1:{args.api_port}/silentshift/api', '--allow-model-calls',
                    '--output', str(output / 'native-five.json')], '26-native-five', env=child_env, timeout=1500)
                native = json.loads((output / 'native-five.json').read_text())
                (output / 'native-five.json').chmod(0o600)
                if (native.get('passed') is not True or native.get('native_verified') is not True
                        or len(native.get('checks', [])) != 5):
                    raise RuntimeError('Native verifier did not record a passing result')
                receipt['clean_api_native_verified'] = True
                receipt['model_investigations_requested'] = 5
        receipt['space_after'] = space(args, enforce=False)
        private_write(output / 'receipt.json', json.dumps(receipt, indent=2) + '\n')
        return {'receipt': str(output / 'receipt.json'), 'clean_install_verified': True,
            'clean_api_native_verified': receipt['clean_api_native_verified'],
            'registry_published': False, 'retained_resources': receipt['retained_resources']}
    except BaseException:
        if (output / 'native-five.json').exists():
            (output / 'native-five.json').chmod(0o600)
        private_write(output / 'failure.json', json.dumps({'phase': phase,
            'existing_runtime_modified': False, 'resources_retained': True,
            'container': container, 'automatic_cleanup': False}, indent=2) + '\n')
        raise


def activate(args, output, runtime, docker, session, run, *, network_id=None):
    """Explicit setup; this starts only the new instance's production."""
    container = args.container
    if network_id is None:
        run([*docker, 'network', 'create', '--label',
            'silentshift.scope=clean-ipm-verification', container], '18-network')
    else:
        actual = run([*docker, 'network', 'inspect', '--format', '{{.Id}}', container], '18-existing-network').strip()
        if actual != network_id:
            raise RuntimeError('The retained network does not match its original creation receipt')
    networks = json.loads(run([*docker, 'inspect', '--format',
        '{{json .NetworkSettings.Networks}}', container], '19-network-state'))
    if 'none' in networks:
        run([*docker, 'network', 'disconnect', 'none', container], '19-disconnect-none')
    run([*docker, 'network', 'connect', '--alias', 'iris', container, container], '19-connect')
    session('set sc=##class(SilentShift.Setup).Install()\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'write "SS_RUNTIME_SETUP_OK",!', '20-setup', marker='SS_RUNTIME_SETUP_OK')
    conf = output / 'CSP.conf'
    # Copy only reviewed gateway config, never the source tree or current ini.
    private_write(conf, (ROOT / 'docker/CSP.conf').read_text())
    ini = output / 'CSP.ini'
    private_write(ini, '[SYSTEM]\nSystem_Manager=127.0.0.1\nDefault_Server=IRIS\n'
        'Server_Response_Timeout=180\nQueued_Request_Timeout=180\n[SYSTEM_INDEX]\nIRIS=Enabled\n'
        '[IRIS]\nIp_Address=iris\nTCP_Port=1972\nMinimum_Server_Connections=2\nMaximum_Session_Connections=8\n'
        'Username=CSPSystem\nPassword=' + runtime['SILENTSHIFT_GATEWAY_PASSWORD'] + '\n'
        'Connection_Security_Level=0\n[APP_PATH_INDEX]\n/silentshift=Enabled\n/silentshift-provider=Enabled\n/csp=Enabled\n'
        '[APP_PATH:/silentshift]\nDefault_Server=IRIS\n[APP_PATH:/silentshift-provider]\nDefault_Server=IRIS\n'
        '[APP_PATH:/csp]\nDefault_Server=IRIS\n')
    space(args)
    run([*docker, 'run', '-d', '--pull', 'never', '--init', '--name', container + '-gateway',
        '--network', container, '--network-alias', 'gateway', '--publish', f'127.0.0.1:{args.api_port}:80',
        '--env', 'ISC_CSP_CONF_FILE=/silentshift-gateway/CSP.conf',
        '--env', 'ISC_CSP_INI_FILE=/silentshift-gateway/CSP.ini',
        '--mount', f'type=bind,src={conf},dst=/silentshift-gateway/CSP.conf,readonly',
        '--mount', f'type=bind,src={ini},dst=/silentshift-gateway/CSP.ini',
        '--log-opt', 'max-size=10m', '--log-opt', 'max-file=2', args.gateway_image], '21-gateway')
    # Read-only health/auth check, with bounded retries, before optional models.
    from verify_native import Client
    client = Client(f'http://127.0.0.1:{args.api_port}/silentshift/api',
        runtime['SILENTSHIFT_IRIS_USERNAME'], runtime['SILENTSHIFT_IRIS_PASSWORD'])
    for _ in range(30):
        try:
            status, health = client.call('/health')
            if status == 200 and isinstance(health, dict) and health.get('production', {}).get('running') is True:
                private_write(output / '22-runtime-health.json', json.dumps({
                    'http_status': status, 'production_running': True, 'build': health.get('build')}, indent=2) + '\n')
                return
        except OSError:
            pass
        time.sleep(1)
    raise RuntimeError('Isolated authenticated API did not become healthy')


def prepare_native(output, container, docker, session, run) -> dict:
    """Real local inference prerequisites, separate from the five-case score."""
    indexed = session('set sc=##class(SilentShift.Precedents).IndexAmendments(.report)\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'write "SS_AMENDMENT_REPORT=",report,!\n'
        'set rows=##class(%SQL.Statement).%ExecDirect(,"SELECT COUNT(*) AS N FROM SilentShift_Data.Precedent")\n'
        'if rows.%SQLCODE<0 halt\n'
        'if \'rows.%Next() halt\n'
        'write "SS_AMENDMENT_ROWS=",rows.%Get("N"),!\n'
        'write "SS_AMENDMENT_INDEX_OK",!', '23-amendment-index', marker='SS_AMENDMENT_INDEX_OK')
    report_match = re.search(r'^SS_AMENDMENT_REPORT=(.+)$', indexed, re.MULTILINE)
    rows_match = re.search(r'^SS_AMENDMENT_ROWS=(\d+)$', indexed, re.MULTILINE)
    if report_match is None or rows_match is None:
        raise RuntimeError('Amendment embedding/index evidence was missing')
    report = json.loads(report_match.group(1))
    row_count = int(rows_match.group(1))
    if (report.get('status') != 'indexed' or report.get('model') != 'all-minilm:22m'
            or report.get('dimensions') != 384 or report.get('eligible_sources') != 1
            or report.get('written') != 1 or report.get('unchanged') != 0
            or report.get('local_embedding_requests') != 1 or row_count != 1):
        raise RuntimeError('Fresh approved-amendment corpus did not match its expected real index result')
    private_write(output / 'amendment-index.json', json.dumps({
        'report': report, 'persisted_precedent_rows': row_count,
        'synthetic_fixture': True, 'resolved_case_sources_created': 0}, indent=2) + '\n')
    run([*docker, 'cp', str(ROOT / 'tests/iris/ProviderProbe.cls'),
        container + ':' + RELEASE + '/ProviderProbe.cls'], '24-copy-sdk-probe')
    text = session('set sc=$system.OBJ.Load(' + literal(RELEASE + '/ProviderProbe.cls') + ',"ck")\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'set sc=##class(SilentShift.Test.ProviderProbe).Run("basic",.id,.summary)\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'set detail=##class(%DynamicObject).%FromJSON(summary)\n'
        'if detail.%Get("failure_caught")\'=0 halt\n'
        'if detail.%Get("provider_requests")\'=1 halt\n'
        'if detail.%Get("route")\'="QUARANTINED" halt\n'
        'if detail.%Get("delivery_count")\'=0 halt\n'
        'if detail.%Get("kind")\'="basic" halt\n'
        'if detail.%Get("case_id")\'=id halt\n'
        'if detail.%Get("trace_id")="" halt\n'
        'write "SS_SDK_WARMUP_SUMMARY=",summary,!\n'
        'write "SS_SDK_WARMUP_OK",!', '25-sdk-warmup', marker='SS_SDK_WARMUP_OK')
    summary_match = re.search(r'^SS_SDK_WARMUP_SUMMARY=(.+)$', text, re.MULTILINE)
    if summary_match is None:
        raise RuntimeError('SDK warmup evidence was missing')
    summary = json.loads(summary_match.group(1))
    if (summary.get('kind') != 'basic' or summary.get('failure_caught') != 0
            or summary.get('provider_requests') != 1 or summary.get('route') != 'QUARANTINED'
            or summary.get('delivery_count') != 0 or not summary.get('case_id')
            or not str(summary.get('trace_id') or '').strip()):
        raise RuntimeError('SDK warmup failed its caught/requests/Q0 proof')
    private_write(output / 'sdk-warmup.json', json.dumps({
        'scope': 'synthetic SDK diagnostic, excluded from native-five evaluation',
        'diagnostic_count': 1, 'summary': summary}, indent=2) + '\n')
    return {'approved_amendment_index': {'report': report, 'persisted_rows': row_count},
        'sdk_diagnostic_count': 1, 'sdk_diagnostic': summary}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True, help='Fresh real IPM archive matching the current source')
    parser.add_argument('--source', type=Path, default=ROOT, help='Source used to inspect archive resources/assets')
    parser.add_argument('--vendor', type=Path, default=ROOT / '.local/ipm/vendor/zpm-0.10.10.xml')
    parser.add_argument('--context', default='colima-silentshift')
    parser.add_argument('--vm-profile', default='silentshift')
    parser.add_argument('--image', default='silentshift-iris:2026.3.0AI.154.0')
    parser.add_argument('--gateway-image', default='containers.intersystems.com/intersystems/webgateway:2026.1')
    parser.add_argument('--container', default='silentshift-ipm-clean-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S'))
    parser.add_argument('--min-host-free-gib', type=float, default=1.8)
    parser.add_argument('--min-vm-free-gib', type=float, default=3)
    parser.add_argument('--execute', action='store_true', help='Create a NEW isolated runtime and perform actual IPM install')
    parser.add_argument('--resume-pristine', action='store_true',
        help='Resume only the exact owned container from its recorded pristine pre-namespace state')
    parser.add_argument('--activate-runtime', action='store_true', help='Explicitly configure security, seed references and start the NEW production/gateway')
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env', help='Private runtime environment; used only with --activate-runtime')
    parser.add_argument('--api-port', type=int, default=52783)
    parser.add_argument('--allow-model-calls', action='store_true',
        help='After setup: one local amendment embedding, one separate SDK warmup, then five native API investigations')
    args = parser.parse_args()
    try:
        plan = preflight(args)
        print(json.dumps(execute(args, plan) if args.execute else plan))
    except (OSError, ValueError, RuntimeError, tarfile.TarError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f'Clean IPM verification stopped: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
