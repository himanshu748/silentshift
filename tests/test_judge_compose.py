"""Test new-project setup boundaries without a daemon, credentials or model."""
from __future__ import annotations

import importlib.util
import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / 'scripts'))
    try:
        spec.loader.exec_module(loaded)
    finally:
        sys.path.pop(0)
    return loaded


judge = module('judge_compose_test', 'scripts/judge_compose.py')
prepare = module('judge_prepare_test', 'docker/judge-prepare.py')
start = module('judge_start_test', 'docker/judge-start.py')


def environment():
    return {'SILENTSHIFT_IRIS_USERNAME': 'reviewer', 'SILENTSHIFT_VIEWER_USERNAME': 'viewer',
            'SILENTSHIFT_IRIS_PASSWORD': 'synthetic-reviewer-password',
            'SILENTSHIFT_VIEWER_PASSWORD': 'synthetic-viewer-password',
            'SILENTSHIFT_GATEWAY_PASSWORD': 'synthetic-gateway-password',
            'SILENTSHIFT_PROVIDER_MODE': 'recorded-replay', 'SILENTSHIFT_API_KEY': '',
            'SILENTSHIFT_EMBED_BASE_URL': '', 'SILENTSHIFT_JUDGE_PROJECT': 'silentshift-judge-test'}


@pytest.fixture
def preflight(monkeypatch, tmp_path):
    monkeypatch.setattr(judge, 'ROOT', tmp_path)
    monkeypatch.setattr(judge.shutil, 'which', lambda _: '/synthetic/docker')
    monkeypatch.setattr(judge, 'compose_command', lambda _: ['docker', 'compose'])
    monkeypatch.setattr(judge, 'space', lambda _: {})
    monkeypatch.setattr(judge, 'unused_network_subnet', lambda _: '10.253.123.0/28')
    monkeypatch.setattr(judge, 'available_network_subnet', lambda value, _: value)
    calls = []
    image = {'Architecture': 'arm64', 'Config': {'Labels': {
        'com.intersystems.platform-version': '2026.3.0AI.154.0com'}}}

    def command(argv, **kwargs):
        calls.append(argv)
        result = '2.24.0' if argv[-2:] == ['version', '--short'] else ''
        if 'image' in argv:
            result = json.dumps([image])
        return subprocess.CompletedProcess(argv, 0, result, '')

    monkeypatch.setattr(judge, 'command', command)
    args = judge.parser().parse_args(['--project', 'silentshift-judge-test'])
    return args, calls, image


def test_missing_docker_stops_before_private_files(preflight, monkeypatch, tmp_path):
    args, calls, _ = preflight
    monkeypatch.setattr(judge.shutil, 'which', lambda _: None)
    with pytest.raises(ValueError, match='Docker CLI is missing'):
        judge.preflight(args, {})
    assert not calls and not list(tmp_path.iterdir())


def test_existing_compose_project_is_never_replaced(preflight, monkeypatch):
    args, calls, _ = preflight
    original = judge.command

    def existing(argv, **kwargs):
        if 'ps' in argv:
            return subprocess.CompletedProcess(argv, 0, 'existing-container-id', '')
        return original(argv, **kwargs)

    monkeypatch.setattr(judge, 'command', existing)
    with pytest.raises(ValueError, match='already exists'):
        judge.preflight(args, {})
    assert all('image' not in call for call in calls)


@pytest.mark.parametrize('floor', [float('nan'), float('inf'), -1, 0])
def test_invalid_disk_floor_cannot_bypass_guard(preflight, floor):
    args, _, _ = preflight
    args.min_host_free_gib = floor
    with pytest.raises(ValueError, match='safety floors'):
        judge.preflight(args, {})


def test_missing_official_image_never_downloads_it(preflight, monkeypatch):
    args, calls, _ = preflight
    original = judge.command

    def missing(argv, **kwargs):
        if 'image' in argv and args.image in argv:
            return subprocess.CompletedProcess(argv, 1, '', '')
        return original(argv, **kwargs)

    monkeypatch.setattr(judge, 'command', missing)
    with pytest.raises(ValueError, match='no image is downloaded'):
        judge.preflight(args, {})
    assert all('pull' not in call and 'run' not in call and 'up' not in call for call in calls)


def test_wrong_iris_architecture_is_rejected(preflight):
    args, _, image = preflight
    image['Architecture'] = 'amd64'
    with pytest.raises(ValueError, match='other builds/platforms are unverified'):
        judge.preflight(args, {})


