"""The HTTP boundary shares the exact CLI parser; no IRIS execution claimed."""
import json

import pytest
from silentshift.csv_orders import prepare_bytes, prepare_request


def files():
    return {
        "orders_csv": "partner,event_id,order_id,line_id,occurred_at,product_id,quantity,unit,business_unit\npartner,one,PO-1,1,2026-11-07T12:00:00Z,SKU,20,CASE,WEST\n",
        "approved_csv": "partner,order_id,line_id,revision,effective_from,effective_to,approved_by,approved_at,product_id,quantity,unit,business_unit\npartner,PO-1,1,v1,2026-11-01T00:00:00Z,,buyer,2026-10-31T00:00:00Z,SKU,240,EA,WEST\n",
    }


def commitment():
    body = files()
    preview = prepare_request(json.dumps(body))
    return {**body, "preview_hash": preview["preview_hash"], "confirmation": True,
            "reason": "Approved export supplied by the buyer."}


def test_http_and_cli_byte_mapping_are_identical():
    body = files()
    result = prepare_request(json.dumps(body))
    assert result["bundle"] == prepare_bytes(body["orders_csv"].encode(), body["approved_csv"].encode())
    assert result["bundle"]["records"][0]["message"]["quantity"] == "20"
    assert result["bundle"]["references"][0]["quantity"] == "240"
    assert prepare_request(json.dumps(commitment()), commit=True)["preview_hash"] == result["preview_hash"]


@pytest.mark.parametrize("confirmation", [False, 1, "true", None])
def test_confirmation_is_explicit_boolean(confirmation):
    body = commitment()
    body["confirmation"] = confirmation
    with pytest.raises(ValueError, match="Confirm authority"):
        prepare_request(json.dumps(body), commit=True)


@pytest.mark.parametrize("reason", ["short", " " * 20, None, ["buyer"], "x" * 161])
def test_import_source_note_is_bounded_text(reason):
    body = commitment()
    body["reason"] = reason
    with pytest.raises(ValueError):
        prepare_request(json.dumps(body), commit=True)


def test_changed_files_invalidate_the_reviewed_preview():
    body = commitment()
    body["orders_csv"] = body["orders_csv"].replace(",20,CASE,", ",21,CASE,")
    with pytest.raises(ValueError, match="Preview no longer matches"):
        prepare_request(json.dumps(body), commit=True)


def test_client_cannot_supply_an_authority_bundle_or_extra_fields():
    body = commitment()
    body["references"] = [{"authority": "approved"}]
    with pytest.raises(ValueError, match="two documented CSV"):
        prepare_request(json.dumps(body), commit=True)


def test_unicode_byte_limit_and_duplicate_json_keys_are_enforced():
    body = files()
    body["orders_csv"] = "é" * 66000
    with pytest.raises(ValueError, match="128 KiB"):
        prepare_request(json.dumps(body, ensure_ascii=False))
    with pytest.raises(ValueError):
        prepare_request('{"orders_csv":"a","orders_csv":"b","approved_csv":"c"}')


def test_same_export_cannot_be_its_own_authority():
    body = files()
    body["approved_csv"] = body["orders_csv"]
    with pytest.raises(ValueError, match="independent exports"):
        prepare_request(json.dumps(body))


def test_bom_and_crlf_preserve_original_source_hashes():
    body = files()
    body["orders_csv"] = "\ufeff" + body["orders_csv"].replace("\n", "\r\n")
    body["approved_csv"] = "\ufeff" + body["approved_csv"].replace("\n", "\r\n")
    direct = prepare_bytes(body["orders_csv"].encode(), body["approved_csv"].encode())
    assert prepare_request(json.dumps(body))["bundle"] == direct
    assert direct["records"][0]["source_row"] == 2


def test_source_note_accepts_its_declared_boundaries():
    for length in (12, 160):
        body = commitment()
        body["reason"] = "x" * length
        assert prepare_request(json.dumps(body), commit=True)["reason"] == body["reason"]
