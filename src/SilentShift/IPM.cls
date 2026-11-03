Include (Ensemble, %occStatus)

/// Package activation installs assets only. Runtime setup remains explicit.
Class SilentShift.IPM Extends %RegisteredObject
{
/// Namespace-local configuration; the fallback preserves the Docker mount.
ClassMethod AssetRoot() As %String
{
    Return $Get(^SilentShift.Config("AssetRoot"), "/opt/silentshift")
}

/// Callers supply application constants, never partner-controlled filenames.
ClassMethod AssetPath(relative As %String) As %String
{
    If relative = "" $$$ThrowStatus($$$ERROR($$$GeneralError, "Invalid application asset path"))
    Set allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./-"
    For index = 1:1:$Length(relative) {
        If allowed'[$Extract(relative, index) $$$ThrowStatus($$$ERROR($$$GeneralError, "Invalid application asset path"))
    }
    For index = 1:1:$Length(relative, "/") {
        Set segment = $Piece(relative, "/", index)
        If (segment = "") || (segment = ".") || (segment = "..") $$$ThrowStatus($$$ERROR($$$GeneralError, "Invalid application asset path"))
    }
    Return ##class(%Library.File).NormalizeDirectory(..AssetRoot())_relative
}

/// Compile-time guard runs before FileCopy's Activate phase. Classes can have
/// been imported by IPM at this point; no runtime assets or config are changed.
ClassMethod CheckTarget() As %Status
{
    If $NAMESPACE '= "SILENTSHIFT" Return $$$ERROR($$$GeneralError, "SilentShift IPM requires the SILENTSHIFT namespace")
    If '..Build154($ZVERSION) Return $$$ERROR($$$GeneralError, "SilentShift is tested on IRIS AI Hub 2026.3.0AI build 154 only")
    Return ..RequireStopped()
}

ClassMethod RequireStopped() As %Status
{
    Set sc = ##class(Ens.Director).GetProductionStatus(.name, .state)
    $$$ThrowOnError(sc)
    If state '= $$$eProductionStateStopped Return $$$ERROR($$$GeneralError, "Stop the production before package installation or removal")
    Return $$$OK
}

ClassMethod Build154(version As %String) As %Boolean [ Language = python, Private ]
{
    import re
    return bool(re.search(r'(?<![\w.])2026\.3\.0AI\.154\.0(?![\w.])', version, re.I)
        or (re.search(r'(?<![\w.])2026\.3\.0AI(?![\w.])', version, re.I)
            and re.search(r'\bBuild\s+154(?:[A-Za-z])?\b', version, re.I)))
}

/// The only persistent change made by package activation is this asset root.
ClassMethod ConfigureAssets(root As %String) As %Status
{
    Try {
        Set sc = ..CheckTarget()
        $$$ThrowOnError(sc)
        Set error = ..ValidateAssets(root)
        If error '= "" Return $$$ERROR($$$GeneralError, error)
        Set ^SilentShift.Config("AssetRoot") = ##class(%Library.File).NormalizeDirectory(root)
        Return $$$OK
    } Catch error {
        Return $$$ERROR($$$GeneralError, "SilentShift asset activation failed; inspect local installation diagnostics")
    }
}

/// Refuse destructive removal of a populated namespace. Empty installs can be
/// removed without deleting database directories, security or unrelated config.
ClassMethod PrepareUninstall(root As %String) As %Status
{
    Try {
        If $NAMESPACE '= "SILENTSHIFT" Return $$$ERROR($$$GeneralError, "SilentShift uninstall requires SILENTSHIFT")
        Set sc = ..RequireStopped()
        $$$ThrowOnError(sc)
        For table = "SilentShift_Data.CaseRecord", "SilentShift_Data.Reference", "SilentShift_Data.AuditEvent", "SilentShift_Data.Delivery", "SilentShift_Data.ReviewAction", "SilentShift_Data.Evaluation", "SilentShift_Data.Runbook", "SilentShift_Data.Precedent", "SilentShift_Workflow.ReviewTask", "EnsLib_Workflow.Worklist", "Ens.MessageHeader" {
            Set query = ##class(%SQL.Statement).%New()
            Set sc = query.%Prepare("SELECT TOP 1 1 FROM "_table)
            $$$ThrowOnError(sc)
            Set result = query.%Execute()
            If result.%SQLCODE < 0 Return $$$ERROR($$$GeneralError, "Cannot establish an empty SilentShift database; uninstall refused")
            If result.%Next() Return $$$ERROR($$$GeneralError, "SilentShift contains persisted data; retain the package and use an operator-managed migration or rollback")
        }
        Set expected = ##class(%Library.File).NormalizeDirectory(##class(%Library.File).ManagerDirectory())_"silentshift/SILENTSHIFT/"
        If ##class(%Library.File).NormalizeDirectory(root) '= expected Return $$$ERROR($$$GeneralError, "Unexpected SilentShift uninstall asset target")
        If $Get(^SilentShift.Config("AssetRoot")) = expected Kill ^SilentShift.Config("AssetRoot")
        Return $$$OK
    } Catch error {
        Return $$$ERROR($$$GeneralError, "Cannot establish a safe empty SilentShift installation; uninstall refused")
    }
}

/// Validate independently of the application package, which is not importable
/// until ConfigureAssets has completed on an installation without /opt assets.
ClassMethod ValidateAssets(root As %String) As %String [ Language = python, Private ]
{
    import hashlib, iris, json
    from pathlib import Path
    try:
        manager = Path(iris.cls('%Library.File').ManagerDirectory()).absolute()
        expected = manager / 'silentshift' / 'SILENTSHIFT'
        target = Path(root)
        if (not target.is_absolute() or target != expected
                or target.resolve(strict=True) != expected.resolve(strict=True)):
            return 'SilentShift assets must use the namespace-specific manager directory'
        current = target
        while current != manager:
            if current.is_symlink():
                return 'SilentShift asset directories must not be symbolic links'
            current = current.parent
        required = ('python/silentshift/__init__.py', 'python/silentshift/engine.py',
            'python/silentshift/evaluation.py', 'python/silentshift/embeddings.py',
            'fixtures/v1/scenarios.json', 'fixtures/v1/manifest.json',
            'fixtures/v1/README.md', 'fixtures/runbooks.json', 'LICENSE')
        for relative in required:
            asset = target / relative
            if not asset.is_file() or asset.stat().st_size > 1048576:
                return 'SilentShift required asset is missing or exceeds its size bound'
            for component in (asset, *asset.parents):
                if component == target:
                    break
                if component.is_symlink():
                    return 'SilentShift assets must not contain symbolic links'
        def reject_constant(value):
            raise ValueError('Non-finite JSON value')
        manifest = json.loads((target / 'fixtures/v1/manifest.json').read_text(encoding='utf-8'),
            parse_constant=reject_constant)
        scenarios = (target / 'fixtures/v1/scenarios.json').read_bytes()
        dataset = json.loads(scenarios, parse_constant=reject_constant)
        if (manifest.get('file') != 'scenarios.json'
                or manifest.get('dataset_version') != dataset.get('dataset_version')
                or manifest.get('scenario_count') != len(dataset.get('scenarios', []))
                or manifest.get('sha256') != hashlib.sha256(scenarios).hexdigest()):
            return 'SilentShift frozen dataset failed its checksum or metadata validation'
        json.loads((target / 'fixtures/runbooks.json').read_text(encoding='utf-8'),
            parse_constant=reject_constant)
        return ''
    except (OSError, ValueError, TypeError, AttributeError):
        return 'SilentShift required assets could not be validated'
}
}
