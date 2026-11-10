#!/usr/bin/env python3
"""Prepare bounded CSV orders for the existing native API. No policy runs here."""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "scripts"))
from silentshift.csv_orders import (
    FEED as FEED,
)
from silentshift.csv_orders import (
    MAX_BYTES as MAX_BYTES,
)
from silentshift.csv_orders import (
    MAX_ROWS as MAX_ROWS,
)
from silentshift.csv_orders import (
    REFERENCE as REFERENCE,
)
from silentshift.csv_orders import (
    digest as digest,
)
from silentshift.csv_orders import (
    prepare,
)
from verify_native import Client, native_build


def submit(bundle: dict, client: Client, checkpoint=lambda: None) -> dict:
    status, health = client.call("/health")
    if status != 200 or not isinstance(health, dict) or not native_build(health.get("build")) or health.get("production", {}).get("running") is not True:
        raise ValueError("Required native production is unavailable")
    outcomes = []
    state = {"mode": "shadow-simulator-only", "feed_sha256": bundle["feed_sha256"], "lines": outcomes, "orders": []}
    bundle["native_results"] = state
    for record in bundle["records"]:
        state["pending_event_id"] = record["message"]["event_id"]
        checkpoint()
        status, case = client.call("/messages", record["message"])
        if status != 200 or not isinstance(case, dict) or not case.get("id"):
            # Do not retry an uncertain dispatch with another identity.
            raise ValueError("Native submission failed; inspect persisted cases before resuming the same bundle")
        state["pending_case_id"] = case["id"]
        checkpoint()
        deadline = time.monotonic() + 180
        while case.get("routing") == "PROCESSING" and time.monotonic() < deadline:
            time.sleep(1)
            status, updated = client.call("/cases/" + case["id"])
            if status != 200 or not isinstance(updated, dict):
                raise ValueError("Native case polling failed")
            case = updated
        outcomes.append({k: record[k] for k in ("partner", "order_id", "line_id", "source_row")} |
                        {"case_id": case["id"], "trace_id": case.get("trace_id"), "routing": case.get("routing"),
                         "delivery_count": case.get("delivery_count"),
                         "agent_status": (case.get("agent") or {}).get("status"),
                         "agent_failure_code": (case.get("agent") or {}).get("failure_code")})
        state.pop("pending_event_id", None)
        state.pop("pending_case_id", None)
        checkpoint()
    orders = {}
    for result in outcomes:
        key = json.dumps([result["partner"], result["order_id"]])
        orders.setdefault(key, []).append(result)
    state["orders"] = [{"partner": group[0]["partner"], "order_id": group[0]["order_id"],
                        "shadow_disposition": "ALL_SUBMITTED_LINES_SIMULATED" if all(r["routing"] == "DELIVERED" and r["delivery_count"] == 1 for r in group) else "HOLD",
                        "order_completeness": "not_verified", "atomic_order_delivery": False} for group in orders.values()]
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", required=True, type=Path)
    parser.add_argument("--approved", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--submit-local", action="store_true", help="Invoke local native investigations; may create per-line simulator receipts")
    args = parser.parse_args()
    try:
        if args.submit_local and shutil.disk_usage(ROOT).free < 2 * 1024**3:
            raise ValueError("Native CSV submission requires 2 GiB free host space")
        bundle = prepare(args.orders, args.approved)
        # Operator chooses a new private output; never overwrite retained evidence.
        with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as stream:
            def checkpoint():
                stream.seek(0)
                json.dump(bundle, stream, indent=2, allow_nan=False, ensure_ascii=False)
                stream.write("\n")
                stream.truncate()
                stream.flush()
                os.fsync(stream.fileno())
            checkpoint()
            if args.submit_local:
                # No user-controlled remote destination or redirect is admitted.
                client = Client("http://127.0.0.1:52773/silentshift/api", os.environ["SILENTSHIFT_IRIS_USERNAME"], os.environ["SILENTSHIFT_IRIS_PASSWORD"])
                try:
                    submit(bundle, client, checkpoint)
                    bundle["submission_status"] = "COMPLETED"
                except (ValueError, OSError):
                    bundle["submission_status"] = "INCOMPLETE_INSPECT_BEFORE_RESUME"
                    checkpoint()
                    raise
            checkpoint()
        print("Prepared CSV pilot bundle" + (" and native shadow results" if args.submit_local else "; no API calls"))
        return 0
    except (ValueError, OSError, KeyError, csv.Error, UnicodeError):
        print("CSV pilot failed; check documented layout, local configuration and retained case state. Input values and credentials withheld.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
