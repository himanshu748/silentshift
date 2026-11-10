"""Bounded CSV order mapping shared by CLI and native Embedded Python.

This module performs no I/O except the explicit file wrapper, no model calls,
and no reference-store writes. Callers must separately authorize imports.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
from pathlib import Path

from .engine import _decimal, _text, _time, strict_loads

FEED = ["partner", "event_id", "order_id", "line_id", "occurred_at", "product_id", "quantity", "unit", "business_unit"]
REFERENCE = ["partner", "order_id", "line_id", "revision", "effective_from", "effective_to", "approved_by", "approved_at", "product_id", "quantity", "unit", "business_unit"]
MAX_BYTES = 131072
MAX_ROWS = 20


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read_csv_bytes(raw: bytes, columns: list[str]) -> tuple[list[dict], str]:
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
    if any(path.is_symlink() or not path.is_file() for path in (feed, approved)):
        raise ValueError("CSV input must be a regular file, not a symlink")
    if feed.resolve() == approved.resolve() or os.path.samefile(feed, approved):
        raise ValueError("Incoming orders and approved references must be separate files")
    with feed.open("rb") as stream:
        feed_raw = stream.read(MAX_BYTES + 1)
    with approved.open("rb") as stream:
        approved_raw = stream.read(MAX_BYTES + 1)
    return prepare_bytes(feed_raw, approved_raw)


def prepare_bytes(feed_raw: bytes, approved_raw: bytes) -> dict:
    rows, feed_hash = read_csv_bytes(feed_raw, FEED)
    references, ref_hash = read_csv_bytes(approved_raw, REFERENCE)
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


def prepare_request(raw: str, *, commit: bool = False) -> dict:
    """Rebuild authority from the original CSVs; never accept a client bundle."""
    request = strict_loads(raw, max_bytes=524288)
    fields = {"orders_csv", "approved_csv"}
    if commit:
        fields |= {"preview_hash", "confirmation", "reason"}
    if not isinstance(request, dict) or set(request) != fields:
        raise ValueError("Supply the two documented CSV files")
    for field in ("orders_csv", "approved_csv"):
        if not isinstance(request[field], str) or len(request[field].encode("utf-8")) > MAX_BYTES:
            raise ValueError("Each UTF-8 CSV must be at most 128 KiB")
    if request["orders_csv"] == request["approved_csv"]:
        raise ValueError("Incoming orders and approved references must be independent exports")
    bundle = prepare_bytes(request["orders_csv"].encode("utf-8"), request["approved_csv"].encode("utf-8"))
    preview_hash = digest(bundle)
    result = {"bundle": bundle, "preview_hash": preview_hash}
    if commit:
        if request["preview_hash"] != preview_hash:
            raise ValueError("Preview no longer matches these files; preview again")
        if request["confirmation"] is not True:
            raise ValueError("Confirm authority to import the approved export")
        reason = request["reason"]
        if not _text(reason) or not 12 <= len(reason.strip()) <= 160:
            raise ValueError("Describe the approved source in 12 to 160 characters")
        result["reason"] = reason.strip()
    return result