def test_another_native_instance_is_not_stopped(preflight, monkeypatch):
    args, calls, _ = preflight
    original = judge.command

    def running(argv, **kwargs):
        if 'ps' in argv and '--quiet' in argv:
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, 'another-native-instance', '')
        return original(argv, **kwargs)

    monkeypatch.setattr(judge, 'command', running)
    with pytest.raises(ValueError, match='no instance was stopped'):
        judge.preflight(args, {})
    assert all('stop' not in call and 'up' not in call for call in calls)


def test_private_environment_cannot_inherit_a_paid_provider(preflight, monkeypatch):
    args, _, _ = preflight
    args.network_subnet = '10.253.123.0/28'
    monkeypatch.setenv('SILENTSHIFT_PROVIDER', 'openai')
    monkeypatch.setenv('SILENTSHIFT_API_KEY', 'synthetic-key-never-used')
    path, values = judge.private_environment(args)
    assert values['SILENTSHIFT_PROVIDER_MODE'] == 'recorded-replay'
    assert values['SILENTSHIFT_PROVIDER'] == 'ollama'
    assert values['SILENTSHIFT_API_KEY'] == values['SILENTSHIFT_EMBED_BASE_URL'] == ''
    assert len({values[key] for key in prepare.PASSWORD_KEYS}) == 3
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert 'synthetic-key-never-used' not in path.read_text()
    with pytest.raises(FileExistsError):
        judge.private_environment(args)


@pytest.fixture
def state(monkeypatch, tmp_path):
    root, state = tmp_path / 'source', tmp_path / 'state'
    (root / 'docker').mkdir(parents=True)
    (root / 'docker/CSP.conf').write_text('synthetic gateway config\n')
    monkeypatch.setattr(prepare, 'ROOT', root)
    monkeypatch.setattr(prepare, 'STATE', state)
    monkeypatch.setattr(prepare.os, 'chown', lambda *_: None)
    return state


def test_prepare_refuses_changed_password_without_overwriting_state(state):
    values = environment()
    prepare.prepare(values)
    before = (state / 'CSP.ini').read_bytes()
    values['SILENTSHIFT_GATEWAY_PASSWORD'] = 'different-synthetic-gateway-password'
    with pytest.raises(ValueError, match='different configuration'):
        prepare.prepare(values)
    assert (state / 'CSP.ini').read_bytes() == before


def test_prepare_rejects_an_unowned_nonempty_volume(state):
    state.mkdir()
    (state / 'unrelated-data').write_text('retain')
    with pytest.raises(ValueError, match='unrecognized nonempty'):
        prepare.prepare(environment())
    assert (state / 'unrelated-data').read_text() == 'retain'


@pytest.mark.parametrize('changed', [
    {'SILENTSHIFT_PROVIDER_MODE': 'live'},
    {'SILENTSHIFT_API_KEY': 'synthetic-key'},
    {'SILENTSHIFT_EMBED_BASE_URL': 'http://localhost:11434/v1/'},
    {'SILENTSHIFT_IRIS_PASSWORD': 'short'},
    {'SILENTSHIFT_IRIS_PASSWORD': 'synthetic\nmultiline-password'},
    {'SILENTSHIFT_IRIS_USERNAME': 'viewer'},
])
def test_prepare_rejects_unsafe_or_incomplete_configuration_before_writes(state, changed):
    values = {**environment(), **changed}
    with pytest.raises(ValueError):
        prepare.prepare(values)
    assert not state.exists()


def test_prepare_is_idempotent_and_never_prints_passwords(state, capsys):
    values = environment()
    prepare.prepare(values)
    first = (state / 'CSP.ini').read_bytes()
    prepare.prepare(values)
    assert (state / 'CSP.ini').read_bytes() == first
    output = capsys.readouterr().out
    assert all(values[key] not in output for key in prepare.PASSWORD_KEYS)
    assert stat.S_IMODE((state / 'CSP.ini').stat().st_mode) == 0o600


def test_source_bootstrap_refuses_namespace_owned_by_another_install(monkeypatch, tmp_path):
    monkeypatch.setattr(start, 'STATE', tmp_path)
    monkeypatch.setattr(start.platform, 'machine', lambda: 'aarch64')
    calls = []

    def command(argv, label, data=None):
        calls.append((argv, label))
        if label == '01-probe':
            return ('JUDGE_VERSION=IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) '
                    '2026.3.0AI (Build 154U)\nJUDGE_NAMESPACE=1\nJUDGE_PROBE_OK\n')
        return 'not owned by this project\n'

    monkeypatch.setattr(start, 'command', command)
    with pytest.raises(ValueError, match='02-owner'):
        start.bootstrap(environment())
    assert [label for _, label in calls] == ['01-probe', '02-owner']
    assert not (tmp_path / 'bootstrap.ok').exists()
