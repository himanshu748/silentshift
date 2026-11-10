"""No Docker or provider access is needed to reject unsafe verifier options."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_bonus_release as bonus
import verify_ipm_clean as clean


@pytest.mark.parametrize(
    "options,reason",
    [
        (["--execution-mode", "live"], "requires --allow-model-calls"),
        (["--install-latest"], "requires --source public-registry"),
        (["--network-subnet", "8.8.8.0/24"], "RFC1918"),
        (["--verification-source", "/synthetic/other-source"], "source-load verification must"),
    ],
)
def test_invalid_verification_options_stop_before_external_commands(options, reason):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/verify_bonus_release.py"),
         "--source", "load", "--container", "silentshift-bonus-load-unused", *options],
        cwd=ROOT, env={**os.environ, "PATH": ""}, text=True,
        capture_output=True, timeout=10, check=False,
    )
    assert result.returncode == 1
    assert reason in result.stderr
    assert "Creating fresh" not in result.stdout


@pytest.mark.parametrize('value', [
    '8.8.8.0/24', '127.0.0.0/24', '169.254.0.0/24', '100.64.0.0/24',
    '198.51.100.0/24', '10.0.0.0/23', '10.0.0.0/29', '10.0.0.1/24',
    'fd00::/24', '172.32.0.0/24', '192.169.0.0/24', 'not-a-network',
])
def test_network_subnet_rejects_noncanonical_nonprivate_or_unbounded_values(value):
    with pytest.raises(ValueError, match='RFC1918'):
        clean.validate_network_subnet(value)


@pytest.mark.parametrize('value', ['10.243.8.0/24', '172.31.4.0/28', '192.168.10.0/25'])
def test_network_subnet_accepts_only_bounded_private_networks(value):
    assert clean.validate_network_subnet(value) == value


def test_network_overlap_uses_only_read_only_inspection(monkeypatch):
    calls = []
    def command(argv, **kwargs):
        calls.append(argv)
        data = 'network-id\n' if argv[-2:] == ['ls', '--quiet'] else json.dumps([
            {'Name': 'existing-test', 'IPAM': {'Config': [{'Subnet': '10.12.0.0/16'}]}}
        ])
        return subprocess.CompletedProcess(argv, 0, data, '')
    monkeypatch.setattr(clean, 'command', command)
    with pytest.raises(ValueError, match='overlaps existing Docker network existing-test'):
        clean.available_network_subnet('10.12.5.0/24', ['docker', '--context', 'synthetic'])
    assert [argv[3:5] for argv in calls] == [['network', 'ls'], ['network', 'inspect']]
    assert all(not any(word in argv for word in ('create', 'rm', 'prune')) for argv in calls)


def test_disjoint_subnet_accepts_ipv4_and_ignores_existing_ipv6(monkeypatch):
    def command(argv, **kwargs):
        data = 'network-id' if argv[-2:] == ['ls', '--quiet'] else json.dumps([
            {'Name': 'existing', 'IPAM': {'Config': [{'Subnet': '172.18.0.0/16'},
                                                   {'Subnet': 'fd00::/64'}]}}
        ])
        return subprocess.CompletedProcess(argv, 0, data, '')
    monkeypatch.setattr(clean, 'command', command)
    assert clean.available_network_subnet('10.243.8.0/24', ['docker']) == '10.243.8.0/24'


@pytest.mark.parametrize('subnet', [None, '10.243.8.0/24'])
def test_activate_forwards_only_explicit_subnet_on_new_network(monkeypatch, tmp_path, subnet):
    class StoppedAfterCreate(Exception): pass
    read_calls, create_calls = [], []
    def command(argv, **kwargs):
        read_calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, '', '')
    def run(argv, label, **kwargs):
        create_calls.append(argv)
        raise StoppedAfterCreate()
    monkeypatch.setattr(clean, 'command', command)
    args = argparse.Namespace(container='synthetic-container', network_subnet=subnet)
    with pytest.raises(StoppedAfterCreate):
        clean.activate(args, tmp_path, {}, ['docker'], None, run)
    if subnet is None:
        assert read_calls == [] and '--subnet' not in create_calls[0]
    else:
        assert create_calls[0][create_calls[0].index('--subnet') + 1] == subnet
        assert read_calls == [['docker', 'network', 'ls', '--quiet']]


def test_registry_verification_selects_frozen_tests_and_trace_only(tmp_path):
    (tmp_path / 'tests/iris').mkdir(parents=True)
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts/trace_example.py').write_text('# synthetic pinned script\n')
    args = argparse.Namespace(source='public-registry', execution_mode='recorded-replay',
                              verification_source=tmp_path)
    selected = bonus.verification_inputs(args)
    assert selected == {'source': tmp_path.resolve(), 'tests': tmp_path / 'tests/iris',
                        'trace': tmp_path / 'scripts/trace_example.py'}
    assert bonus.ROOT == ROOT
    args.source = 'load'
    with pytest.raises(ValueError, match='source-load verification must'):
        bonus.verification_inputs(args)


def test_default_source_gate_keeps_current_source_tests():
    selected = bonus.verification_inputs(argparse.Namespace(source='load', execution_mode='recorded-replay'))
    assert selected['source'] == ROOT
    assert selected['tests'] == ROOT / 'tests/iris'
    assert selected['trace'] == ROOT / 'scripts/trace_example.py'
