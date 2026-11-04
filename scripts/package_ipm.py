#!/usr/bin/env python3
"""Prepare an allowlisted source tree for the real IPM load/package commands.

This does not emulate IPM, publish a registry package, or invoke IRIS/model calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = (
    'python/silentshift/__init__.py', 'python/silentshift/engine.py',
    'python/silentshift/evaluation.py', 'python/silentshift/embeddings.py',
    'fixtures/v1/scenarios.json', 'fixtures/v1/manifest.json',
    'fixtures/v1/README.md', 'fixtures/provider-replay.json', 'fixtures/runbooks.json', 'LICENSE',
)
TARGET_PREFIX = '${mgrdir}silentshift/${namespace}/'


def regular_file(root: Path, relative: str) -> Path:
    """Reject traversal, external files and symlinked ancestors before copying."""
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith('/') or '\\' in relative or any(
        part in ('', '.', '..') for part in relative.split('/')
    ):
        raise ValueError('Package path must be a relative application file')
    target = root.joinpath(*parts)
    for candidate in (target, *target.parents):
        if candidate == root:
            break
        if candidate.is_symlink():
            raise ValueError(f'Symlink rejected: {relative}')
    if not target.is_file() or target.stat().st_size > 1048576:
        raise ValueError(f'Missing or oversized package file: {relative}')
    return target


def package_files(root: Path) -> list[str]:
    """Validate the release boundary and return its exact declared source set."""
    raw = regular_file(root, 'module.xml').read_bytes()
    if b'<!' in raw:
        raise ValueError('DTD and XML entity declarations are not package metadata')
    module = ET.fromstring(raw).find('./Document/Module')
    if (module is None or module.findtext('Name') != 'silentshift'
            or module.findtext('Version') != '0.2.0'):
        raise ValueError('Expected the silentshift IPM module')
    requirements = module.find('SystemRequirements')
    if requirements is None or requirements.attrib != {
        'Version': '>=2026.3', 'Interoperability': 'enabled', 'IPMVersion': '>=0.10.10'
    }:
        raise ValueError('IRIS/interoperability/IPM requirements must remain explicit')
    classes = sorted(root.glob('src/SilentShift/**/*.cls'))
    expected_resources = [{'Name': '.'.join(path.relative_to(root / 'src').with_suffix('').parts) + '.CLS'}
        for path in classes]
    if module.findtext('SourcesRoot') != 'src' or [
        node.attrib for node in module.findall('Resource')
    ] != expected_resources:
        raise ValueError('Package must explicitly load only its declared source classes')
    copies = module.findall('FileCopy')
    if len(copies) != len(RUNTIME_FILES) or {node.get('Name') for node in copies} != set(RUNTIME_FILES):
        raise ValueError('Runtime assets must match the explicit release allowlist')
    for node in copies:
        name = node.get('Name', '')
        if node.attrib != {'Name': name, 'Target': TARGET_PREFIX + name}:
            raise ValueError('Each asset must copy one file into its package-owned target')
    invokes = module.findall('Invoke')
    expected_invokes = [
        {'Class': 'SilentShift.IPM', 'Method': 'CheckTarget', 'Phase': 'Compile',
         'When': 'After', 'CheckStatus': 'true'},
        {'Class': 'SilentShift.IPM', 'Method': 'ConfigureAssets', 'Phase': 'Activate',
         'When': 'After', 'CheckStatus': 'true'},
        {'Class': 'SilentShift.IPM', 'Method': 'PrepareUninstall', 'Phase': 'Clean',
         'When': 'Before', 'CheckStatus': 'true'},
    ]
    if ([node.attrib for node in invokes] != expected_invokes
            or list(invokes[0]) or [arg.text for arg in invokes[1]] != [TARGET_PREFIX]
            or [arg.text for arg in invokes[2]] != [TARGET_PREFIX]):
        raise ValueError('Activation must remain asset-only, with no runtime setup')
    # New deployment elements require an explicit packaging review.
    allowed_elements = {'Name', 'Version', 'Description', 'Keywords', 'Author',
        'Packaging', 'SystemRequirements', 'SourcesRoot', 'Resource', 'Invoke',
        'FileCopy', 'AfterInstallMessage'}
    if any(node.tag not in allowed_elements for node in module):
        raise ValueError('Unexpected installation resource in module.xml')
    if not classes or not (root / 'src/SilentShift/IPM.cls') in classes:
        raise ValueError('Native core and IPM helper are required')
    files = ['module.xml', *RUNTIME_FILES, 'docs/IPM.md']
    for source in classes:
        relative = source.relative_to(root).as_posix()
        body = regular_file(root, relative).read_text(encoding='utf-8')
        expected = '.'.join(source.relative_to(root / 'src').with_suffix('').parts)
        match = re.search(r'^Class\s+([\w.]+)\s', body, re.MULTILINE)
        if not match or match.group(1) != expected:
            raise ValueError(f'Class/path mismatch: {relative}')
        files.append(relative)
    for relative in files:
        regular_file(root, relative)
    scenarios = regular_file(root, 'fixtures/v1/scenarios.json').read_bytes()
    manifest = json.loads(regular_file(root, 'fixtures/v1/manifest.json').read_bytes())
    if hashlib.sha256(scenarios).hexdigest() != manifest['sha256']:
        raise ValueError('Frozen scenario checksum mismatch')
    return sorted(files)


def stage(root: Path, destination: Path) -> dict:
    """Create a new tree atomically; never replace an existing release tree."""
    root = root.resolve(strict=True)
    destination = destination.absolute()
    files = package_files(root)
    if destination.exists() or destination.is_symlink():
        raise ValueError('Destination already exists; choose a fresh release directory')
    resolved = destination.resolve()
    if resolved == root or any(resolved.is_relative_to(root / name)
        for name in ('src', 'python', 'fixtures', 'docs', 'web')):
        raise ValueError('Staging must not be placed inside application sources')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Resolve only after creating the parent, and reject aliases into source trees.
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    if destination == root or any(destination.is_relative_to(root / name)
        for name in ('src', 'python', 'fixtures', 'docs', 'web')):
        raise ValueError('Staging must not be placed inside application sources')
    with tempfile.TemporaryDirectory(prefix='.silentshift-stage-', dir=parent) as tmp:
        staging = Path(tmp) / 'module'
        staging.mkdir()
        inventory = []
        for relative in files:
            source = regular_file(root, relative)
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            inventory.append({'path': relative, 'bytes': target.stat().st_size,
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        result = {'package': 'silentshift', 'version': '0.2.0',
            'kind': 'allowlisted-source-stage', 'native_install_verified': False,
            'registry_published': False, 'files': inventory}
        (staging / 'package-inventory.json').write_text(
            json.dumps(result, indent=2) + '\n', encoding='utf-8')
        staging.rename(destination)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
        help='Fresh directory, preferably under ignored .local/ipm/')
    args = parser.parse_args()
    try:
        result = stage(ROOT, args.output)
    except (OSError, ValueError, ET.ParseError, KeyError) as error:
        parser.exit(1, f'Package staging failed: {error}\n')
    print(json.dumps({'package': result['package'], 'version': result['version'],
        'file_count': len(result['files']), 'output': str(args.output.absolute()),
        'native_install_verified': False, 'registry_published': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
