Include %occStatus

/// Server-issued capabilities and short-lived raw byte transport. CacheTemp.*
/// maps to the verified IRISTEMP database, which has GlobalJournalState=2 (No).
/// No token, request body or response body is stored in application globals.
Class SilentShift.Provider.Lease Extends %RegisteredObject
{
Parameter MAXBYTES = 262144;
Parameter MAXCALLS = 8;

/// Deployment-owned, never selected by an incoming partner message.
ClassMethod ExecutionMode() As %String
{
    Set mode = $SYSTEM.Util.GetEnviron("SILENTSHIFT_PROVIDER_MODE")
    If mode = "" Return "live"
    If (mode '= "live") && (mode '= "recorded-replay") Throw ##class(%Exception.General).%New("PROVIDER_MODE_INVALID")
    Return mode
}

ClassMethod Seconds() As %Integer
{
    Set stamp = $ZTIMESTAMP
    Return ($PIECE(stamp,",",1)*86400)+($PIECE(stamp,",",2)\1)
}

ClassMethod TemporaryStoreSafe() As %Boolean
{
    Set destination = ##class(%SYS.Namespace).GetGlobalDest($NAMESPACE,"^CacheTemp.SilentShift.Provider")
    Return ($ZCONVERT(destination,"L") [ "/iristemp/") && ($GET(^%ISCLOG,1) < 3)
}

ClassMethod TokenKey(token As %String) As %String
{
    Return $SYSTEM.Encryption.Base64Encode($SYSTEM.Encryption.SHAHash(256,token),1)
}

ClassMethod LocalHost(Output host As %String) As %Status
{
    Set host = "", url = $SYSTEM.Util.GetEnviron("SILENTSHIFT_LLM_BASE_URL")
    For allowed = "localhost", "127.0.0.1", "host.docker.internal", "host.lima.internal", "ollama" {
        If url = ("http://"_allowed_":11434/v1/") Set host = allowed
    }
    If host = "" Return $$$ERROR($$$GeneralError,"PROVIDER_LOCAL_ROUTE_REQUIRED")
    If $SYSTEM.Util.GetEnviron("SILENTSHIFT_MODEL") '= ##class(SilentShift.Provider.Config).DefaultModel() Return $$$ERROR($$$GeneralError,"PROVIDER_LOCAL_MODEL_REQUIRED")
    Return $$$OK
}

ClassMethod CaseMatches(caseId As %String, sessionId As %Integer) As %Boolean
{
    If (caseId = "") || (sessionId < 1) Return 0
    Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(caseId)
    If '$ISOBJECT(record) Return 0
    If record.Routing '= "PROCESSING" Return 0
    Set body = ##class(%DynamicObject).%FromJSON(record.Body)
    Return (body.%Get("routing") = "PROCESSING") && (body.%Get("trace_id") = (sessionId_""))
}

ClassMethod Open(caseId As %String, sessionId As %Integer, model As %String, promptVersion As %String, Output token As %String, invocationSpan As %String = "") As %Status
{
    Set token = ""
    Try {
        If '..TemporaryStoreSafe() Return $$$ERROR($$$GeneralError,"PROVIDER_TEMP_MAPPING_REQUIRED")
        Set mode = ..ExecutionMode()
        If mode = "recorded-replay" {
            Set sc = ##class(SilentShift.Provider.Replay).CheckCase(caseId)
            $$$ThrowOnError(sc)
        }
        Set config=##class(SilentShift.Provider.Config).Read(),host=config.%Get("host")
        If model '= config.%Get("model") Return $$$ERROR($$$GeneralError,"PROVIDER_MODEL_CONFIGURATION_MISMATCH")
        If '..CaseMatches(caseId,sessionId) Return $$$ERROR($$$GeneralError,"PROVIDER_CASE_BINDING_INVALID")
        If (promptVersion = "") || ($LENGTH(promptVersion) > 80) Return $$$ERROR($$$GeneralError,"PROVIDER_PROMPT_VERSION_INVALID")
        If invocationSpan = "" Set invocationSpan = $TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
        If $LENGTH(invocationSpan) > 80 Return $$$ERROR($$$GeneralError,"PROVIDER_SPAN_INVALID")
        Do ..Sweep()
        Set token = $TRANSLATE($SYSTEM.Encryption.Base64Encode($SYSTEM.Encryption.GenCryptRand(32,1),1),"+/","-_")
        Set key = ..TokenKey(token), expires = ..Seconds()+##class(SilentShift.AI.Investigator).WaitSeconds()+5
        Set binding = {"CaseId":(caseId),"SessionId":(sessionId),"Model":(model),"PromptVersion":(promptVersion),"InvocationSpanId":(invocationSpan),"Host":(host),"Expires":(expires)}
        Do binding.%Set("RouteSignature",##class(SilentShift.Bridge).Hash(config.%ToJSON()))
        Do binding.%Set("Provider",config.%Get("trace_provider"))
        Do binding.%Set("ExecutionMode", mode)
        Set ^CacheTemp.SilentShift.Provider("lease",key,"binding") = binding.%ToJSON()
        Set ^CacheTemp.SilentShift.Provider("lease",key,"count") = 0
        Return $$$OK
    } Catch error {
        Set token = ""
        Return $$$ERROR($$$GeneralError,"PROVIDER_LEASE_UNAVAILABLE")
    }
}

/// Authentication happens before request JSON is read. No client association
/// fields are consulted; the bearer binds the original server-known case.
ClassMethod AuthorizeBearer(header As %String, Output binding As %DynamicObject) As %Boolean
{
    Set binding = ""
    Try {
        If $EXTRACT(header,1,7) '= "Bearer " Return 0
        Set token = $EXTRACT(header,8,*), length = $LENGTH(token)
        If (length < 40) || (length > 64) Return 0
        Set key = ..TokenKey(token), encoded = $GET(^CacheTemp.SilentShift.Provider("lease",key,"binding"))
        If encoded = "" Return 0
        Set candidate = ##class(%DynamicObject).%FromJSON(encoded)
        If candidate.Expires < ..Seconds() Return 0
        If '..CaseMatches(candidate.CaseId,candidate.SessionId) Return 0
        If $GET(^CacheTemp.SilentShift.Provider("lease",key,"count")) >= ..#MAXCALLS Return 0
        Set binding = candidate
        Return 1
    } Catch error {
        Return 0
    }
}

/// Shape only the final local-model request after this invocation's four reads.
/// This is pre-inference request configuration, never output repair or retry.
ClassMethod ShapeFinal(raw As %String, binding As %DynamicObject, Output shaped As %Boolean) As %String
{
    Set shaped=0
    If (binding.%Get("ExecutionMode")'="live") || (binding.%Get("Provider")'="ollama/openai-compatible") || (binding.%Get("PromptVersion")'="silentshift-investigator/1.4.2") Return raw
    Set statement=##class(%SQL.Statement).%New()
    Set sc=statement.%Prepare("SELECT Detail FROM SilentShift_Data.AuditEvent WHERE CaseId=? AND Kind='agent_tool_read'")
    $$$ThrowOnError(sc)
    Set rows=statement.%Execute(binding.CaseId),seen=0
    If rows.%SQLCODE<0 Throw ##class(%Exception.General).%New("FINAL_FORMAT_READ_CHECK_FAILED")
    While rows.%Next() {
        Set detail=##class(%DynamicObject).%FromJSON(rows.%Get("Detail"))
        If detail.%Get("invocation_span_id")'=binding.InvocationSpanId Continue
        Set tool=detail.%Get("tool")
        If tool="GetCurrentMessage" Set reads("message")=1
        If tool="GetApprovedContracts" Set reads("contracts")=1
        If tool="GetRelatedRecords" Set reads("related")=1
        If tool="find_similar_precedents" Set reads("precedents")=1
    }
    If '$DATA(reads("message")) || '$DATA(reads("contracts")) || '$DATA(reads("related")) || '$DATA(reads("precedents")) Return raw
    Set body=##class(%DynamicObject).%FromJSON($ZCONVERT(raw,"I","UTF8"))
    Do body.%Remove("tools"),body.%Remove("tool_choice"),body.%Remove("parallel_tool_calls")
    // Read the server-owned assessment directly: no extra SQL privileges,
    // Embedded Python callback, partner-provided IDs, or response mutation.
    Set record=##class(SilentShift.Data.CaseRecord).%OpenId(binding.CaseId)
    If '$ISOBJECT(record) Throw ##class(%Exception.General).%New("FINAL_FORMAT_CASE_UNAVAILABLE")
    Set current=##class(%DynamicObject).%FromJSON(record.Body),assessment=current.%Get("assessment")
    If '$ISOBJECT(assessment) Throw ##class(%Exception.General).%New("FINAL_FORMAT_CITATIONS_UNAVAILABLE")
    Set ids=assessment.%Get("evidence_ids")
    If '$ISOBJECT(ids) Throw ##class(%Exception.General).%New("FINAL_FORMAT_CITATIONS_UNAVAILABLE")
    Do body.%Set("response_format",##class(SilentShift.AI.Investigator).FinalResponseFormat(ids))
    Set result=$ZCONVERT(body.%ToJSON(),"O","UTF8")
    If $LENGTH(result)>..#MAXBYTES Throw ##class(%Exception.General).%New("FINAL_FORMAT_REQUEST_BOUNDS")
    Set shaped=1
    Return result
}

/// Claims one actual call after authentication and bounded payload validation.
ClassMethod Claim(header As %String, raw As %String, Output request As SilentShift.Provider.CallRequest, tools As %String = "[]") As %Status
{
    Set request = "", locked = 0, call = ""
    Try {
        If (raw = "") || ($LENGTH(raw) > ..#MAXBYTES) || ($LENGTH(tools) > 512) Return $$$ERROR($$$GeneralError,"PROVIDER_REQUEST_BOUNDS")
        If '..AuthorizeBearer(header,.binding) Return $$$ERROR($$$GeneralError,"PROVIDER_LEASE_REJECTED")
        Set key = ..TokenKey($EXTRACT(header,8,*))
        Lock +^CacheTemp.SilentShift.Provider("lease",key):2
        If '$TEST Return $$$ERROR($$$GeneralError,"PROVIDER_LEASE_BUSY")
        Set locked = 1
        If '..AuthorizeBearer(header,.binding) Throw ##class(%Exception.General).%New("PROVIDER_LEASE_REJECTED")
        Set round = $INCREMENT(^CacheTemp.SilentShift.Provider("lease",key,"count"))
        Set request = ##class(SilentShift.Provider.CallRequest).%New()
        Set request.CallId = $TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
        Set request.CaseId = binding.CaseId, request.ProductionSessionId = binding.SessionId
        Set request.InvocationSpanId = binding.InvocationSpanId, request.Round = round
        Set request.Model = binding.Model, request.PromptVersion = binding.PromptVersion
        Set request.Provider=binding.%Get("Provider","ollama/openai-compatible")
        Set request.ExecutionMode = binding.%Get("ExecutionMode", "live")
        If request.ExecutionMode = "recorded-replay" {
            Set request.Provider = "recorded-ollama/openai-compatible"
            Set request.ReplayRecordId = ##class(SilentShift.Provider.Replay).#RECORDID
        }
        Set raw=..ShapeFinal(raw,binding,.shaped)
        If shaped Set tools="[]"
        Set request.StructuredFinal=shaped
        If shaped Set request.FinalFormatVersion=##class(SilentShift.AI.Investigator).#FINALFORMATVERSION
        Set request.StartedAt = ##class(SilentShift.TraceEvent).UTC(), request.RequestBytes = $LENGTH(raw)
        Set request.ToolNamesJSON = tools
        Set call = request.CallId
        Set ^CacheTemp.SilentShift.Provider("call",call,"binding") = binding.%ToJSON()
        Set ^CacheTemp.SilentShift.Provider("call",call,"lease") = key
        Set ^CacheTemp.SilentShift.Provider("call",call,"round") = round
        Set ^CacheTemp.SilentShift.Provider("call",call,"request") = raw
        Set ^CacheTemp.SilentShift.Provider("call",call,"state") = "pending"
        Lock -^CacheTemp.SilentShift.Provider("lease",key)
        Return $$$OK
    } Catch error {
        If locked Lock -^CacheTemp.SilentShift.Provider("lease",key)
        Do ..Cleanup(call)
        Return $$$ERROR($$$GeneralError,"PROVIDER_CALL_REJECTED")
    }
}

ClassMethod Close(token As %String)
{
    If token = "" Quit
    Set key = ..TokenKey(token)
    Lock +^CacheTemp.SilentShift.Provider("lease",key):2
    If '$TEST Quit
    Kill ^CacheTemp.SilentShift.Provider("lease",key)
    Lock -^CacheTemp.SilentShift.Provider("lease",key)
}

ClassMethod Cleanup(call As %String)
{
    If call = "" Quit
    Lock +^CacheTemp.SilentShift.Provider("call",call):5
    If '$TEST Quit
    Kill ^CacheTemp.SilentShift.Provider("call",call)
    Lock -^CacheTemp.SilentShift.Provider("call",call)
}

/// Bounded opportunistic cleanup supplements mandatory API completion cleanup.
ClassMethod Sweep()
{
    For kind = "lease", "call" {
        Set key = "", checked = 0
        For {
            Set key = $ORDER(^CacheTemp.SilentShift.Provider(kind,key))
            Quit:((key = "") || (checked >= 64))
            Set checked = checked+1, encoded = $GET(^CacheTemp.SilentShift.Provider(kind,key,"binding"))
            If encoded '= "" {
                Set binding = ##class(%DynamicObject).%FromJSON(encoded)
                If binding.Expires < ..Seconds() {
                    If kind = "call" {
                        Do ..Cleanup(key)
                    } Else {
                        Lock +^CacheTemp.SilentShift.Provider("lease",key):1
                        If $TEST {
                            Kill ^CacheTemp.SilentShift.Provider("lease",key)
                            Lock -^CacheTemp.SilentShift.Provider("lease",key)
                        }
                    }
                }
            }
        }
    }
}
}
