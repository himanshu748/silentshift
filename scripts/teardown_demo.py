#!/usr/bin/env python3
"""Plan, or explicitly tear down, one tagged SilentShift demo deployment.

The private deployment receipt is produced by the operator. No broad tag-based
deletion, account-wide cleanup, image upload or billing-setting change occurs.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path


def tags_match(tags, deployment):
    values = {t['Key']: t['Value'] for t in tags}
    return values.get('project') == 'silentshift' and values.get('deployment') == deployment


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--profile', default='default')
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    receipt = json.loads(a.receipt.read_text())
    instance = receipt['instance_id']
    deployment = receipt['deployment']
    group = receipt['security_group_id']
    key = receipt['key_name']
    if not (re.fullmatch(r'i-[a-f0-9]+', instance) and re.fullmatch(r'sg-[a-f0-9]+', group)
            and re.fullmatch(r'silentshift-[a-z0-9-]+', deployment)
            and key == deployment):
        raise ValueError('Receipt does not identify a single bounded demo deployment')
    base = ['aws', '--profile', a.profile, '--region', receipt['region']]

    def aws(*args):
        data = subprocess.check_output(base + list(args), text=True)
        return json.loads(data) if data.strip() else {}

    if aws('sts', 'get-caller-identity')['Account'] != receipt['account_id']:
        raise ValueError('AWS account differs from deployment receipt')
    rows = aws('ec2', 'describe-instances', '--instance-ids', instance)['Reservations']
    item = rows[0]['Instances'][0]
    if not tags_match(item.get('Tags', []), deployment):
        raise ValueError('Instance project/deployment tags do not match; nothing deleted')
    security = aws('ec2', 'describe-security-groups', '--group-ids', group)['SecurityGroups'][0]
    if not tags_match(security.get('Tags', []), deployment):
        raise ValueError('Security group tags do not match; nothing deleted')
    keys = aws('ec2', 'describe-key-pairs', '--key-names', key)['KeyPairs']
    if not keys or not tags_match(keys[0].get('Tags', []), deployment):
        raise ValueError('Key pair tags do not match; nothing deleted')
    if any(not b.get('Ebs', {}).get('DeleteOnTermination') for b in item.get('BlockDeviceMappings', [])):
        raise ValueError('A volume would survive termination; inspect it before proceeding')
    print(json.dumps({'instance_id': instance, 'security_group_id': group,
        'key_name': key, 'execute': a.execute, 'volumes': 'delete with instance',
        'budget': 'retained monitoring-only'}, indent=2))
    if not a.execute:
        return
    aws('ec2', 'terminate-instances', '--instance-ids', instance)
    subprocess.run(base + ['ec2', 'wait', 'instance-terminated', '--instance-ids', instance], check=True)
    aws('ec2', 'delete-security-group', '--group-id', group)
    aws('ec2', 'delete-key-pair', '--key-name', key)
    print('Tagged instance terminated; its security group and key pair removed. No other project changed.')


if __name__ == '__main__':
    main()
