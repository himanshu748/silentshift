#!/usr/bin/env python3
"""Prepare bounded CSV orders for the existing native API. No policy runs here."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "scripts"))
from silentshift.engine import _decimal, _time, _text  # noqa: E402
from verify_native import Client, native_build  # noqa: E402

FEED = "partner,event_id,order_id,line_id,occurred_at,product_id,quantity,unit,business_unit".split(",")
REFERENCE = "partner,order_id,line_id,revision,effective_from,effective_to,approved_by,approved_at,product_id,quantity,unit,business_unit".split(",")
MAX_BYTES = 131072
MAX_ROWS = 20


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read_csv(path: Path, columns: list[str]) -> tuple[list[dict], str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("CSV input must be a regular file, not a symlink")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES or b"\x00" in raw:
        raise ValueError("CSV input exceeds 128 KiB or contains NUL")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)) or set(headers) != set(columns):
        raise ValueError("CSV headers must match the documented layout exactly")
    result = []
    for row in reader:
        if len(result) >= MAX_ROWS:
            raise ValueError("Pilot files are limited to 20 records")
        if set(row) != set(columns) or any(value is None for value in row.values()):
            raise ValueError("CSV record has a missing or extra cell")
        for key, value in row.items():
            if key == "effective_to" and value == "":
                continue
            if not _text(value) or value != value.strip():
                raise ValueError("CSV cells must be bounded text without surrounding whitespace or control characters")
        if not re.fullmatch(r"[0-9]{1,13}(?:\.[0-9]{1,9})?", row["quantity"]):
            raise ValueError("Quantity must use bounded plain decimal notation")
        quantity = _decimal(row["quantity"])
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        for field in ("occurred_at", "effective_from", "approved_at"):
            if field in row:
                _time(row[field])
        if row.get("effective_to"):
            if _time(row["effective_to"]) <= _time(row["effective_from"]):
                raise ValueError("Reference validity interval must be increasing")
        # Control characters (including embedded newlines) are rejected above,
        # so each admitted record occupies one physical line. DictReader may
        # skip blank lines; use its actual line number rather than a row index.
        row["source_row"] = reader.line_num
        result.append(row)
    if not result:
        raise ValueError("CSV file contains no records")
    return result, hashlib.sha256(raw).hexdigest()


def identity(row: dict) -> list[str]:
    return [row[k] for k in ("partner", "order_id", "line_id")]


def prepare(feed: Path, approved: Path) -> dict:
    if feed.resolve() == approved.resolve() or os.path.samefile(feed, approved):
        raise ValueError("Incoming orders and approved references must be separate files")
    rows, feed_hash = read_csv(feed, FEED)
    references, ref_hash = read_csv(approved, REFERENCE)
    messages, catalog, seen, revisions = [], [], set(), set()
    for row in rows:
        key = (row["partner"], row["event_id"], row["line_id"])
        if key in seen:
            raise ValueError("Duplicate event/line identity within CSV file")
        seen.add(key)
        message = {k: row[k] for k in ("occurred_at", "product_id", "quantity", "unit", "business_unit")}
        message.update(kind="order", source=row["partner"],
                       event_id="csv:" + digest(list(key)),
                       correlation_id="csv-order:" + digest([row["partner"], row["order_id"]]),
                       contract_id="csv-line:" + digest(identity(row)))
        messages.append({"message": message, "order_id": row["order_id"], "line_id": row["line_id"],
                         "partner": row["partner"], "source_row": row["source_row"]})
    for row in references:
        key = (*identity(row), row["revision"])
        if key in revisions:
            raise ValueError("Duplicate reference revision within approved export")
        revisions.add(key)
        reference = {k: row[k] for k in ("product_id", "quantity", "unit", "business_unit", "effective_from")}
        reference.update(id="csv-ref:" + digest(list(key)), contract_id="csv-line:" + digest(identity(row)),
                         authority="approved", effective_to=row["effective_to"] or None,
                         timestamp_semantics="event_time",
                         approval_provenance={"approved_by": row["approved_by"], "approved_at": row["approved_at"],
                                              "revision": row["revision"], "source_sha256": ref_hash,
                                              "source_row": row["source_row"]})
        catalog.append(reference)
    bundle = {"schema": "silentshift-csv-pilot/1", "mapping_version": "orders-csv/1",
            "mode": "shadow-simulator-only", "feed_sha256": feed_hash,
            "approved_sha256": ref_hash, "records": messages, "references": catalog}
    if len(json.dumps(bundle, ensure_ascii=False, indent=2, allow_nan=False).encode()) + 1 > MAX_BYTES:
        raise ValueError("Prepared import exceeds native pilot byte limit")
    return bundle


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
