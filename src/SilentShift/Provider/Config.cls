/// Deployment configuration only. Keys never enter returned data or messages.
Class SilentShift.Provider.Config Extends %RegisteredObject
{
ClassMethod Resolve() As %String [ Language = python ]
{
    import iris, os, sys, json
    root=iris.cls('SilentShift.IPM').AssetPath('python')
    if root not in sys.path:
        sys.path.insert(0,root)
    from silentshift.provider_config import resolve_provider
    return json.dumps(resolve_provider(os.environ).public(),sort_keys=True,separators=(',',':'))
}

ClassMethod Read() As %DynamicObject
{
    Return ##class(%DynamicObject).%FromJSON(..Resolve())
}

ClassMethod ForwardHTTP(raw As %String, config As %String, timeout As %Integer) As %String [ Language = python ]
{
    import iris, os, sys, json
    root=iris.cls('SilentShift.IPM').AssetPath('python')
    if root not in sys.path:
        sys.path.insert(0,root)
    from silentshift.provider_transport import forward
    # The lease carries UTF-8 wire bytes in an ObjectScript binary string.
    result=forward(raw.encode('latin-1'),json.loads(config),os.environ,int(timeout))
    return json.dumps(result,separators=(',',':'))
}
}
