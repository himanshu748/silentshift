import copy
import csv
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location("pilot_orders", Path(__file__).parents[1] / "pilot/orders.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def write(path, columns, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)
    return path


def inputs(tmp_path):
    feed = write(tmp_path / "orders.csv", pilot.FEED, [["partner-a", "event-1", "PO-1", "1", "2026-11-06T15:00:00Z", "SKU-1", "20", "CASE", "WEST"]])
    refs = write(tmp_path / "approved.csv", pilot.REFERENCE, [["partner-a", "PO-1", "1", "v1", "2026-11-01T00:00:00Z", "", "buyer-ops", "2026-10-31T12:00:00Z", "SKU-1", "240", "EA", "WEST"]])
    return feed, refs


def test_maps_independent_authority_without_transforming_quantity(tmp_path):
    feed, refs = inputs(tmp_path)
    bundle = pilot.prepare(feed, refs)
    message = bundle["records"][0]["message"]
    reference = bundle["references"][0]
    assert message["quantity"] == "20" and message["unit"] == "CASE"
    assert reference["quantity"] == "240" and reference["unit"] == "EA"
    assert message["contract_id"] == reference["contract_id"]
    assert reference["approval_provenance"]["source_sha256"] == bundle["approved_sha256"]
    assert bundle["records"][0]["source_row"] == 2
    assert pilot.prepare(feed, refs) == bundle


@pytest.mark.parametrize("quantity", ["NaN", "Infinity", "0", "-1", "1.0000000001", "1e100000000", " 20"])
def test_rejects_unsafe_numeric_inputs(tmp_path, quantity):
    feed, refs = inputs(tmp_path)
    feed.write_text(feed.read_text().replace(",20,CASE,", f",{quantity},CASE,"))
    with pytest.raises(ValueError):
        pilot.prepare(feed, refs)


def test_rejects_duplicate_identity_and_header(tmp_path):
    feed, refs = inputs(tmp_path)
    original = feed.read_text()
    feed.write_text(original + original.splitlines()[1] + "\n")
    with pytest.raises(ValueError, match="Duplicate"):
        pilot.prepare(feed, refs)
    feed.write_text(original.replace("event_id", "partner"))
    with pytest.raises(ValueError, match="headers"):
        pilot.prepare(feed, refs)


def test_source_row_tracks_physical_line_when_csv_has_blank_lines(tmp_path):
    feed, refs = inputs(tmp_path)
    lines = feed.read_text().splitlines()
    feed.write_text(lines[0] + "\n\n" + lines[1] + "\n")
    assert pilot.prepare(feed, refs)["records"][0]["source_row"] == 3


def test_rejects_extra_cell_naive_time_same_file_and_oversize(tmp_path):
    feed, refs = inputs(tmp_path)
    original = feed.read_text()
    with pytest.raises(ValueError, match="separate"):
        pilot.prepare(feed, feed)
    feed.write_text(original.rstrip() + ",unexpected\n")
    with pytest.raises(ValueError):
        pilot.prepare(feed, refs)
    feed.write_text(original.replace("T15:00:00Z", "T15:00:00"))
    with pytest.raises(ValueError):
        pilot.prepare(feed, refs)
    feed.write_bytes(b"x" * (pilot.MAX_BYTES + 1))
    with pytest.raises(ValueError):
        pilot.prepare(feed, refs)


def test_event_identity_survives_reordering_but_changed_order_conflicts(tmp_path):
    feed, refs = inputs(tmp_path)
    first = pilot.prepare(feed, refs)["records"][0]["message"]
    feed.write_text(feed.read_text().replace("PO-1", "PO-2"))
    second = pilot.prepare(feed, refs)["records"][0]["message"]
    assert first["event_id"] == second["event_id"]
    assert first["contract_id"] != second["contract_id"]


class FakeNative:
    """Unit-test transport only; no native execution is claimed."""
    def __init__(self, routes, fail_second=False):
        self.routes = iter(routes)
        self.calls = 0
        self.fail_second = fail_second

    def call(self, path, body=None):
        if path == "/health":
            return 200, {"build": "IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT", "production": {"running": True}}
        self.calls += 1
        if self.fail_second and self.calls == 2:
            raise OSError("uncertain dispatch")
        route = next(self.routes)
        return 200, {"id": str(self.calls), "trace_id": str(100+self.calls), "routing": route,
                     "delivery_count": 1 if route == "DELIVERED" else 0}


def test_order_summary_holds_mixed_outcomes_and_never_claims_atomic_delivery(tmp_path):
    feed, refs = inputs(tmp_path)
    bundle = pilot.prepare(feed, refs)
    second = copy.deepcopy(bundle["records"][0])
    second["line_id"] = "2"
    second["message"]["event_id"] = "second-event"
    bundle["records"].append(second)
    checkpoints = []
    report = pilot.submit(bundle, FakeNative(["DELIVERED", "QUARANTINED"]), lambda: checkpoints.append(copy.deepcopy(bundle)))
    assert report["orders"][0]["shadow_disposition"] == "HOLD"
    assert report["orders"][0]["atomic_order_delivery"] is False
    assert report["orders"][0]["order_completeness"] == "not_verified"
    assert checkpoints[0]["native_results"]["pending_event_id"]


def test_uncertain_dispatch_retains_completed_lines_and_pending_identity(tmp_path):
    feed, refs = inputs(tmp_path)
    bundle = pilot.prepare(feed, refs)
    second = copy.deepcopy(bundle["records"][0])
    second["message"]["event_id"] = "second-event"
    bundle["records"].append(second)
    client = FakeNative(["DELIVERED"], fail_second=True)
    with pytest.raises(OSError):
        pilot.submit(bundle, client)
    assert len(bundle["native_results"]["lines"]) == 1
    assert bundle["native_results"]["pending_event_id"] == "second-event"
    assert client.calls == 2


def test_existing_output_prevents_any_native_submission(tmp_path, monkeypatch):
    feed, refs = inputs(tmp_path)
    output = tmp_path / "saved.json"
    output.write_text("preserve")
    monkeypatch.setattr(pilot.shutil, "disk_usage", lambda _: SimpleNamespace(free=3 * 1024**3))
    monkeypatch.setattr(pilot, "Client", lambda *args: pytest.fail("client must not be created"))
    monkeypatch.setattr(pilot.sys, "argv", ["orders.py", "--orders", str(feed), "--approved", str(refs), "--output", str(output), "--submit-local"])
    assert pilot.main() == 1
    assert output.read_text() == "preserve"


def test_native_submission_stops_before_any_side_effect_when_space_is_low(tmp_path, monkeypatch):
    feed, refs = inputs(tmp_path)
    output = tmp_path / "result.json"
    monkeypatch.setattr(pilot.shutil, "disk_usage", lambda _: SimpleNamespace(free=100))
    monkeypatch.setattr(pilot, "Client", lambda *args: pytest.fail("no native calls permitted"))
    monkeypatch.setattr(pilot.sys, "argv", ["orders.py", "--orders", str(feed), "--approved", str(refs), "--output", str(output), "--submit-local"])
    assert pilot.main() == 1
    assert not output.exists()


def test_failed_investigation_is_visible_alongside_the_held_route(tmp_path):
    feed, refs = inputs(tmp_path)
    bundle = pilot.prepare(feed, refs)
    class FailedNative(FakeNative):
        def call(self, path, body=None):
            status, result = super().call(path, body)
            if path == "/messages":
                result["agent"] = {"status": "failed", "failure_code": "AI_UNAVAILABLE_OR_TIMEOUT"}
            return status, result
    report = pilot.submit(bundle, FailedNative(["QUARANTINED"]))
    assert report["lines"][0]["agent_status"] == "failed"
    assert report["lines"][0]["agent_failure_code"] == "AI_UNAVAILABLE_OR_TIMEOUT"
    assert report["orders"][0]["shadow_disposition"] == "HOLD"
