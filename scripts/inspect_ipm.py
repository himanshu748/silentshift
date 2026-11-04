#!/usr/bin/env python3
"""Inspect the real IPM-generated archive without extracting or executing it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import xml.etree.ElementTree as ET

from package_ipm import ROOT, RUNTIME_FILES, package_files


def inspect(archive: Path, source: Path = ROOT) -> dict:
    release_files = package_files(source)
    expected_classes = {'.'.join(PurePosixPath(path).relative_to('src').with_suffix('').parts)
        for path in release_files if path.endswith('.cls')}
    if not archive.is_file() or archive.is_symlink() or archive.stat().st_size > 16777216:
        raise ValueError('Expected a bounded regular IPM archive')
    files = {}
    total_bytes = 0
    with tarfile.open(archive, 'r:gz') as package:
        for index, member in enumerate(package):
            if index >= 1000:
                raise ValueError('Too many archive entries')
            name = member.name
            while name.startswith('./'):
                name = name[2:]
            path = PurePosixPath(name)
            if path.is_absolute() or '\\' in name or '..' in path.parts:
                raise ValueError('Unsafe archive path')
            # IPM 0.10.10 exports separators such as fixtures/v1//manifest.json.
            # Compare canonical POSIX names, including for duplicate detection.
            name = str(path)
            if name == '.':
                if member.isdir():
                    continue
                raise ValueError('Unsafe archive path')
            if member.isdir():
                continue
            if not member.isfile() or member.size > 1048576:
                raise ValueError('Archive links/devices/oversized files are forbidden')
            total_bytes += member.size
            if total_bytes > 8388608:
                raise ValueError('Archive expanded size exceeds application bounds')
            if name in files:
                raise ValueError('Duplicate archive member')
            stream = package.extractfile(member)
            assert stream is not None
            files[name] = stream.read(member.size + 1)
    manifests = [name for name in files if PurePosixPath(name).name == 'module.xml']
    if len(manifests) != 1:
        raise ValueError('Exactly one package manifest is required')
    prefix = str(PurePosixPath(manifests[0]).parent)
    prefix = '' if prefix == '.' else prefix + '/'
    if any(not name.startswith(prefix) for name in files):
        raise ValueError('Archive contains files outside its module root')
    relative_files = {name[len(prefix):]: value for name, value in files.items()}
    # IPM may reserialize metadata and export UDL under src/cls. Validate the
    # actual declared resources and class identities rather than byte-comparing
    # native exports whose formatting can legitimately change.
    if b'<!' in relative_files['module.xml']:
        raise ValueError('Exported manifest must not contain DTD/entity declarations')
    manifest = ET.fromstring(relative_files['module.xml'])
    for node in manifest.iter():
        node.tag = node.tag.rsplit('}', 1)[-1]
    module = manifest.find('./Document/Module')
    if module is None and manifest.tag == 'Module':
        module = manifest
    if module is None:
        raise ValueError('Invalid exported module metadata')
    expected = ET.parse(source / 'module.xml').find('./Document/Module')
    if any(node.tag not in {item.tag for item in expected} for node in module):
        raise ValueError('Unexpected deployment element in exported metadata')
    for tag in {node.tag for node in expected}:
        expected_count, actual_count = len(expected.findall(tag)), len(module.findall(tag))
        # The official external XSLT drops the default <Packaging>module</...>.
        if tag == 'Packaging' and actual_count == 0:
            continue
        if expected_count != actual_count:
            raise ValueError('Exported metadata field/resource multiplicity changed')
    for key in ('Name', 'Version', 'SourcesRoot'):
        if module.findtext(key, '').lower() != expected.findtext(key, '').lower():
            raise ValueError('Exported package identity/source root changed')
    requirements = module.find('SystemRequirements')
    if requirements is None or any(requirements.get(key) != value for key, value
        in expected.find('SystemRequirements').attrib.items()):
        raise ValueError('Exported runtime requirements changed')
    for kind in ('Invoke', 'FileCopy', 'Resource'):
        actual = [(node.attrib, [arg.text for arg in node]) for node in module.findall(kind)]
        declared = [(node.attrib, [arg.text for arg in node]) for node in expected.findall(kind)]
        if actual != declared:
            raise ValueError(f'Exported {kind} configuration differs from source')
    observed_classes = set()
    for name, data in relative_files.items():
        if name == 'module.xml':
            continue
        if name in RUNTIME_FILES:
            if data != (source / name).read_bytes():
                raise ValueError(f'Runtime file differs from release source: {name}')
            continue
        if not name.endswith('.cls') or not name.startswith('src/'):
            raise ValueError(f'Unexpected exported file: {name}')
        match = re.search(rb'^Class\s+([\w.]+)\s', data, re.MULTILINE)
        classname = match.group(1).decode('ascii') if match else ''
        if classname not in expected_classes or classname in observed_classes:
            raise ValueError(f'Unexpected or duplicate exported class: {name}')
        observed_classes.add(classname)
    if observed_classes != expected_classes or not set(RUNTIME_FILES).issubset(relative_files):
        raise ValueError('Exported archive is missing application classes/assets')
    return {'package': 'silentshift', 'version': '0.2.0',
        'artifact_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'compressed_bytes': archive.stat().st_size, 'expanded_bytes': total_bytes,
        'file_count': len(files), 'class_count': len(observed_classes),
        'archive_boundary_verified': True, 'native_install_verified': False,
        'registry_published': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        receipt = inspect(args.archive)
    except (OSError, ValueError, ET.ParseError, tarfile.TarError) as error:
        parser.exit(1, f'IPM archive inspection failed: {error}\n')
    print(json.dumps(receipt))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
