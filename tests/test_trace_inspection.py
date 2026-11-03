"""Read-only trace inspection must never compile code or invoke a model."""
import importlib.util
import sys
from pathlib import Path

import pytest

scripts = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location("verify_native_trace", scripts / "verify_native_trace.py")
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


@pytest.mark.parametrize("present", [False, True])
def test_inspection_requires_existing_class_without_mutations(monkeypatch, tmp_path, present):
    commands = []
    inspected = []
    output = tmp_path / "inspection.json"
    monkeypatch.setattr(sys, "argv", ["verify_native_trace.py", "--inspect-case", "synthetic-case", "--output", str(output)])
    monkeypatch.setattr(trace, "read_env", lambda _: {})

    def native(args, command, marker):
        commands.append(command)
        assert marker == "TRACE_PRESENT="
        return "1" if present else "0"

    def inspect(args, case_id):
        inspected.append(case_id)
        return {"agent": {"model_invoked": False}}

    monkeypatch.setattr(trace, "native", native)
    monkeypatch.setattr(trace, "inspect", inspect)
    monkeypatch.setattr(trace, "validate", lambda observed, budget: {"record_valid": True})
    assert trace.main() == (0 if present else 1)
    assert inspected == (["synthetic-case"] if present else [])
    assert len(commands) == 1
    assert "$SYSTEM.OBJ.Load" not in commands[0]
    assert "CompiledClass" in commands[0]
