#!/usr/bin/env python3
"""Compile/run isolated native reference-limit checks; no model calls or deletion.

Requires the production evidence-budget guard to be compiled and the production
running. The native test checks the compiled routine before creating any case.
Only tests/iris/RuntimeChecks.cls is compiled. Synthetic cases/references remain.
Credentials are unnecessary: the existing local IRIS terminal context is used.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NATIVE_SCRIPT = '''\
set sc=$SYSTEM.OBJ.Load("/opt/silentshift/tests/iris/RuntimeChecks.cls","ck")
write "SILENTSHIFT_BOUNDARY_COMPILE=",$SYSTEM.Status.IsOK(sc),!
if $SYSTEM.Status.IsOK(sc) {set sc=##class(SilentShift.Test.RuntimeChecks).RunBoundaries(.report) write "SILENTSHIFT_BOUNDARY_JSON=",report,! write "SILENTSHIFT_BOUNDARY_STATUS=",$SYSTEM.Status.IsOK(sc),!}
halt
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", default=os.environ.get("DOCKER_CONTEXT"))
    project = os.environ.get("COMPOSE_PROJECT_NAME", ROOT.name.lower())
    parser.add_argument("--container", default=f"{project}-iris-1")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/native/reference-boundaries.json")
    args = parser.parse_args()
    try:
        docker = ["docker"] + (["--context", args.context] if args.context else [])
        result = subprocess.run(
            docker + ["exec", "-i", args.container,
             "iris", "session", "IRIS", "-U", "SILENTSHIFT"],
            input=NATIVE_SCRIPT, text=True, capture_output=True, timeout=45,
            check=False,
        )
        lines = result.stdout.splitlines()
        if result.returncode or "SILENTSHIFT_BOUNDARY_COMPILE=1" not in lines:
            print("FAILED: native test compilation; production classes were not compiled.", file=sys.stderr)
            return 2
        reports = [line.removeprefix("SILENTSHIFT_BOUNDARY_JSON=")
                   for line in lines if line.startswith("SILENTSHIFT_BOUNDARY_JSON=")]
        if len(reports) != 1:
            print("FAILED: native boundary driver returned no unique report.", file=sys.stderr)
            return 2
        report = json.loads(reports[0])
        passed = ("SILENTSHIFT_BOUNDARY_STATUS=1" in lines
                  and report.get("passed") is True
                  and len(report.get("cases", [])) == 2
                  and all(case.get("passed") is True for case in report["cases"]))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        for case in report.get("cases", []):
            print(f"{case['authority']}: passed={case['passed']} case={case.get('case_id', 'unavailable')} "
                  f"route={case.get('routing', 'unavailable')} deliveries={case.get('delivery_count', 'unavailable')}")
        print(f"Evidence saved: {args.output}")
        return 0 if passed else 1
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
        # Avoid dumping terminal/native diagnostics or environment values.
        print("FAILED: native boundary command did not return a valid bounded report.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
