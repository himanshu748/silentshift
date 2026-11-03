Include (%occStatus, %outUnitTest)

/// Native provider contracts and metadata export. No method calls a model.
Class SilentShift.Test.ProviderChecks Extends %UnitTest.TestCase
{
Method TestMetadataOnlyMessages()
{
    Set request = ##class(SilentShift.Provider.CallRequest).%New()
    Set request.CallId = "synthetic-call", request.CaseId = "synthetic-case", request.ProductionSessionId = 42
    Set request.Round = 1, request.Model = "qwen3-silentshift:4b-instruct", request.ToolNamesJSON = "[]"
    Set data = ##class(%DynamicObject).%FromJSON(request.AsJSON())
    Do $$$AssertEquals(data.%Get("granularity"),"provider_http_call")
    Do $$$AssertEquals(data.%GetTypeOf("provider_retry_count"),"null")
    Do $$$AssertEquals(data.%GetTypeOf("billing_cost"),"null")
    Do $$$AssertTrue('data.%Get("content_retained"))
    Do $$$AssertTrue('data.%IsDefined("prompt") && 'data.%IsDefined("messages") && 'data.%IsDefined("authorization"))
    Set response = ##class(SilentShift.Provider.CallResponse).%New()
    Set response.CallId = request.CallId, response.HTTPStatus = 502
    Set response.ErrorCode = "PROVIDER_TRANSPORT_FAILED", response.DurationMS = 0, response.ResponseBytes = 0
    Set data = ##class(%DynamicObject).%FromJSON(response.AsJSON())
    Do $$$AssertEquals(data.%GetTypeOf("upstream_http_status"),"null")
    Do $$$AssertEquals(data.%GetTypeOf("response_usage"),"null")
    Do $$$AssertEquals(data.%Get("http_status"),502)
    Do $$$AssertTrue('data.%Get("fallback_used"))
    Do $$$AssertTrue('data.%IsDefined("raw_response") && 'data.%IsDefined("arguments"))
}

Method TestAuthorizationRejectsUnknownCapability()
{
    Do $$$AssertTrue('##class(SilentShift.Provider.Lease).AuthorizeBearer("",.binding))
    Do $$$AssertTrue('##class(SilentShift.Provider.Lease).AuthorizeBearer("Basic synthetic",.binding))
    Do $$$AssertTrue('##class(SilentShift.Provider.Lease).AuthorizeBearer("Bearer synthetic-unknown-capability-0000000000000000",.binding))
    Set sc = ##class(SilentShift.Provider.Lease).Claim("Bearer synthetic-unknown-capability-0000000000000000","{}",.request)
    Do $$$AssertStatusNotOK(sc)
    Do $$$AssertTrue('$ISOBJECT(request))
}

Method TestExpiredCapability()
{
    Set token = $TRANSLATE($SYSTEM.Encryption.Base64Encode($SYSTEM.Encryption.GenCryptRand(32,1),1),"+/","-_")
    Set key = ##class(SilentShift.Provider.Lease).TokenKey(token)
    Set expired = {"Expires":(##class(SilentShift.Provider.Lease).Seconds()-1)}
    Set ^CacheTemp.SilentShift.Provider("lease",key,"binding") = expired.%ToJSON()
    Set accepted = ##class(SilentShift.Provider.Lease).AuthorizeBearer("Bearer "_token,.binding)
    Do ##class(SilentShift.Provider.Lease).Close(token)
    Do $$$AssertTrue('accepted)
    Do $$$AssertTrue('$DATA(^CacheTemp.SilentShift.Provider("lease",key)))
}

/// No network: verifies temporary stream assignment and RAW HTTP controls.
ClassMethod TransportContract() As %String
{
    Set request = ##class(%Net.HttpRequest).%New()
    Set out = request.EntityBody, in = ##class(SilentShift.Provider.BoundedBinaryStream).%New()
    Set location = $NAME(^CacheTemp.SilentShift.Provider("contract-test","stream"))
    Set out.%Location = location, request.ResponseStream = in
    Set request.ReadRawMode = 1, request.WriteRawMode = 1, request.AcceptGzip = 0
    Set request.FollowRedirect = 0
    Set result = {"temporary_store_safe":false,"entity_body_iris_temp":false,"response_stream_tmp":false,"raw_modes":false,"unknown_bearer_rejected":false,"maximum_calls":(##class(SilentShift.Provider.Lease).#MAXCALLS),"maximum_bytes":(##class(SilentShift.Provider.Lease).#MAXBYTES),"native_http_log_level":($GET(^%ISCLOG,1))}
    Do result.%Set("temporary_store_safe",##class(SilentShift.Provider.Lease).TemporaryStoreSafe(),"boolean")
    Do result.%Set("entity_body_iris_temp",request.EntityBody.%Location = location,"boolean")
    Do result.%Set("response_stream_tmp",request.ResponseStream.%IsA("%Stream.TmpBinary"),"boolean")
    Do result.%Set("raw_modes",request.ReadRawMode && request.WriteRawMode && 'request.AcceptGzip && 'request.FollowRedirect,"boolean")
    Do result.%Set("unknown_bearer_rejected",'##class(SilentShift.Provider.Lease).AuthorizeBearer("Bearer synthetic-unknown-capability-0000000000000000",.binding),"boolean")
    Do result.%Set("global_destination",##class(%SYS.Namespace).GetGlobalDest($NAMESPACE,"^CacheTemp.SilentShift.Provider"))
    Set raw = $ZCONVERT("SYNTHETIC caf"_$CHAR(233)_" "_$CHAR(28450,23383),"O","UTF8")
    Set sc = out.Write(raw)
    Set rewound = out.Rewind(), echoed = out.Read(256)
    Do result.%Set("outbound_utf8_bytes_exact",$$$ISOK(sc) && $$$ISOK(rewound) && (echoed = raw) && (out.Size = $LENGTH(raw)),"boolean")
    Set in.ByteLimit = 4, pair = $CHAR(195,169)
    Set first = in.Write(pair_pair), second = in.Write("x"), third = in.Write("y")
    Do in.Rewind()
    Do result.%Set("response_cap_before_allocation",$$$ISOK(first) && $$$ISERR(second) && $$$ISERR(third) && in.Exceeded && (in.Size = 4) && (in.Read(8) = (pair_pair)),"boolean")
    Set reply = ##class(%Net.HttpResponse).%New(), reply.Data = in
    Set absentAccepted = (##class(SilentShift.Provider.Forwarder).ResponseContractError(reply,in) = "")
    Do reply.SetHeader("Content-Encoding"," identity ")
    Do result.%Set("identity_response_contract",absentAccepted && (##class(SilentShift.Provider.Forwarder).ResponseContractError(reply,in) = ""),"boolean")
    Do reply.SetHeader("Content-Encoding","gzip")
    Do result.%Set("nonidentity_response_rejected",##class(SilentShift.Provider.Forwarder).ResponseContractError(reply,in) = "PROVIDER_CONTENT_ENCODING_REJECTED","boolean")
    Set reply = ##class(%Net.HttpResponse).%New()
    Do reply.SetHeader("Content-Encoding","identity")
    Set reply.Data = ##class(%Stream.TmpBinary).%New()
    Do result.%Set("replacement_response_sink_rejected",##class(SilentShift.Provider.Forwarder).ResponseContractError(reply,in) = "PROVIDER_RESPONSE_SINK_CHANGED","boolean")
    Set ignored = out.Clear(), ignored = in.Clear()
    Kill ^CacheTemp.SilentShift.Provider("contract-test")
    Return result.%ToJSON()
}

/// Read-only export of real paired Ens headers; metadata comes from their
/// actual persisted typed message bodies, rather than a reconstructed Chat log.
ClassMethod InspectCase(id As %String) As %String
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), headers = [], calls = []
    Set agent = body.%Get("agent"), trace = ""
    If $ISOBJECT(agent) Set trace = agent.%Get("trace")
    Set result = {"case_id":(id),"scenario_id":(body.%Get("scenario_id")),"trace_id":(body.%Get("trace_id")),"routing":(body.%Get("routing")),"delivery_count":(body.%Get("delivery_count")),"invocation_trace":(trace),"native_headers":(headers),"provider_messages":(calls),"transient_call_count":0}
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT TOP 100 ID,SessionId,CorrespondingMessageId,SourceConfigName,TargetConfigName,MessageBodyClassName,MessageBodyId,TimeCreated,TimeProcessed FROM Ens.MessageHeader WHERE SessionId = ? AND MessageBodyClassName IN ('SilentShift.Provider.CallRequest','SilentShift.Provider.CallResponse') ORDER BY ID")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(+body.%Get("trace_id"))
    If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PROVIDER_HEADER_READ_FAILED")
    While rows.%Next() {
        Set header = {"id":(rows.%Get("ID")),"session_id":(rows.%Get("SessionId")),"corresponding_message_id":(rows.%Get("CorrespondingMessageId")),"source":(rows.%Get("SourceConfigName")),"target":(rows.%Get("TargetConfigName")),"body_class":(rows.%Get("MessageBodyClassName")),"body_id":(rows.%Get("MessageBodyId")),"created_at":(rows.%Get("TimeCreated")),"processed_at":(rows.%Get("TimeProcessed"))}
        Do headers.%Push(header)
        Set entry = $CLASSMETHOD(rows.%Get("MessageBodyClassName"),"%OpenId",rows.%Get("MessageBodyId"))
        If '$ISOBJECT(entry) Throw ##class(%Exception.General).%New("PROVIDER_BODY_MISSING")
        Set data = ##class(%DynamicObject).%FromJSON(entry.AsJSON())
        Do data.%Set("message_header_id",rows.%Get("ID"))
        Do calls.%Push(data)
    }
    Set call = "", count = 0
    For {
        Set call = $ORDER(^CacheTemp.SilentShift.Provider("call",call))
        Quit:call=""
        Set encoded = $GET(^CacheTemp.SilentShift.Provider("call",call,"binding"))
        If encoded '= "" {
            Set binding = ##class(%DynamicObject).%FromJSON(encoded)
            If binding.CaseId = id Set count = count+1
        }
    }
    Do result.%Set("transient_call_count",count,"number")
    Return result.%ToJSON()
}
}
