"""New trace metadata must not move any released persistent message slot."""
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_provider_request_preserves_released_storage_slots():
    baseline = subprocess.run(
        ['git', 'show', '1c92e09:src/SilentShift/Provider/CallRequest.cls'],
        cwd=ROOT, text=True, capture_output=True, check=True,
    ).stdout
    released = re.findall(r'^Property (\w+) As ', baseline, re.MULTILINE)
    source = (ROOT / 'src/SilentShift/Provider/CallRequest.cls').read_text()
    block = re.search(r'Storage Default\s*\{(.*?)\n\}', source, re.DOTALL)
    assert block is not None
    storage = ET.fromstring('<Storage>' + block[1] + '</Storage>')
    values = storage.find('Data').findall('Value')
    slots = {int(node.attrib['name']): node.findtext('Value') for node in values}
    assert [slots[n] for n in range(1, len(released) + 1)] == released
    assert slots[len(released) + 1] == 'FinalFormatVersion'
    assert len(slots) == len(released) + 1
