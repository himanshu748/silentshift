/// Pure Python business arithmetic executes inside IRIS, never an external API.
Class SilentShift.Bridge Extends %RegisteredObject
{
ClassMethod Assess(messageJSON As %String, referencesJSON As %String, clock As %String) As %String [ Language = python ]
{
    import sys
    if '/opt/silentshift/python' not in sys.path:
        sys.path.insert(0, '/opt/silentshift/python')
    from silentshift.engine import assess_json
    return assess_json(messageJSON, referencesJSON, clock)
}
ClassMethod Policy(assessmentJSON As %String, recommendationJSON As %String) As %String [ Language = python ]
{
    import sys
    if '/opt/silentshift/python' not in sys.path:
        sys.path.insert(0, '/opt/silentshift/python')
    from silentshift.engine import policy_json
    return policy_json(assessmentJSON, recommendationJSON)
}
ClassMethod Canonical(value As %String) As %String [ Language = python ]
{
    import json, sys
    if '/opt/silentshift/python' not in sys.path:
        sys.path.insert(0, '/opt/silentshift/python')
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
    from pathlib import Path
    return Path('/opt/silentshift/fixtures/v1/scenarios.json').read_text(encoding='utf-8')
}
ClassMethod IsRequiredBuild(version As %String) As %Boolean [ Language = python ]
{
    import sys
    if '/opt/silentshift/python' not in sys.path:
        sys.path.insert(0, '/opt/silentshift/python')
    from silentshift.evaluation import _build154
    return _build154(version)
}
}
