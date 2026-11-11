#!/usr/bin/env python3
"""Run JUnit against owned receipt logic using pinned public test dependencies.

The native PEX adapter is tested only with the operator-owned IRIS SDK; CI
checks the shared signing/storage logic without downloading restricted SDKs.
"""
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / '.local/java-core'
    output.mkdir(parents=True, exist_ok=True)
    dependencies = []
    for item in json.loads((ROOT / 'java/test-dependencies.json').read_text()):
        path = output / item['file']
        if not path.exists():
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'SilentShift-JUnit'})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(8_000_001)
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('Public Java test dependency checksum mismatch')
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Cached Java test dependency checksum mismatch')
        dependencies.append(path)
    classes = output / 'classes'
    classes.mkdir(exist_ok=True)
    classpath = os.pathsep.join(map(str, dependencies))
    subprocess.run(['javac', '--release', '11', '-cp', classpath, '-d', str(classes),
        str(ROOT / 'java/src/main/java/SilentShift/PEX/ReceiptStore.java'),
        str(ROOT / 'java/src/test/java/SilentShift/PEX/ReceiptStoreTest.java')], check=True)
    subprocess.run(['java', '-jar', str(dependencies[0]), 'execute', '--class-path',
        os.pathsep.join([str(classes), *map(str, dependencies[1:])]),
        '--scan-class-path', '--fail-if-no-tests', '--disable-ansi-colors'], check=True)


if __name__ == '__main__':
    main()
