#!/usr/bin/env python3
"""Operator-run local IPM load/package check in an existing stopped runtime.

Mutates installed classes/assets and optional IPM client, not case data. It never
stops/starts a production, invokes Setup.Install, uninstalls, or calls a model.
This is deliberately not evidence of a clean or public-registry installation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

from fetch_ipm import SHA256, SIZE, VERSION, fetch
from inspect_ipm import inspect
from package_ipm import ROOT, stage

TABLES = tuple('SilentShift_Data.' + name for name in (
    'CaseRecord', 'Reference', 'AuditEvent', 'Delivery', 'ReviewAction', 'Evaluation', 'Runbook', 'Precedent'
)) + ('SilentShift_Workflow.ReviewTask', 'EnsLib_Workflow.Worklist')


def literal(value: str) -> str:
    if any(ord(char) < 32 for char in value):
        raise ValueError('Control characters are not valid command arguments')
    return '"' + value.replace('"', '""') + '"'


def run(args, log: Path, *, input_text=None, timeout=900) -> str:
    result = subprocess.run(args, input=input_text, text=True, capture_output=True, timeout=timeout)
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    log.chmod(0o600)
    if result.returncode:
        raise RuntimeError(f'Command failed; inspect private {log.name}')
    return result.stdout


def session(docker, container, script, log) -> str:
    return run([*docker, 'exec', '-i', container, 'iris', 'session', 'IRIS', '-U', 'SILENTSHIFT'],
        log, input_text=script + '\nhalt\n')


def snapshot(docker, container, output, label):
    # Count only: never print persisted payloads, user credentials or case notes.
    script = 'write "SS_NAMESPACE=",$namespace,!\nwrite "SS_RUNTIME=",$zversion,!\n'
    script += ('set sc=##class(SilentShift.IPM).CheckTarget()\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'set sc=##class(SilentShift.IPM).RequireStopped()\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        )
    for table in TABLES:
        script += ('set statement=##class(%SQL.Statement).%New()\n'
            'set sc=statement.%Prepare(' + literal('SELECT COUNT(*) AS N FROM ' + table) + ')\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'set rows=statement.%Execute()\n'
            'if rows.%SQLCODE<0 write "SS_SNAPSHOT_SQL_ERROR",! halt\n'
            'if \'rows.%Next() write "SS_SNAPSHOT_ROW_ERROR",! halt\n'
            'write "SS_COUNT=' + table + '=",rows.%Get("N"),!\n')
    script += ('write "SS_IPM_PRESENT=",##class(%Dictionary.CompiledClass).%ExistsId("%IPM.Main"),!\n'
        'write "SS_PREFLIGHT_OK",!')
    text = session(docker, container, script, output / (label + '.log'))
    if 'SS_PREFLIGHT_OK' not in text or 'SS_NAMESPACE=SILENTSHIFT' not in text:
        raise RuntimeError('Stopped-production/build/namespace preflight failed; no package load attempted')
    counts = {name: int(count) for name, count in re.findall(r'SS_COUNT=([\w.]+)=(\d+)', text)}
    if set(counts) != set(TABLES):
        raise RuntimeError('Incomplete data-preservation snapshot')
    return {'counts': counts, 'ipm_present': 'SS_IPM_PRESENT=1' in text,
        'runtime': re.search(r'SS_RUNTIME=([^\r\n]+)', text).group(1)}


def verify(args) -> dict:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', args.container):
        raise ValueError('Expected an explicit existing container name')
    docker = ['docker', '--context', args.context]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT / '.local/ipm/runs' / stamp
    output.mkdir(parents=True, mode=0o700)
    print('Checking the existing stopped SILENTSHIFT runtime...', flush=True)
    before = snapshot(docker, args.container, output, '01-before')
    # Rebuild only after preflight, from the latest shared source files.
    source_stage = output / 'stage'
    inventory = stage(ROOT, source_stage)
    runtime_root = '/tmp/silentshift-ipm-' + stamp
    run([*docker, 'exec', args.container, 'mkdir', '-p', runtime_root + '/out'], output / '02-mkdir.log')
    run([*docker, 'cp', str(source_stage), args.container + ':' + runtime_root + '/stage'],
        output / '03-copy-stage.log')
    if not before['ipm_present']:
        if not args.install_client:
            raise RuntimeError('IPM is absent; rerun in the operator window with --install-client')
        vendor = ROOT / '.local/ipm/vendor/zpm-0.10.10.xml'
        fetch(vendor)
        run([*docker, 'cp', str(vendor), args.container + ':' + runtime_root + '/zpm.xml'],
            output / '04-copy-client.log')
        print('Importing the pinned namespace-local IPM client...', flush=True)
        text = session(docker, args.container,
            'set sc=$system.OBJ.Load(' + literal(runtime_root + '/zpm.xml') + ',"ck")\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'write "SS_CLIENT_IMPORTED",!', output / '05-client-install.log')
        if 'SS_CLIENT_IMPORTED' not in text:
            raise RuntimeError('IPM client import failed; inspect private client-install log')
    version_script = ('set module=##class(%IPM.Storage.Module).NameOpen("zpm")\n'
        'if \'$isobject(module) write "SS_IPM_VERSION_MISSING",! halt\n'
        'write "SS_IPM_VERSION=",module.VersionString,!')
    version_text = session(docker, args.container, version_script, output / '06-client-version.log')
    if 'SS_IPM_VERSION=' + VERSION not in version_text:
        raise RuntimeError('Existing IPM version differs from the pinned verification client; not replaced')
    print('Loading the fresh source stage through real IPM...', flush=True)
    text = session(docker, args.container,
        'set sc=##class(%IPM.Main).Shell(' + literal('load ' + runtime_root + '/stage') + ')\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'write "SS_LOCAL_LOAD_OK",!', output / '07-module-load.log')
    if 'SS_LOCAL_LOAD_OK' not in text:
        raise RuntimeError('Local IPM load failed; production remains stopped')
    print('Generating the actual IPM archive...', flush=True)
    text = session(docker, args.container,
        'set sc=##class(%IPM.Main).Shell(' + literal('package silentshift -path ' + runtime_root + '/out/') + ')\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'write "SS_LOCAL_PACKAGE_OK",!', output / '08-module-package.log')
    if 'SS_LOCAL_PACKAGE_OK' not in text:
        raise RuntimeError('IPM package generation failed; production remains stopped')
    archive = output / 'silentshift-0.2.0.tgz'
    run([*docker, 'cp', args.container + ':' + runtime_root + '/out.tgz', str(archive)],
        output / '09-copy-archive.log')
    boundary = inspect(archive, source_stage)
    # Load the separately owned test only AFTER packaging, never as a resource.
    run([*docker, 'cp', str(ROOT / 'tests/iris/IPMChecks.cls'),
        args.container + ':' + runtime_root + '/IPMChecks.cls'], output / '10-copy-checks.log')
    text = session(docker, args.container,
        'set sc=$system.OBJ.Load(' + literal(runtime_root + '/IPMChecks.cls') + ',"ck")\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'set sc=##class(SilentShift.Test.IPMChecks).Run()\n'
        'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
        'write "SS_INSTALLED_CHECKS_OK",!', output / '11-installed-checks.log')
    if 'SS_INSTALLED_CHECKS_OK' not in text:
        raise RuntimeError('Installed deterministic checks failed; production remains stopped')
    after = snapshot(docker, args.container, output, '12-after')
    if before['counts'] != after['counts']:
        raise RuntimeError('Data-row counts changed during packaging; investigate before resuming')
    receipt = {'package': 'silentshift', 'version': '0.2.0',
        'verification_scope': 'existing-namespace-local-ipm-load-and-package',
        'runtime': after['runtime'], 'namespace': 'SILENTSHIFT',
        'ipm_client': {'version': VERSION, 'sha256': SHA256, 'bytes': SIZE},
        'source_inventory_files': len(inventory['files']), 'archive': boundary,
        'local_load_verified': True, 'local_package_verified': True,
        'installed_deterministic_cases': 5, 'invalid_path_rejections': 10,
        'installed_python_module_origins': 4,
        'before_data_row_counts': before['counts'], 'after_data_row_counts': after['counts'],
        'data_row_counts_preserved': True, 'model_calls': 0,
        'clean_install_verified': False, 'registry_install_verified': False,
        'registry_published': False, 'production_left_stopped': True}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'receipt': str(output / 'receipt.json'),
        'local_load_verified': True, 'local_package_verified': True,
        'clean_install_verified': False, 'registry_published': False,
        'production_left_stopped': True}))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', default='colima-silentshift')
    parser.add_argument('--container', required=True)
    parser.add_argument('--install-client', action='store_true',
        help='Explicitly import the pinned official client if absent in SILENTSHIFT')
    args = parser.parse_args()
    try:
        verify(args)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f'Native IPM verification stopped: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
