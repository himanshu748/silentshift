#!/usr/bin/env python3
"""Exercise actual IRIS REST → production → native agent → policy → route.

This command makes FIVE native investigations through the configured local
Ollama route. No external provider or mock server is supported.
Credentials are read from the environment and never written into evidence.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from silentshift.engine import strict_loads  # noqa: E402
from silentshift.evaluation import aggregate_native, load_dataset, _build154  # noqa: E402


def native_build(value: object) -> bool:
    return _build154(value)


def capture_matches(captured: object, run_id: str, case_ids: list[str], evaluation: dict) -> bool:
    return (isinstance(captured, dict) and captured.get("id") == run_id
            and captured.get("case_ids") == case_ids and captured.get("native") == evaluation)


class DenyRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # urllib forwards Authorization on redirects, including other origins.
        # An API redirect is a failure; never send credentials to its target.
        return None


class Client:
    def __init__(self, base: str, username: str, password: str):
        parsed = urlparse(base)
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("API URL must not embed credentials, query or fragment")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}):
            raise ValueError("Use HTTPS for a remote API")
        self.base = base.rstrip("/")
        self.auth = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
        self.opener = build_opener(DenyRedirects())

    def call(self, path: str, body: dict | None = None, *, anonymous: bool = False) -> tuple[int, object]:
        headers = {"Accept": "application/json"}
        if not anonymous:
            headers["Authorization"] = self.auth
        raw = None
        if body is not None:
            raw = json.dumps(body, allow_nan=False).encode()
            headers["Content-Type"] = "application/json"
        request = Request(self.base + path, data=raw, headers=headers, method="POST" if raw is not None else "GET")
        try:
            with self.opener.open(request, timeout=180) as response:
                result = response.read(2_000_001)
                if len(result) > 2_000_000:
                    raise ValueError("Response exceeded evidence size bound")
                return response.status, strict_loads(result.decode(), max_bytes=2_000_000)
        except HTTPError as error:
            # Error bodies may be gateway HTML or provider diagnostics. Do not
            # record them; the numeric status is sufficient for the assertion.
            return error.code, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default=os.environ.get("SILENTSHIFT_API_URL", "http://127.0.0.1:52773/silentshift/api"))
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/latest.json")
    parser.add_argument("--allow-model-calls", action="store_true", help="Confirm local inference or an authorized provider budget for five native runs")
    args = parser.parse_args()
    required = ("SILENTSHIFT_IRIS_USERNAME", "SILENTSHIFT_IRIS_PASSWORD")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print("BLOCKED: missing environment variables " + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        client = Client(args.api, *(os.environ[name] for name in required))
        status, health = client.call("/health")
        if status != 200 or not isinstance(health, dict):
            raise ValueError(f"Native health endpoint did not succeed (HTTP {status})")
        if not native_build(health.get("build")):
            raise ValueError("The actual IRIS build is not required Community AI Hub build154")
        if health.get("production", {}).get("running") is not True:
            raise ValueError("SilentShift.Production is not running")
        reviewer_authorized = (health.get("permissions") or {}).get("review") is True
        unauthorized, _ = client.call("/cases", anonymous=True)
        if unauthorized not in {401, 403}:
            raise ValueError("Unauthenticated case access was not rejected")
        if not args.allow_model_calls:
            print("BLOCKED: native runtime is reachable; rerun --allow-model-calls only for local inference or an authorized five-run provider budget.", file=sys.stderr)
            return 2
        dataset = load_dataset(ROOT / "fixtures/v1/scenarios.json")
        run_id = str(uuid.uuid4())
        records, checks = [], []
        for scenario in dataset["scenarios"]:
            started = time.monotonic()
            path = "/scenarios/" + scenario["id"] + "/run"
            status, record = client.call(path, {"run_id": run_id})
            if status != 200 or not isinstance(record, dict):
                raise ValueError(f"Scenario {scenario['id']} failed (HTTP {status})")
            record["http_elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
            # Poll persisted records only; never resubmit an unknown run with a
            # new idempotency key, which would cause another model invocation.
            for _ in range(12):
                if record.get("routing") != "PROCESSING":
                    break
                time.sleep(0.5)
                status, record = client.call("/cases/" + str(record["id"]))
                if status != 200 or not isinstance(record, dict):
                    raise ValueError("Persisted case polling failed")
            records.append(record)
            agent = record.get("agent") or {}
            reads = agent.get("tool_reads") or {}
            native = (agent.get("mode") == "native-ai-hub" and agent.get("status") == "returned"
                      and all(isinstance(reads.get(k), (int, float)) and reads[k] >= 1 for k in ("message", "contracts", "related")))
            trace = bool(str(record.get("trace_id") or "").strip())
            correct = (record.get("policy") or {}).get("decision") == scenario["ground_truth"]["decision"]
            held = scenario["ground_truth"]["decision"] != "ALLOW"
            safe_route = record.get("routing") == ("DELIVERED" if not held else "REVIEW" if scenario["ground_truth"]["decision"] == "REQUEST_REVIEW" else "QUARANTINED")
            repeat_status, repeated = client.call(path, {"run_id": run_id})
            dedup = (repeat_status == 200 and isinstance(repeated, dict) and repeated.get("id") == record.get("id")
                     and repeated.get("routing") == record.get("routing")
                     and repeated.get("delivery_receipt") == record.get("delivery_receipt")
                     and repeated.get("delivery_count") == record.get("delivery_count")
                     and record.get("delivery_count") == (0 if held else 1)
                     and (held or bool(record.get("delivery_receipt"))))
            # Reject release of the known contradiction through the actual
            # reviewer entry point. A viewer gets403; a reviewer must also403.
            denied = True
            critical_policy_gate = True
            if scenario["id"] == "quantity-mismatch":
                review_status, _ = client.call("/cases/" + str(record["id"]) + "/review", {
                    "action": "APPROVE", "reason": "Native safety test: critical contradiction must not be released.",
                    "expected_version": record.get("version"), "idempotency_key": str(uuid.uuid4())})
                denied = review_status == 403
                post_status, after_review = client.call("/cases/" + str(record["id"]))
                denied = (denied and post_status == 200 and isinstance(after_review, dict)
                          and after_review.get("routing") == "QUARANTINED"
                          and after_review.get("delivery_count") == 0)
                critical_policy_gate = denied and reviewer_authorized
            checks.append({"scenario_id": scenario["id"], "native_agent_and_tools": native, "trace_present": trace,
                           "policy_matches_ground_truth": correct, "routing_matches_ground_truth": safe_route,
                           "duplicate_reuses_case_and_receipt": dedup, "critical_release_denied": denied,
                           "critical_policy_test_used_reviewer": critical_policy_gate})
            print(f"{scenario['id']}: policy={(record.get('policy') or {}).get('decision')} route={record.get('routing')} native={native}")
        native_verified = all(item["native_agent_and_tools"] and item["trace_present"] for item in checks)
        artifact = {"created_at": datetime.now(timezone.utc).isoformat(), "dataset_version": dataset["dataset_version"],
                    "iris_version": health["build"], "production": "SilentShift.Production", "run_id": run_id,
                    "native_verified": native_verified, "records": records, "checks": checks,
                    "reviewer_authorized": reviewer_authorized,
                    "limitations": ["Synthetic fixed-clock dataset; not production data.",
                                    "Restart, real external destination and provider cancellation require separate native checks.",
                                    "Export metadata is observed by this client, not cryptographically attested."]}
        artifact["evaluation"] = aggregate_native(artifact, dataset)
        case_ids = [str(record["id"]) for record in records]
        capture_status, captured = client.call("/evaluations", {"run_id": run_id, "case_ids": case_ids})
        artifact["evaluation_persisted"] = capture_status == 200 and capture_matches(captured, run_id, case_ids, artifact["evaluation"])
        artifact["passed"] = native_verified and artifact["evaluation_persisted"] and artifact["evaluation"].get("passed") is True and all(all(value is True for key, value in item.items() if key != "scenario_id") for item in checks)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
        print(f"Evidence saved: {args.output}")
        return 0 if artifact["passed"] else 1
    except (URLError, TimeoutError, ValueError, KeyError, TypeError, OSError) as error:
        # Never print request objects or exception text from network libraries.
        message = str(error) if isinstance(error, ValueError) else type(error).__name__
        print("BLOCKED/FAILED: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
