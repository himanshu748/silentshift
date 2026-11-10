/// Deployment configuration only. Keys never enter returned data or messages.
Class SilentShift.Provider.Config Extends %RegisteredObject
{
/// One default from the same configuration module used by the provider route.
ClassMethod DefaultModel() As %String [ Language = python ]
{
    import iris
    iris.cls('SilentShift.Bridge').Import()
    from silentshift.provider_config import DEFAULT_MODEL
    return DEFAULT_MODEL
}

ClassMethod Resolve() As %String [ Language = python ]
{
    import iris, os, sys, json
    iris.cls('SilentShift.Bridge').Import()
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
    iris.cls('SilentShift.Bridge').Import()
    from silentshift.provider_transport import forward
    # The lease carries UTF-8 wire bytes in an ObjectScript binary string.
    result=forward(raw.encode('latin-1'),json.loads(config),os.environ,int(timeout))
    return json.dumps(result,separators=(',',':'))
}
}
