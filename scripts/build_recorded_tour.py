#!/usr/bin/env python3
"""Select two already-public native records; never creates or reruns a case."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/evidence/bonus-claims-nov11/java-pex-native-five.json'
RECEIPTS = ROOT / 'docs/evidence/bonus-claims-nov11/java-pex-frozen-cases.json'
FIELDS = ('id', 'scenario_id', 'received_at', 'clock', 'message', 'references',
          'assessment', 'recommendation', 'policy', 'routing', 'delivery_count', 'trace_id', 'synthetic')


def build():
    native = json.loads(SOURCE.read_text())
    receipts = {row['case_id']: row for row in json.loads(RECEIPTS.read_text())['cases']}
    selected = []
    for scenario in ('quantity-mismatch', 'approved-amendment'):
        case = next(row for row in native['records'] if row['scenario_id'] == scenario)
        export = receipts[case['id']]
        assert case['synthetic'] is True and export['routing'] == case['routing']
        assert export['receipt']['signed']['payload']['case_id'] == case['id']
        assert export['receipt']['signed']['payload']['decision'] == case['routing']
        selected.append({**{key: case[key] for key in FIELDS},
                         'agent': {key: case['agent'][key] for key in
                                   ('execution_mode', 'provider', 'model', 'prompt_version', 'tool_reads')},
                         'receipt': export['receipt']})
    return {'schema': 'silentshift-recorded-tour/1', 'synthetic': True,
            'scope': 'Historical native live cases recorded November 11; viewing does not run IRIS or a model. These are demonstrations, not accuracy evidence.',
            'native_recorded_at': native['created_at'], 'runtime': native['iris_version'],
            'source': str(SOURCE.relative_to(ROOT)),
            'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'receipts_source': str(RECEIPTS.relative_to(ROOT)),
            'receipts_source_sha256': hashlib.sha256(RECEIPTS.read_bytes()).hexdigest(),
            'cases': selected}


if __name__ == '__main__':
    target = ROOT / 'docs/site/assets/recorded-cases.json'
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + '\n')
    print('Selected public synthetic records:', target.relative_to(ROOT))
