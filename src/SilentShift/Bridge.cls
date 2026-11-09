/// Pure Python business arithmetic executes inside IRIS, never an external API.
Class SilentShift.Bridge Extends %RegisteredObject
{
ClassMethod Assess(messageJSON As %String, referencesJSON As %String, clock As %String) As %String [ Language = python ]
{
    import iris, sys
    asset_python = iris.cls('SilentShift.IPM').AssetPath('python')
    if asset_python not in sys.path:
        sys.path.insert(0, asset_python)
    from silentshift.engine import assess_json
    return assess_json(messageJSON, referencesJSON, clock)
}
ClassMethod Policy(assessmentJSON As %String, recommendationJSON As %String, evidenceContextJSON As %String = "") As %String [ Language = python ]
{
    import iris, sys
    asset_python = iris.cls('SilentShift.IPM').AssetPath('python')
    if asset_python not in sys.path:
        sys.path.insert(0, asset_python)
    from silentshift.engine import policy_json
    return policy_json(assessmentJSON, recommendationJSON, evidence_context_json=evidenceContextJSON)
}
ClassMethod Canonical(value As %String) As %String [ Language = python ]
{
    import iris, json, sys
    asset_python = iris.cls('SilentShift.IPM').AssetPath('python')
    if asset_python not in sys.path:
        sys.path.insert(0, asset_python)
    from silentshift.engine import strict_loads
    return json.dumps(strict_loads(value, max_bytes=1048576), sort_keys=True, separators=(',', ':'), allow_nan=False)
}
ClassMethod Hash(value As %String) As %String [ Language = python ]
{
    import hashlib
    return hashlib.sha256(value.encode('utf-8')).hexdigest()
}
ClassMethod PairHash(left As %String, right As %String) As %String [ Language = python ]
{
    import hashlib, json
    return hashlib.sha256(json.dumps([left, right], separators=(',', ':')).encode('utf-8')).hexdigest()
}
ClassMethod Now() As %String [ Language = python ]
{
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
}
ClassMethod FixtureJSON() As %String [ Language = python ]
{
    import iris
    from pathlib import Path
    return Path(iris.cls('SilentShift.IPM').AssetPath('fixtures/v1/scenarios.json')).read_text(encoding='utf-8')
}
ClassMethod IsRequiredBuild(version As %String) As %Boolean [ Language = python ]
{
    import iris, sys
    asset_python = iris.cls('SilentShift.IPM').AssetPath('python')
    if asset_python not in sys.path:
        sys.path.insert(0, asset_python)
    from silentshift.evaluation import _build154
    return _build154(version)
}
/// Local-only embeddings execute outside native agent callbacks. Corpus text
/// and structured queries are bounded; generated vectors are never hand-built.
ClassMethod Embed(textsJSON As %String, base As %String = "", model As %String = "") As %String [ Language = python ]
{
    import iris, json, os, sys
    asset_python = iris.cls('SilentShift.IPM').AssetPath('python')
    if asset_python not in sys.path:
        sys.path.insert(0, asset_python)
    from silentshift.embeddings import encode
    base = base or os.environ.get('SILENTSHIFT_EMBED_BASE_URL', '')
    model = model or os.environ.get('SILENTSHIFT_EMBED_MODEL', 'all-minilm:22m')
    return json.dumps(encode(json.loads(textsJSON), base, model), allow_nan=False, separators=(',', ':'))
}
ClassMethod RunbookJSON() As %String [ Language = python ]
{
    import iris
    from pathlib import Path
    return Path(iris.cls('SilentShift.IPM').AssetPath('fixtures/runbooks.json')).read_text(encoding='utf-8')
}
}
