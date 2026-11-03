"""Verification tooling must not leak credentials or accept a different build."""
import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest


spec = importlib.util.spec_from_file_location("verify_native", Path(__file__).parents[1] / "scripts/verify_native.py")
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


@pytest.mark.parametrize("version,expected", [
    ("2026.3.0AI.154.0", True),
    ("IRIS for UNIX Version2026.3.0AI (Build154)", True),
    ("IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT", True),
    ("2026.3.0AI.154.0.1", False),
    ("2026.3.0AI.1154.0", False),
    ("2026.3.0AI (Build1154)", False),
    ("2026.3.0AI (Build162)", False),
    ("2026.3.0AI (Build154U1)", False),
])
def test_build_gate(version, expected):
    assert native.native_build(version) is expected


def test_credentialed_api_client_refuses_cross_origin_redirect():
    destination_requests = []

    class Destination(BaseHTTPRequestHandler):
        def do_GET(self):
            destination_requests.append(self.headers.get("Authorization"))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{}')

        def log_message(self, *args):
            pass

    destination = ThreadingHTTPServer(("127.0.0.1", 0), Destination)

    class Redirector(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{destination.server_port}/credential-target")
            self.end_headers()

        def log_message(self, *args):
            pass

    source = ThreadingHTTPServer(("127.0.0.1", 0), Redirector)
    threads = [Thread(target=server.serve_forever, daemon=True) for server in (destination, source)]
    for thread in threads:
        thread.start()
    try:
        client = native.Client(f"http://127.0.0.1:{source.server_port}", "synthetic-user", "synthetic-test-password")
        assert client.call("/redirect") == (302, None)
        assert destination_requests == []
    finally:
        for server in (source, destination):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)


@pytest.mark.parametrize("url", ["http://external.invalid/api", "https://user:secret@example.invalid", "https://example.invalid/?secret=value"])
def test_client_rejects_unsafe_api_destination(url):
    with pytest.raises(ValueError):
        native.Client(url, "synthetic-user", "synthetic-test-password")


def test_evaluation_receipt_must_match_observed_native_results():
    evaluation = {"passed": True, "accepted_records": 5, "unsafe_release": {"count": 0, "denominator": 4}}
    receipt = {"id": "run-id", "case_ids": ["a", "b"], "native": evaluation}
    assert native.capture_matches(receipt, "run-id", ["a", "b"], evaluation)
    assert not native.capture_matches({}, "run-id", ["a", "b"], evaluation)
    assert not native.capture_matches({**receipt, "id": "another-run"}, "run-id", ["a", "b"], evaluation)
    assert not native.capture_matches({**receipt, "case_ids": ["b", "a"]}, "run-id", ["a", "b"], evaluation)
    assert not native.capture_matches({**receipt, "native": {**evaluation, "accepted_records": 4}}, "run-id", ["a", "b"], evaluation)
    failed = {**evaluation, "passed": False}
    # A failed benchmark can still be faithfully persisted. Persistence is
    # independent of the main verifier's separate evaluation-passed gate.
    assert native.capture_matches({**receipt, "native": failed}, "run-id", ["a", "b"], failed)
