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

/// Settings are administrator-owned, not request-selected. Empty preserves env.
ClassMethod ModelSetting() As %String
{
    Set value = ##class(Ens.Director).GetHostSettingValue("Investigator", "Model", .sc)
    If $SYSTEM.Status.IsError(sc) Return ""
    Return value
}

ClassMethod Resolve() As %String [ Language = python ]
{
    import iris, os, sys, json
    iris.cls('SilentShift.Bridge').Import()
    from silentshift.provider_config import resolve_provider
    environment = dict(os.environ)
    configured_model = iris.cls('SilentShift.Provider.Config').ModelSetting()
    if configured_model:
        environment['SILENTSHIFT_MODEL'] = configured_model
    return json.dumps(resolve_provider(environment).public(),sort_keys=True,separators=(',',':'))
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
