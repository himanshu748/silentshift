"""The XData relocation must not tune the released investigator prompt."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def test_system_prompt_relocation_preserves_original_bytes():
    source = (ROOT / "src/SilentShift/AI/Investigator.cls").read_text()
    block = re.search(r'XData SystemPrompt \[ MimeType = "application/json" \]\s*\{(.*?)\n\}', source, re.S)
    assert block is not None
    fragments = json.loads(block.group(1))
    assert all(isinstance(part, str) for part in fragments)
    prompt = "".join(fragments).encode("utf-8")
    assert len(prompt) == 1959
    assert hashlib.sha256(prompt).hexdigest() == "6e7453ef1af46af157c64dbc0ea93953da508c5b278b3dd1c25b71b5ff7aedc3"
    assert 'Set agent.SystemPrompt = ..SystemPrompt()' in source
