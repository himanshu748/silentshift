#!/usr/bin/env python3
"""Export an existing IRIS session using its installed vendor SVG renderer.

This invokes no model, compiles nothing, and changes no security configuration.
The vendor renderer reads business messages and builds its normal temporary cache.
The result is a vendor-rendered SVG export, not an authenticated portal capture.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--context", default="colima-silentshift")
    parser.add_argument("--container", default="silentshift-clean-iris-1")
    parser.add_argument("--namespace", default="SILENTSHIFT")
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    if args.session < 1 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", args.namespace):
        parser.error("session and namespace must identify an existing native session")

    render_id = "ss-native-svg-" + uuid.uuid4().hex
    remote_file = "/tmp/" + render_id + ".svg"
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    docker = ["docker", "--context", args.context]

    setup = [
        'set renderOriginalIO=$io,renderOpened=0',
        'set %request=##class(%CSP.Request).%New()',
        'set %response=##class(%CSP.Response).%New()',
        f'set %session=##class(%CSP.Session).%New("{render_id}",0)',
        f'set %request.Data("SESSIONID",1)="{args.session}"',
        'set %request.Data("PAGE",1)=1',
        'set %request.Data("PRINTABLE",1)=1',
        'set %request.Data("MSGPERPAGE",1)=200',
        'set %request.Data("INCLUDEEVENTS",1)=0',
        'set %request.Data("INCLUDEIOLOG",1)=0',
        'set %request.Data("INCLUDEACKS",1)=0',
        'set %request.Data("SHOWINTERNAL",1)=1',
        'set %svgpage=##class(EnsPortal.SVG.VisualTrace).%New()',
        'do %svgpage.%ApplyURLParms()',
        f'set renderFile="{remote_file}"',
        'open renderFile:("WNS"):5',
        'if \'$test { throw ##class(%Exception.General).%New("SVG_OUTPUT_OPEN_FAILED") }',
        'set renderOpened=1',
        'use renderFile',
        'write "<?xml version=""1.0"" ?>",!',
        'do %svgpage.%DrawSVGPage()',
        'use renderOriginalIO',
        'close renderFile',
        'set renderOpened=0',
        'do ##class(EnsPortal.SVG.VisualTrace).ClearTraceData()',
        'write "SSVG_OK=1",!',
    ]
    catch = [
        'use renderOriginalIO',
        'if renderOpened { close renderFile }',
        'if $isobject($get(%session)) { do ##class(EnsPortal.SVG.VisualTrace).ClearTraceData() }',
        'write "SSVG_ERROR=",error.Name," LOCATION=",error.Location,!',
    ]
    script = "try { " + " ".join(setup) + " } catch error { " + " ".join(catch) + " }\nhalt\n"
    command = docker + ["exec", "-i", args.container, "iris", "session", "IRIS", "-U", args.namespace]
    receipt: dict[str, object] = {
        "artifact_type": "native-vendor-svg-export",
        "authenticated_portal_capture": False,
        "session_id": args.session,
        "renderer_class": "EnsPortal.SVG.VisualTrace",
        "renderer_method": "%DrawSVGPage",
        "model_calls": 0,
        "compiled_classes": 0,
        "security_changes": 0,
    }
    receipt_path = output.with_suffix(".receipt.json")
    try:
        run = subprocess.run(command, input=script, text=True, capture_output=True, timeout=60, check=False)
        copy = subprocess.run(docker + ["cp", args.container + ":" + remote_file, str(output)], capture_output=True, check=False)
        if run.returncode != 0 or copy.returncode != 0:
            output.with_suffix(".renderer.log").write_text(run.stdout + run.stderr)
            errors = [line.strip() for line in run.stdout.splitlines() if "SSVG_ERROR=" in line]
            receipt.update(ok=False, error=errors[0] if errors else "RENDERER_DID_NOT_COMPLETE")
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
            print(json.dumps(receipt, indent=2))
            return 1
    finally:
        subprocess.run(docker + ["exec", args.container, "rm", "-f", "--", remote_file], check=False, capture_output=True)

    data = output.read_bytes()
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        receipt.update(ok=False, error="SVG_XML_INVALID", detail=str(error))
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))
        return 1
    svg_ns = "{http://www.w3.org/2000/svg}"
    visible_text = "\n".join("".join(node.itertext()) for node in root.iter(svg_ns + "text"))
    header_ids = [node.get("id") for node in root.iter(svg_ns + "g") if re.fullmatch(r"[0-9]+", node.get("id", ""))]
    header_query = '\n'.join([
        'set renderStatement=##class(%SQL.Statement).%New()',
        'set renderStatus=renderStatement.%Prepare("SELECT ID,Type,CorrespondingMessageId FROM Ens.MessageHeader WHERE SessionId = ? ORDER BY ID")',
        f'set renderRows=renderStatement.%Execute({args.session})',
        'while renderRows.%Next() { write "SSVG_HEADER=",renderRows.ID,"|",renderRows.Type,"|",renderRows.CorrespondingMessageId,! }',
        'halt',
        '',
    ])
    header_run = subprocess.run(command, input=header_query, text=True, capture_output=True, timeout=30, check=True)
    native_headers = [
        {"id": match.group(1), "type": int(match.group(2)), "corresponding_id": match.group(3)}
        for match in re.finditer(r"SSVG_HEADER=([0-9]+)\|([0-9]+)\|([0-9]*)", header_run.stdout)
    ]
    text = data.decode("utf-8")
    credential_patterns = [
        r'(?i)\bBearer\s+[A-Za-z0-9_-]{16,}',
        r'(?i)CSPCHD=',
        r'(?i)CSPSESSIONID=',
        r'(?i)"api_key"\s*:',
        r'(?i)"authorization"\s*:',
    ]
    checks: dict[str, bool] = {
        "xml_valid": True,
        "native_svg_root": root.tag == svg_ns + "svg",
        "native_header_groups_present": bool(header_ids),
        "header_ids_match_native_session": header_ids == [header["id"] for header in native_headers],
        "native_requests_and_responses_present": {1, 2}.issubset({header["type"] for header in native_headers}),
        "native_buildinfo_annotation_present": any(node.get("id") == "buildinfo" for node in root.iter()),
        "credential_patterns_absent": not any(re.search(pattern, text) for pattern in credential_patterns),
    }
    if args.baseline:
        baseline = json.loads(args.baseline.read_text())
        records = [record for record in baseline.get("records", []) if str(record.get("trace_id")) == str(args.session)]
        checks["baseline_session_found"] = len(records) == 1
        if records:
            record = records[0]
            checks["raw_payload_absent"] = not record.get("raw_payload") or record["raw_payload"] not in text
            message_values = [value for value in record.get("message", {}).values() if isinstance(value, str) and len(value) >= 12]
            checks["message_field_values_absent_from_visible_text"] = all(value not in visible_text for value in message_values)
    receipt.update(ok=all(checks.values()), output=str(output), bytes=len(data), header_ids=header_ids, native_headers=native_headers, checks=checks)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    output.with_suffix(".renderer.log").unlink(missing_ok=True)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
