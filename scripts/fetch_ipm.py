#!/usr/bin/env python3
"""Fetch the pinned official IPM installer without importing it into IRIS."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path

VERSION = '0.10.10'
URL = 'https://github.com/intersystems/ipm/releases/download/v0.10.10/zpm-0.10.10.xml'
SHA256 = 'daa2adabd66b488f57187d29712e54b0c25bbe000794fbf2a35a882c458b788a'
SIZE = 1593780


def fetch(destination: Path) -> dict:
    destination = destination.absolute()
    if destination.is_symlink():
        raise ValueError('Installer destination must not be a symlink')
    if destination.exists():
        data = destination.read_bytes()
    else:
        request = urllib.request.Request(URL, headers={'User-Agent': 'SilentShift-IPM-preflight'})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(SIZE + 1)
        if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError('Official installer size/SHA256 mismatch; not saved')
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
            temporary.write(data)
            temporary_path = Path(temporary.name)
        try:
            # Same-directory hard link publishes the complete file exclusively.
            os.link(temporary_path, destination)
        finally:
            temporary_path.unlink(missing_ok=True)
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('Existing destination does not match the pinned installer')
    return {'version': VERSION, 'source': URL, 'sha256': SHA256,
        'bytes': SIZE, 'path': str(destination), 'installed': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = fetch(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'IPM fetch failed: {error}\n')
    print(json.dumps(receipt))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
