Include (%occStatus, Ensemble)

/// Fixed local Ollama operation in its own pool. Every actual provider POST
/// passes through one native request/response pair in the original session.
Class SilentShift.Provider.Forwarder Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";

Method Forward(request As SilentShift.Provider.CallRequest, Output response As SilentShift.Provider.CallResponse) As %Status
{
    Set response = ##class(SilentShift.Provider.CallResponse).%New()
    Set response.CallId = request.CallId, response.CaseId = request.CaseId
    Set response.ProductionSessionId = request.ProductionSessionId, response.InvocationSpanId = request.InvocationSpanId
    Set response.Round = request.Round, response.Model = request.Model, response.PromptVersion = request.PromptVersion
    Set response.StartedAt = ##class(SilentShift.TraceEvent).UTC(), started = $ZTIMESTAMP
    Set response.HTTPStatus = 503, response.ErrorCode = "PROVIDER_CALL_UNAVAILABLE", response.ResponseBytes = 0
    Set call = request.CallId, claimed = 0, locked = 0
    Try {
        If (request.ProductionSessionId < 1) || (request.ProductionSessionId '= ..%SessionId) Throw ##class(%Exception.General).%New("PROVIDER_SESSION_MISMATCH")
        Lock +^CacheTemp.SilentShift.Provider("call",call):2
        If '$TEST Throw ##class(%Exception.General).%New("PROVIDER_CALL_BUSY")
        Set locked = 1, encoded = $GET(^CacheTemp.SilentShift.Provider("call",call,"binding"))
        If encoded = "" Throw ##class(%Exception.General).%New("PROVIDER_CALL_MISSING")
        Set binding = ##class(%DynamicObject).%FromJSON(encoded)
        Set leaseKey = $GET(^CacheTemp.SilentShift.Provider("call",call,"lease"))
        If (binding.CaseId '= request.CaseId) || (binding.SessionId '= request.ProductionSessionId) || (binding.Model '= request.Model) || (binding.InvocationSpanId '= request.InvocationSpanId) Throw ##class(%Exception.General).%New("PROVIDER_CALL_BINDING_INVALID")
        If (binding.Expires < ##class(SilentShift.Provider.Lease).Seconds()) || '..CaseActive(binding) Throw ##class(%Exception.General).%New("PROVIDER_CALL_EXPIRED")
        If '$DATA(^CacheTemp.SilentShift.Provider("lease",leaseKey,"binding")) Throw ##class(%Exception.General).%New("PROVIDER_LEASE_CLOSED")
        If $GET(^CacheTemp.SilentShift.Provider("call",call,"state")) '= "pending" Throw ##class(%Exception.General).%New("PROVIDER_CALL_ALREADY_SENT")
        Set raw = $GET(^CacheTemp.SilentShift.Provider("call",call,"request"))
        If (raw = "") || ($LENGTH(raw) > ##class(SilentShift.Provider.Lease).#MAXBYTES) Throw ##class(%Exception.General).%New("PROVIDER_REQUEST_BOUNDS")
        Set sc = ##class(SilentShift.Provider.Lease).LocalHost(.host)
        $$$ThrowOnError(sc)
        If '##class(SilentShift.Provider.Lease).TemporaryStoreSafe() Throw ##class(%Exception.General).%New("PROVIDER_TEMP_OR_LOG_CONFIGURATION_UNSAFE")
        If host '= binding.Host Throw ##class(%Exception.General).%New("PROVIDER_ROUTE_CHANGED")
        Set ^CacheTemp.SilentShift.Provider("call",call,"state") = "sending", claimed = 1
        Kill ^CacheTemp.SilentShift.Provider("call",call,"request")
        Lock -^CacheTemp.SilentShift.Provider("call",call)
        Set locked = 0

        // EntityBody's legacy stream setter copies a supplied stream into a
        // GlobalBinaryStream. Set its explicit location before writing instead;
        // even an accidental save then targets only nonjournaled IRISTEMP.
        Set http = ##class(%Net.HttpRequest).%New(), inbound = ##class(SilentShift.Provider.BoundedBinaryStream).%New()
        Set outbound = http.EntityBody
        Set outbound.%Location = $NAME(^CacheTemp.SilentShift.Provider("call",call,"stream"))
        Set sc = outbound.Write(raw)
        $$$ThrowOnError(sc)
        Set raw = ""
        Set http.Server = host, http.Port = 11434, http.Https = 0
        Set http.FollowRedirect = 0, http.AcceptGzip = 0, http.PostGzip = 0
        Set http.ReadRawMode = 1, http.WriteRawMode = 1, http.SocketTimeout = 0
        Set remaining = binding.Expires-##class(SilentShift.Provider.Lease).Seconds()
        If remaining < 1 Throw ##class(%Exception.General).%New("PROVIDER_CALL_EXPIRED")
        Set http.Timeout = remaining, http.OpenTimeout = $SELECT(remaining > 5:5,1:remaining), http.WriteTimeout = $SELECT(remaining > 5:5,1:remaining)
        Set http.ContentType = "application/json", http.ContentCharset = "utf-8"
        Set sc = http.SetHeader("Accept-Encoding","identity")
        $$$ThrowOnError(sc)
        Set http.ResponseStream = inbound
        Set sc = http.Post("/v1/chat/completions")
        If '$ISOBJECT(http.HttpResponse) Throw ##class(%Exception.General).%New("PROVIDER_TRANSPORT_FAILED")
        Set upstream = http.HttpResponse.StatusCode
        If (upstream < 100) || (upstream > 599) Throw ##class(%Exception.General).%New("PROVIDER_TRANSPORT_FAILED")
        Set response.UpstreamHTTPStatus = upstream
        Set contractError = ..ResponseContractError(http.HttpResponse,inbound)
        If contractError '= "" {
            Set response.HTTPStatus = 502, response.ErrorCode = contractError
        } ElseIf inbound.Exceeded || (inbound.Size > ##class(SilentShift.Provider.Lease).#MAXBYTES) {
            Set response.HTTPStatus = 502, response.ErrorCode = "PROVIDER_RESPONSE_BOUNDS"
        } Else {
            If $$$ISERR(sc) Throw ##class(%Exception.General).%New("PROVIDER_TRANSPORT_FAILED")
            Do inbound.Rewind()
            Set rawResponse = inbound.Read(##class(SilentShift.Provider.Lease).#MAXBYTES+1)
            If $LENGTH(rawResponse) > ##class(SilentShift.Provider.Lease).#MAXBYTES Throw ##class(%Exception.General).%New("PROVIDER_RESPONSE_BOUNDS")
            Set response.HTTPStatus = upstream, response.ResponseBytes = $LENGTH(rawResponse)
            Set response.ErrorCode = $SELECT(upstream >= 400:"UPSTREAM_HTTP_ERROR",1:"")
            Lock +^CacheTemp.SilentShift.Provider("call",call):2
            If '$TEST Throw ##class(%Exception.General).%New("PROVIDER_RESPONSE_PUBLISH_BUSY")
            Set locked = 1
            Set active = $DATA(^CacheTemp.SilentShift.Provider("call",call,"binding")) && $DATA(^CacheTemp.SilentShift.Provider("lease",leaseKey,"binding"))
            If active Set active = (binding.Expires >= ##class(SilentShift.Provider.Lease).Seconds()) && ..CaseActive(binding)
            If active {
                Set ^CacheTemp.SilentShift.Provider("call",call,"response") = rawResponse
                Set ^CacheTemp.SilentShift.Provider("call",call,"state") = "complete"
            } Else {
                Set response.HTTPStatus = 503, response.ErrorCode = "PROVIDER_RESPONSE_DISCARDED"
            }
            Lock -^CacheTemp.SilentShift.Provider("call",call)
            Set locked = 0
            Do ..ResponseMetadata(rawResponse,response)
            Set rawResponse = ""
        }
    } Catch error {
        // Never return provider exception text: it can contain response bodies.
        // An OK framework status prevents Ensemble's automatic BO retries.
        Set response.HTTPStatus = 502
        Set response.ErrorCode = $SELECT(claimed:"PROVIDER_TRANSPORT_FAILED",1:"PROVIDER_CALL_REJECTED")
    }
    If locked Lock -^CacheTemp.SilentShift.Provider("call",call)
    Try {
        If $ISOBJECT($GET(outbound)) Set ignored = outbound.Clear()
        If $ISOBJECT($GET(inbound)) Set ignored = inbound.Clear()
        Set outbound = "", inbound = "", http = ""
    } Catch cleanupError {
        // Explicit per-call IRISTEMP storage is also removed by API Cleanup.
    }
    Set response.FinishedAt = ##class(SilentShift.TraceEvent).UTC()
    Set response.DurationMS = ##class(SilentShift.TraceEvent).ElapsedMS(started)
    Return $$$OK
}

/// Identity encoding is part of the fixed local route contract. Native HTTP
/// can stage gzip to a temporary file before decoding into ResponseStream;
/// reject it rather than relay transformed bytes or claim that file was capped.
ClassMethod ResponseContractError(httpResponse As %Net.HttpResponse, sink As SilentShift.Provider.BoundedBinaryStream) As %String
{
    If '$ISOBJECT(httpResponse) Return "PROVIDER_RESPONSE_SINK_CHANGED"
    Set encoding = $ZSTRIP($ZCONVERT(httpResponse.GetHeader("CONTENT-ENCODING"),"L"),"<>W")
    If (encoding '= "") && (encoding '= "identity") Return "PROVIDER_CONTENT_ENCODING_REJECTED"
    If '$ISOBJECT(httpResponse.Data) Return "PROVIDER_RESPONSE_SINK_CHANGED"
    If httpResponse.Data '= sink Return "PROVIDER_RESPONSE_SINK_CHANGED"
    Return ""
}

Method CaseActive(binding As %DynamicObject) As %Boolean [ Private ]
{
    Return ##class(SilentShift.Provider.Lease).CaseMatches(binding.CaseId,binding.SessionId)
}

/// Parse only bounded metadata. Content, reasoning and function arguments are
/// never copied into persistent messages. Parsing cannot alter the HTTP relay.
Method ResponseMetadata(raw As %String, response As SilentShift.Provider.CallResponse) [ Private ]
{
    Try {
        Set canonical = ##class(SilentShift.Bridge).Canonical($ZCONVERT(raw,"I","UTF8"))
        Set data = ##class(%DynamicObject).%FromJSON(canonical), usage = data.%Get("usage")
        If $ISOBJECT(usage) {
            For field = "prompt_tokens", "completion_tokens", "total_tokens" {
                If usage.%GetTypeOf(field) = "number" {
                    Set value = usage.%Get(field)
                    If (value >= 0) && (value = $JUSTIFY(value,0,0)) && (value < 1000000000) {
                        If field = "prompt_tokens" Set response.PromptTokens = value
                        If field = "completion_tokens" Set response.CompletionTokens = value
                        If field = "total_tokens" Set response.TotalTokens = value
                    }
                }
            }
        }
        Set choices = data.%Get("choices"), calls = []
        If '$ISOBJECT(choices) Quit
        If choices.%Size() < 1 Quit
        Set choice = choices.%Get(0), reason = choice.%Get("finish_reason")
        If (reason = "stop") || (reason = "length") || (reason = "tool_calls") || (reason = "content_filter") || (reason = "function_call") Set response.FinishReason = reason
        Set message = choice.%Get("message")
        If '$ISOBJECT(message) Quit
        Set source = message.%Get("tool_calls")
        If '$ISOBJECT(source) Quit
        For index = 0:1:source.%Size()-1 {
            Quit:(index >= 8)
            Set item = source.%Get(index), function = item.%Get("function"), name = "unrecognized"
            If $ISOBJECT(function) {
                Set candidate = function.%Get("name")
                If (candidate = "GetCurrentMessage") || (candidate = "GetApprovedContracts") || (candidate = "GetRelatedRecords") Set name = candidate
            }
            Set id = item.%Get("id"), safeId = ""
            If ($LENGTH(id) <= 96) && (id ? 1.96(1AN,1"_",1"-")) Set safeId = id
            Do calls.%Push({"id":(safeId),"name":(name),"arguments_omitted":true})
        }
        Set response.ToolCallsJSON = calls.%ToJSON()
    } Catch error {
        // HTTP status/bytes still describe the genuine upstream outcome.
    }
}

XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Provider.CallRequest"><Method>Forward</Method></MapItem></MapItems>
}
}
