"""The XData relocation must not tune the released investigator prompt."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_system_prompt_relocation_preserves_original_bytes():
    source = (ROOT / "src/SilentShift/AI/Investigator.cls").read_text()
    block = re.search(r'XData SystemPrompt \[ MimeType = "application/json" \]\s*\{(.*?)\n\}', source, re.DOTALL)
    assert block is not None
    fragments = json.loads(block.group(1))
    assert all(isinstance(part, str) for part in fragments)
    prompt = "".join(fragments).encode("utf-8")
    assert len(prompt) == 1959
    assert hashlib.sha256(prompt).hexdigest() == "6e7453ef1af46af157c64dbc0ea93953da508c5b278b3dd1c25b71b5ff7aedc3"
    assert 'Set agent.SystemPrompt = ..SystemPrompt()' in source


def test_api_uuid_pattern_keeps_objectscript_pattern_spacing():
    source = (ROOT / "src/SilentShift/API.cls").read_text()
    # Spaces within a COS pattern alternation are syntax, not formatting.
    assert source.count("runId'?36(1AN,1\"-\")") == 2
    assert "runId'?36(1AN, 1\"-\")" not in source
