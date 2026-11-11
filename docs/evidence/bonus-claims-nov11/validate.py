"""Validate this documentation-only claims change; does not run the native app."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

ROOT = Path.cwd()
FILES = [
    'README.md', 'docs/SUBMISSION_CHECKLIST.md', 'docs/BONUS_EVIDENCE.md',
    'docs/BUILD_STATUS.md', 'docs/agent-runs/bonus-claims-nov11.md',
    'docs/agent-runs/bonus-comment-draft-nov11.md',
]
EVIDENCE = ROOT / 'docs/evidence/bonus-claims-nov11'
checked = []
for name in FILES:
    text = re.sub(r'```.*?```', '', (ROOT / name).read_text(), flags=re.S)
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+[^)]*)?\)', text):
        if target.startswith(('https:', 'http:', 'mailto:', '#')):
            continue
        target = target.split('#')[0]
        if target:
            checked.append({'document': name, 'target': target,
                            'exists': ((ROOT / name).parent / target).is_file()})
missing = [item for item in checked if not item['exists']]
assert not missing, missing
for path in EVIDENCE.glob('*.json'):
    json.loads(path.read_text())
video = json.loads((EVIDENCE / 'video.json').read_text())
assert video['matches_local'] and video['http_status'] == 200
assert hashlib.sha256((ROOT / 'evidence/video/silentshift-demo.mp4').read_bytes()).hexdigest() == video['sha256']
pub = json.loads((EVIDENCE / 'public.json').read_text())
assert pub['registry']['manifest_version'] == '0.3.1'
assert all(a['http_status'] == 200 and a['has_oex_link'] for a in pub['articles'])
assert pub['issue17']['state'] == 'OPEN'
assert pub['issue17']['comments'] == [] and pub['issue17']['labels'] == []
audit = json.loads((EVIDENCE / 'embedded-python.json').read_text())
for item in audit['files']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
subprocess.run(['git', 'diff', '--check'], check=True)
receipt = {
    'checked_at_ist': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).isoformat(),
    'relative_links_checked': len(checked), 'missing': missing,
    'json_receipts_parse': True, 'raw_video_hash_matches': True,
    'public_manifest_version': pub['registry']['manifest_version'],
    'article_publication_and_backlinks': True,
    'issue17_open_without_comments_or_labels': True,
    'native_source_hashes_match_historical_gate': True,
    'whitespace_check': 'passed', 'new_native_run': False, 'new_pytest_run': False,
    'scope': 'Documentation and anonymous artifact verification only; no runtime or release mutation.',
}
(EVIDENCE / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
