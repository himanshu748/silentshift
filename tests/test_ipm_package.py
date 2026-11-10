"""Release boundaries and the actual Embedded Python asset resolver bodies."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import re
import shutil
import sys
import tarfile
import textwrap
import types
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_ipm', ROOT / 'scripts/package_ipm.py')
packaging = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(packaging)
sys.modules.setdefault('package_ipm', packaging)
inspect_spec = importlib.util.spec_from_file_location('inspect_ipm', ROOT / 'scripts/inspect_ipm.py')
inspector = importlib.util.module_from_spec(inspect_spec)
assert inspect_spec and inspect_spec.loader
inspect_spec.loader.exec_module(inspector)


@pytest.fixture
def source(tmp_path):
    root = tmp_path / 'source'
    for relative in packaging.package_files(ROOT):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return root


def embedded_method(name):
    """Execute the checked-in method body, without pretending to compile IRIS."""
    source = (ROOT / 'src/SilentShift/IPM.cls').read_text()
    match = re.search(r'ClassMethod ' + name + r'\([^\n]*Language = python[^\n]*\n\{\n(.*?)\n\}',
        source, re.DOTALL)
    assert match, name
    params = {'Build154': 'version', 'ValidateAssets': 'root'}[name]
    namespace = {}
    exec('def method(' + params + '):\n' + textwrap.indent(textwrap.dedent(match.group(1)), '    '), namespace)
    return namespace['method']


def fake_iris(monkeypatch, manager, asset_root):
    class File:
        @staticmethod
        def ManagerDirectory():
            return str(manager) + '/'

    class IPM:
        @staticmethod
        def AssetRoot():
            return str(asset_root)

    monkeypatch.setitem(sys.modules, 'iris', types.SimpleNamespace(
        cls=lambda name: {'%Library.File': File, 'SilentShift.IPM': IPM}[name]))


def installed_assets(source, tmp_path):
    manager = tmp_path / 'mgr'
    target = manager / 'silentshift/SILENTSHIFT'
    for relative in packaging.RUNTIME_FILES:
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, dest)
    return manager, target


def test_stage_excludes_private_and_generated_material(source, tmp_path):
    for relative in ('.env', 'private/key.pem', 'python/silentshift/__pycache__/engine.pyc',
            'fixtures/credentials.json', 'evidence/native/case.json', 'iris-image.tar',
            'web/dist/index.html', 'src/other/readme.txt'):
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('must not enter release')
    destination = tmp_path / 'stage'
    result = packaging.stage(source, destination)
    expected = set(packaging.package_files(source))
    actual = {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()}
    assert actual == expected | {'package-inventory.json'}
    assert result['native_install_verified'] is False
    assert result['version'] == packaging.module_version(source) == '0.3.0'
    assert result['registry_published'] is False
    for item in result['files']:
        assert item['sha256'] == hashlib.sha256((destination / item['path']).read_bytes()).hexdigest()


def test_stage_cannot_overwrite_existing_release(source, tmp_path):
    destination = tmp_path / 'stage'
    packaging.stage(source, destination)
    sentinel = destination / 'operator-file'
    sentinel.write_text('preserve')
    with pytest.raises(ValueError, match='already exists'):
        packaging.stage(source, destination)
    assert sentinel.read_text() == 'preserve'


def test_stage_cannot_create_output_inside_application_sources(source):
    output = source / 'src/release/stage'
    with pytest.raises(ValueError, match='inside application sources'):
        packaging.stage(source, output)
    assert not output.parent.exists()


@pytest.mark.parametrize('relative', ['python/silentshift/engine.py', 'src/SilentShift/IPM.cls'])
def test_stage_rejects_symlinked_sources(source, tmp_path, relative):
    target = source / relative
    external = tmp_path / 'private'
    external.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(external)
    with pytest.raises(ValueError, match='Symlink'):
        packaging.stage(source, tmp_path / 'stage')


def test_manifest_cannot_copy_secret_or_activate_setup(source, tmp_path):
    tree = ET.parse(source / 'module.xml')
    module = tree.find('./Document/Module')
    module.find('FileCopy').set('Name', '.env')
    tree.write(source / 'module.xml')
    with pytest.raises(ValueError, match='allowlist'):
        packaging.stage(source, tmp_path / 'stage')
    shutil.copyfile(ROOT / 'module.xml', source / 'module.xml')
    tree = ET.parse(source / 'module.xml')
    tree.find('./Document/Module/Invoke').set('Method', 'Install')
    tree.write(source / 'module.xml')
    with pytest.raises(ValueError, match='asset-only'):
        packaging.stage(source, tmp_path / 'stage')


def test_frozen_checksum_is_a_release_boundary(source, tmp_path):
    fixture = source / 'fixtures/v1/scenarios.json'
    fixture.write_bytes(fixture.read_bytes() + b' ')
    with pytest.raises(ValueError, match='checksum'):
        packaging.stage(source, tmp_path / 'stage')


def test_resolver_never_reenters_embedded_python():
    # Bridge's Embedded Python calls this via iris.cls; a second Python method
    # would recreate the native reentry hazard. Runtime path cases need IRIS UAT.
    source = (ROOT / 'src/SilentShift/IPM.cls').read_text()
    for method in ('AssetRoot', 'AssetPath'):
        declaration = re.search(r'ClassMethod ' + method + r'[^\n]*', source).group()
        assert 'Language = python' not in declaration


@pytest.mark.parametrize(('version', 'expected'), [
    ('2026.3.0AI.154.0', True),
    ('IRIS for UNIX 2026.3.0AI (Build 154U) Thu Sep 24 2026', True),
    ('IRIS 2026.3.0AI (Build 154)', True),
    ('IRIS 2026.3.0AI (Build 1154U)', False),
    ('2026.3.0AI.154.01', False),
    ('IRIS 2026.3.0AI (Build 1540)', False),
    ('IRIS 2026.3.0AI (Build 109U)', False),
    ('IRIS 2026.2.0AI (Build 154U)', False),
])
def test_runtime_guard_accepts_only_verified_build(version, expected):
    assert embedded_method('Build154')(version) is expected


def test_activation_validates_actual_installed_files(source, monkeypatch, tmp_path):
    manager, target = installed_assets(source, tmp_path)
    fake_iris(monkeypatch, manager, target)
    validate = embedded_method('ValidateAssets')
    assert validate(str(target)) == ''
    assert validate(str(source)) != ''
    fixture = target / 'fixtures/v1/scenarios.json'
    fixture.write_bytes(fixture.read_bytes() + b' ')
    assert 'checksum' in validate(str(target))


def test_activation_rejects_symlink_and_nonfinite_data(source, monkeypatch, tmp_path):
    manager, target = installed_assets(source, tmp_path)
    fake_iris(monkeypatch, manager, target)
    validate = embedded_method('ValidateAssets')
    runbook = target / 'fixtures/runbooks.json'
    runbook.write_text('{"invalid": NaN}')
    assert validate(str(target)) != ''
    external = tmp_path / 'runbook.json'
    external.write_text('{}')
    runbook.unlink()
    runbook.symlink_to(external)
    assert 'symbolic' in validate(str(target))


def test_activation_handles_symlinked_manager_without_loop(source, monkeypatch, tmp_path):
    manager, target = installed_assets(source, tmp_path)
    alias = tmp_path / 'manager-alias'
    alias.symlink_to(manager, target_is_directory=True)
    fake_iris(monkeypatch, alias, target)
    assert embedded_method('ValidateAssets')(str(alias / 'silentshift/SILENTSHIFT')) == ''


def archive_fixture(source, destination, extra=None, mutate=None):
    """Synthetic archive for boundary tests; never an IPM installation proof."""
    contents = {'module.xml': (source / 'module.xml').read_bytes()}
    contents.update({name: (source / name).read_bytes() for name in packaging.RUNTIME_FILES})
    for path in source.glob('src/SilentShift/**/*.cls'):
        contents['src/cls/' + path.relative_to(source / 'src').as_posix()] = path.read_bytes()
    if extra:
        contents.update(extra)
    if mutate:
        mutate(contents)
    with tarfile.open(destination, 'w:gz') as archive:
        for name, content in contents.items():
            member = tarfile.TarInfo('./' + name)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    return destination


def test_archive_boundary_accepts_native_export_layout_fixture(source, tmp_path):
    archive = archive_fixture(source, tmp_path / 'synthetic-boundary.tgz')
    result = inspector.inspect(archive, source)
    assert result['version'] == packaging.module_version(source) == '0.3.0'
    assert result['class_count'] == len(list(source.glob('src/SilentShift/**/*.cls')))
    assert result['archive_boundary_verified'] is True
    assert result['native_install_verified'] is False


def test_archive_accepts_real_ipm_doubled_separators(source, tmp_path):
    def double_separators(files):
        renamed = {name.replace('/', '//'): data for name, data in files.items()}
        files.clear()
        files.update(renamed)
    archive = archive_fixture(source, tmp_path / 'ipm-separators.tgz', mutate=double_separators)
    assert inspector.inspect(archive, source)['archive_boundary_verified'] is True


def test_archive_rejects_duplicate_canonical_paths(source, tmp_path):
    archive = archive_fixture(source, tmp_path / 'duplicate.tgz', extra={
        'fixtures//v1/scenarios.json': (source / 'fixtures/v1/scenarios.json').read_bytes()})
    with pytest.raises(ValueError, match='Duplicate archive member'):
        inspector.inspect(archive, source)


@pytest.mark.parametrize('name', ['.env', 'src/cls/SilentShift/Test/Diagnostic.cls',
    '../outside', '/absolute', 'web/dist/index.html'])
def test_archive_rejects_extra_private_or_unsafe_files(source, tmp_path, name):
    archive = archive_fixture(source, tmp_path / 'invalid.tgz',
        extra={name: b'Class SilentShift.Test.Diagnostic Extends %RegisteredObject\n{}'})
    with pytest.raises(ValueError):
        inspector.inspect(archive, source)


def test_archive_rejects_links_and_altered_runtime_data(source, tmp_path):
    archive = archive_fixture(source, tmp_path / 'invalid.tgz',
        mutate=lambda files: files.update({'fixtures/v1/scenarios.json': b'{}'}))
    with pytest.raises(ValueError, match='differs from release source'):
        inspector.inspect(archive, source)
    with tarfile.open(archive, 'w:gz') as package:
        member = tarfile.TarInfo('module.xml')
        member.type = tarfile.SYMTYPE
        member.linkname = '/private'
        package.addfile(member)
    with pytest.raises(ValueError, match='links/devices'):
        inspector.inspect(archive, source)


def test_archive_rejects_added_deployment_actions(source, tmp_path):
    def add_security_resource(files):
        files['module.xml'] = files['module.xml'].replace(b'</Module>',
            b'<WebApplication Url="/unreviewed"/>\n</Module>')
    archive = archive_fixture(source, tmp_path / 'invalid.tgz', mutate=add_security_resource)
    with pytest.raises(ValueError, match='Unexpected deployment element'):
        inspector.inspect(archive, source)
