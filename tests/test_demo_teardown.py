import importlib.util
import json
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('demo_teardown', Path(__file__).resolve().parents[1] / 'scripts/teardown_demo.py')
teardown = importlib.util.module_from_spec(spec)
spec.loader.exec_module(teardown)


@pytest.mark.parametrize('invalid', ['account', 'instance_tags', 'group_tags', 'key_tags', 'volume', None])
def test_teardown_checks_all_ownership_before_any_mutation(tmp_path, monkeypatch, invalid):
    deployment = 'silentshift-synthetic-test'
    receipt = {'instance_id': 'i-123abc', 'security_group_id': 'sg-456def',
        'deployment': deployment, 'key_name': deployment, 'region': 'us-east-1',
        'account_id': '000000000000'}
    target = tmp_path / 'receipt.json'
    target.write_text(json.dumps(receipt))
    monkeypatch.setattr(sys, 'argv', ['teardown_demo.py', '--receipt', str(target), '--execute'])
    tags = [{'Key': 'project', 'Value': 'silentshift'}, {'Key': 'deployment', 'Value': deployment}]
    calls = []
    waits = []

    def aws(args, **kwargs):
        calls.append(args)
        operation = args[6]
        if operation == 'get-caller-identity':
            result = {'Account': '111111111111' if invalid == 'account' else receipt['account_id']}
        elif operation == 'describe-instances':
            result = {'Reservations': [{'Instances': [{'Tags': [] if invalid == 'instance_tags' else tags,
                'BlockDeviceMappings': [{'Ebs': {'DeleteOnTermination': invalid != 'volume'}}]}]}]}
        elif operation == 'describe-security-groups':
            result = {'SecurityGroups': [{'Tags': [] if invalid == 'group_tags' else tags}]}
        elif operation == 'describe-key-pairs':
            result = {'KeyPairs': [{'Tags': [] if invalid == 'key_tags' else tags}]}
        else:
            result = {}
        return json.dumps(result)

    monkeypatch.setattr(teardown.subprocess, 'check_output', aws)
    monkeypatch.setattr(teardown.subprocess, 'run', lambda args, **kw: waits.append(args))
    if invalid:
        with pytest.raises(ValueError):
            teardown.main()
        assert not any(args[6] in {'terminate-instances', 'delete-security-group', 'delete-key-pair'} for args in calls)
        assert waits == []
    else:
        teardown.main()
        mutations = [args[6:] for args in calls if args[6] in {'terminate-instances', 'delete-security-group', 'delete-key-pair'}]
        assert mutations == [
            ['terminate-instances', '--instance-ids', 'i-123abc'],
            ['delete-security-group', '--group-id', 'sg-456def'],
            ['delete-key-pair', '--key-name', deployment],
        ]
        assert waits[0][6:] == ['wait', 'instance-terminated', '--instance-ids', 'i-123abc']
