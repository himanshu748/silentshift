Include (%occStatus, Ensemble)

/// Internal SDK HTTP gateway. Only an active server-issued bearer can enter;
/// the SDK cannot choose its production session, case, model or upstream URL.
Class SilentShift.Provider.API Extends %CSP.REST
{
Parameter CHARSET = "utf-8";
Parameter HandleCorsRequest = 0;
Parameter UseSession = 0;

XData UrlMap [ XMLNamespace = "http://www.intersystems.com/urlmap" ]
{
<Routes><Route Url="/v1/chat/completions" Method="POST" Call="ChatCompletions"/></Routes>
}

ClassMethod OnPreDispatch(url As %String, method As %String, ByRef continue As %Boolean) As %Status
{
    Set continue = 0
    Do %response.SetHeader("Cache-Control","no-store")
    Do %response.SetHeader("X-Content-Type-Options","nosniff")
    If '##class(SilentShift.Provider.Lease).AuthorizeBearer(%request.GetCgiEnv("HTTP_AUTHORIZATION"),.binding) Return ..Fail(401,"PROVIDER_LEASE_REQUIRED")
    If method '= "POST" Return ..Fail(405,"PROVIDER_POST_REQUIRED")
    If $ZCONVERT($PIECE(%request.ContentType,";",1),"L") '= "application/json" Return ..Fail(415,"PROVIDER_JSON_REQUIRED")
    Set continue = 1
    Return $$$OK
}

ClassMethod Fail(status As %Integer, code As %String) As %Status
{
    Set %response.Status = status, %response.ContentType = "application/json"
    Write {"error":{"type":"silentshift_provider_gateway","code":(code)}}.%ToJSON()
    Return $$$OK
}

ClassMethod ChatCompletions() As %Status
{
    Set call = "", status = 503, code = "PROVIDER_GATEWAY_UNAVAILABLE", body = "", relay = 0
    Try {
        Set header = %request.GetCgiEnv("HTTP_AUTHORIZATION")
        If '##class(SilentShift.Provider.Lease).AuthorizeBearer(header,.binding) Return ..Fail(401,"PROVIDER_LEASE_REQUIRED")
        If '$ISOBJECT(%request.Content) Return ..Fail(400,"PROVIDER_BODY_REQUIRED")
        If %request.Content.Size > ##class(SilentShift.Provider.Lease).#MAXBYTES Return ..Fail(413,"PROVIDER_REQUEST_BOUNDS")
        Do %request.Content.Rewind()
        Set raw = %request.Content.Read(##class(SilentShift.Provider.Lease).#MAXBYTES+1)
        If $LENGTH(raw) > ##class(SilentShift.Provider.Lease).#MAXBYTES Return ..Fail(413,"PROVIDER_REQUEST_BOUNDS")
        // This CSP job is separate from the SDK callback job. Strict parsing
        // validates duplicate keys/nonfinite values without re-entering Python
        // from a native agent callback. The original bytes are forwarded.
        Set payload = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Canonical($ZCONVERT(raw,"I","UTF8")))
        If payload.%Get("model") '= binding.Model Return ..Fail(422,"PROVIDER_MODEL_REJECTED")
        Set iterator = payload.%GetIterator()
        While iterator.%GetNext(.field,.value) {
            If ("|model|messages|tools|tool_choice|max_tokens|max_completion_tokens|stream|temperature|top_p|seed|stop|response_format|frequency_penalty|presence_penalty|parallel_tool_calls|reasoning_effort|n|" '[ ("|"_field_"|")) Return ..Fail(422,"PROVIDER_OPTION_REJECTED")
        }
        Set tokenFields = 0
        For field = "max_tokens", "max_completion_tokens" {
            If payload.%IsDefined(field) {
                If payload.%GetTypeOf(field) '= "number" Return ..Fail(422,"PROVIDER_TOKEN_BUDGET_REJECTED")
                Set tokens = payload.%Get(field), tokenFields = tokenFields+1
                If (tokens < 1) || (tokens > 700) || (tokens '= (tokens\1)) Return ..Fail(422,"PROVIDER_TOKEN_BUDGET_REJECTED")
            }
        }
        If tokenFields = 0 Return ..Fail(422,"PROVIDER_TOKEN_BUDGET_REQUIRED")
        If payload.%IsDefined("n") {
            If (payload.%GetTypeOf("n") '= "number") || (payload.%Get("n") '= 1) Return ..Fail(422,"PROVIDER_MULTIPLE_CHOICES_REJECTED")
        }
        If payload.%IsDefined("stream") {
            If (payload.%GetTypeOf("stream") '= "boolean") || payload.%Get("stream") Return ..Fail(422,"PROVIDER_STREAM_REJECTED")
        }
        Set messages = payload.%Get("messages")
        If '$ISOBJECT(messages) Return ..Fail(422,"PROVIDER_MESSAGES_REQUIRED")
        If (messages.%ClassName(1) '= "%Library.DynamicArray") || (messages.%Size() < 1) || (messages.%Size() > 32) Return ..Fail(422,"PROVIDER_MESSAGES_BOUNDS")
        Set names = [], tools = payload.%Get("tools")
        If $ISOBJECT(tools) {
            If (tools.%ClassName(1) '= "%Library.DynamicArray") || (tools.%Size() > 4) Return ..Fail(422,"PROVIDER_TOOLS_REJECTED")
            For index = 0:1:tools.%Size()-1 {
                Set item = tools.%Get(index), function = item.%Get("function")
                If '$ISOBJECT(function) Return ..Fail(422,"PROVIDER_TOOLS_REJECTED")
                Set name = function.%Get("name")
                If (name '= "GetCurrentMessage") && (name '= "GetApprovedContracts") && (name '= "GetRelatedRecords") && (name '= "find_similar_precedents") Return ..Fail(422,"PROVIDER_TOOLS_REJECTED")
                Do names.%Push(name)
            }
        }
        Set sc = ##class(SilentShift.Provider.Lease).Claim(header,raw,.request,names.%ToJSON())
        Set raw = "", header = ""
        $$$ThrowOnError(sc)
        Set call = request.CallId
        Set sc = ##class(Ens.Director).CreateBusinessService("ProviderIngress",.service)
        $$$ThrowOnError(sc)
        Set service.%PreserveSession = 1, service.%SessionId = binding.SessionId
        Set sc = service.ProcessInput(request,.reply)
        $$$ThrowOnError(sc)
        If '$ISOBJECT(reply) Throw ##class(%Exception.General).%New("PROVIDER_RESPONSE_MISSING")
        If 'reply.%IsA("SilentShift.Provider.CallResponse") Throw ##class(%Exception.General).%New("PROVIDER_RESPONSE_TYPE")
        Set status = reply.HTTPStatus, code = reply.ErrorCode
        If $DATA(^CacheTemp.SilentShift.Provider("call",call,"response")) {
            Set body = ^CacheTemp.SilentShift.Provider("call",call,"response"), relay = 1
        }
    } Catch error {
        // Neither request data nor native/provider exception text is logged.
        Set status = 502, code = "PROVIDER_GATEWAY_FAILED"
    }
    // Mandatory cleanup on successful relay, upstream failure and dispatch
    // exceptions. A late BO completion cannot recreate a removed call node.
    Do ##class(SilentShift.Provider.Lease).Cleanup(call)
    If 'relay Return ..Fail(status,code)
    Set %response.Status = status, %response.ContentType = "application/json", %response.NoCharSetConvert = 1
    Write body
    Return $$$OK
}
}
