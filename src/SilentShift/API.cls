Include (%occStatus, Ensemble)

/// Authenticated API. All writes enter the real Partner business service.
Class SilentShift.API Extends %CSP.REST
{

Parameter CHARSET = "utf-8";
Parameter HandleCorsRequest = 0;
Parameter UseSession = 0;

XData UrlMap [ XMLNamespace = "http://www.intersystems.com/urlmap" ]
{
<Routes>
  <Route Url="/api/health" Method="GET" Call="Health"/>
  <Route Url="/api/overview" Method="GET" Call="Overview"/>
  <Route Url="/api/cases" Method="GET" Call="Cases"/>
  <Route Url="/api/cases/:id" Method="GET" Call="Case"/>
  <Route Url="/api/cases/:id/review" Method="POST" Call="Review"/>
  <Route Url="/api/messages" Method="POST" Call="Ingest"/>
  <Route Url="/api/scenarios" Method="GET" Call="Scenarios"/>
  <Route Url="/api/scenarios/:id/run" Method="POST" Call="RunScenario"/>
  <Route Url="/api/policies" Method="GET" Call="Policies"/>
  <Route Url="/api/evaluations" Method="GET" Call="Evaluations"/>
  <Route Url="/api/evaluations" Method="POST" Call="CaptureEvaluation"/>
</Routes>
}

ClassMethod OnPreDispatch(url As %String, method As %String, ByRef continue As %Boolean) As %Status
{
    Set continue = 0
    Do %response.SetHeader("Cache-Control", "no-store")
    Do %response.SetHeader("X-Content-Type-Options", "nosniff")
    If '$SYSTEM.Security.Check("SSView", "USE") Return ..Fail(403, "FORBIDDEN", "SilentShift viewer permission is required.")
    If method = "POST" {
        // No cookie-only mutation: explicit Basic credentials and JSON are
        // required. Cross-origin forms cannot submit this API contract.
        If $EXTRACT(%request.GetCgiEnv("HTTP_AUTHORIZATION"),1,6) '= "Basic " Return ..Fail(401, "AUTH_REQUIRED", "Explicit API authentication is required.")
        If $PIECE(%request.ContentType,";",1) '= "application/json" Return ..Fail(415, "JSON_REQUIRED", "Use application/json.")
    }
    Set continue = 1
    Return $$$OK
}

ClassMethod JSON(value As %String, status As %Integer = 200) As %Status
{
    Set %response.ContentType = "application/json"
    Set %response.Status = status
    Write value
    Return $$$OK
}

ClassMethod Fail(status As %Integer, code As %String, message As %String) As %Status
{
    Set value = {"error": (code), "message": (message)}
    Return ..JSON(value.%ToJSON(),status)
}

ClassMethod ErrorResponse(error As %Exception.AbstractException) As %Status
{
    // Only stable application codes leave the server. ObjectScript/provider
    // exception text may contain credentials or internal filesystem paths.
    Set message = error.DisplayString()
    // Keep one bounded, redacted server-only diagnostic for operator recovery.
    // Never store request objects or headers, and never return this to a client.
    Try {
        Set diagnostic = message
        For name="SILENTSHIFT_IRIS_PASSWORD","SILENTSHIFT_VIEWER_PASSWORD","SILENTSHIFT_GATEWAY_PASSWORD","SILENTSHIFT_LLM_API_KEY","OPENAI_API_KEY" {
            Set secret=$SYSTEM.Util.GetEnviron(name)
            If secret'="" Set diagnostic=$REPLACE(diagnostic,secret,"[REDACTED]")
        }
        Set detail={"timestamp":($ZTIMESTAMP),"message":($EXTRACT(diagnostic,1,2048)),"effective_roles":($ROLES)}
        Set ^SilentShift.Diagnostics("last_api_error")=detail.%ToJSON()
    } Catch diagnosticError {
        // A failure to write diagnostics must not change the safe API response.
    }
    If message [ "APP_CONFLICT" Return ..Fail(409,"CONFLICT","The record changed or an idempotency key was reused with different content.")
    If message [ "APP_NOT_FOUND" Return ..Fail(404,"NOT_FOUND","The requested record was not found.")
    If message [ "APP_FORBIDDEN" Return ..Fail(403,"FORBIDDEN","This action is not permitted by the current policy or permissions.")
    If (message [ "APP_INVALID") || (message [ "INVALID_REQUEST") || (message [ "INVALID_EVALUATION") Return ..Fail(422,"INVALID_REQUEST","The request does not satisfy the API contract.")
    Return ..Fail(503,"IRIS_OPERATION_FAILED","IRIS could not complete this operation. Inspect the native event log; no release is assumed.")
}

ClassMethod StrictJSON(value As %String) As %String [ Language = python ]
{
    import json, sys
    if '/opt/silentshift/python' not in sys.path:
        sys.path.insert(0, '/opt/silentshift/python')
    from silentshift.engine import strict_loads
    try:
        parsed = strict_loads(value)
    except (ValueError, TypeError, RecursionError):
        return ""
    if not isinstance(parsed, dict):
        return ""
    return json.dumps(parsed, allow_nan=False, separators=(",", ":"), sort_keys=True)
}

ClassMethod Body(Output raw As %String) As %DynamicObject
{
    If '$ISOBJECT(%request.Content) Throw ##class(%Exception.General).%New("INVALID_REQUEST")
    If %request.Content.Size > 131072 Throw ##class(%Exception.General).%New("INVALID_REQUEST")
    Do %request.Content.Rewind()
    Set raw = %request.Content.Read(131073)
    Set normalized = ..StrictJSON(raw)
    If normalized="" Throw ##class(%Exception.General).%New("INVALID_REQUEST")
    Return ##class(%DynamicObject).%FromJSON(normalized)
}

ClassMethod Dispatch(envelope As %DynamicObject) As %Status
{
    Try {
        Set sc = ##class(Ens.Director).CreateBusinessService("Partner",.service)
        $$$ThrowOnError(sc)
        Set input = ##class(%Stream.GlobalCharacter).%New()
        Do input.Write(envelope.%ToJSON())
        Set sc = service.ProcessInput(input,.result)
        $$$ThrowOnError(sc)
        Return ..JSON(result.BodyJSON)
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Ingest() As %Status
{
    Try {
        Set message = ..Body(.raw)
        // The public ingress accepts only partner message data. Reference,
        // clock, scenario and fault metadata cannot be supplied in an envelope.
        Set envelope = {"message": (message), "raw_payload": (raw)}
        Return ..Dispatch(envelope)
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Cases() As %Status
{
    Try {
        Set limit = $GET(%request.Data("limit",1),50), offset = $GET(%request.Data("offset",1),0)
        If (limit'?1.3N) || (limit<1) || (limit>100) || (offset'?1.9N) Return ..Fail(422,"INVALID_PAGINATION","Use limit 1–100 and a nonnegative offset.")
        Return ..JSON(##class(SilentShift.Store).ListCases(limit,offset))
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Case(id As %String) As %Status
{
    Try {
        Set result = ##class(SilentShift.Store).CaseJSON(id)
        If (result="") || (result="null") Return ..Fail(404,"NOT_FOUND","Investigation not found.")
        Return ..JSON(result)
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Overview() As %Status
{
    Try {
        Return ..JSON(##class(SilentShift.Store).OverviewJSON())
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod FixtureData() As %DynamicObject
{
    Set file = ##class(%Stream.FileCharacter).%New()
    Set sc = file.LinkToFile("/opt/silentshift/fixtures/v1/scenarios.json")
    $$$ThrowOnError(sc)
    Return ##class(%DynamicObject).%FromJSON(file)
}

ClassMethod Scenarios() As %Status
{
    Try {
        Set data = ..FixtureData(), items = []
        For i=0:1:data.scenarios.%Size()-1 {
            Set source=data.scenarios.%Get(i)
            Set item={"id":(source.id),"name":(source.name),"summary":(source.summary),"message":(source.message),"references":(source.references),"ground_truth":(source.%Get("ground_truth"))}
            Do items.%Push(item)
        }
        Set result={"version":(data.%Get("dataset_version")),"clock":(data.clock),"scenarios":(items),"synthetic":true}
        Return ..JSON(result.%ToJSON())
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod RunScenario(id As %String) As %Status
{
    Try {
        Set request=..Body(.raw), runId=request.%Get("run_id")
        If (request.%Size()'=1) || (runId'?36(1AN,1"-")) Return ..Fail(422,"INVALID_RUN_ID","Supply one UUID run_id; reuse it for a safe retry.")
        Set data=..FixtureData(), selected=""
        For i=0:1:data.scenarios.%Size()-1 {
            Set item=data.scenarios.%Get(i)
            If item.id=id Set selected=item
        }
        If '$ISOBJECT(selected) Return ..Fail(404,"NOT_FOUND","Scenario not found.")
        // A run is deliberately anchored to the frozen dataset clock. It is a
        // labeled replay, not a claim that a historic event arrived live today.
        Set message=selected.message
        Do message.%Set("event_id",message.%Get("event_id")_"-"_runId)
        Do message.%Set("correlation_id",runId)
        Set envelope={"message":(message),"raw_payload":(message.%ToJSON()),"scenario_id":(id),"dataset_version":(data.%Get("dataset_version")),"clock":(data.clock)}
        If id="unsafe-agent-output" {
            Do envelope.%Set("fault",selected.%Get("test_recommendation"))
        }
        Return ..Dispatch(envelope)
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Review(id As %String) As %Status
{
    If '$SYSTEM.Security.Check("SSReview","USE") Return ..Fail(403,"FORBIDDEN","SilentShift reviewer permission is required.")
    Try {
        Set request=..Body(.raw)
        Set action=$ZCONVERT(request.%Get("action"),"L")
        If (action'="approve") && (action'="reject") Return ..Fail(422,"INVALID_ACTION","Choose APPROVE or REJECT.")
        Do request.%Set("action",action)
        Set envelope={"action":"review","case_id":(id),"review":(request),"reviewer":($USERNAME)}
        Return ..Dispatch(envelope)
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Policies() As %Status
{
    Set rules=[]
    Do rules.%Push({"id":"NO_CRITICAL_CONTRADICTION","description":"Invalid messages and verified critical contradictions cannot be released, including by a reviewer."})
    Do rules.%Push({"id":"EVIDENCE_COMPLETE","description":"Every independent reference must be known and cited before release."})
    Do rules.%Push({"id":"SEMANTICS_RESOLVED","description":"Only a resolved comparison to an effective approved contract permits release."})
    Do rules.%Push({"id":"RECOMMENDATION_VALID","description":"Malformed JSON, unsupported actions and unknown evidence IDs fail safely."})
    Do rules.%Push({"id":"UNCERTAINTY_BOUNDED","description":"Uncertainty above 0.35 requires review."})
    Do rules.%Push({"id":"NOT_DUPLICATE","description":"A duplicate source/event key returns the existing case and never repeats delivery."})
    Do rules.%Push({"id":"REVIEW_AUTHORIZATION","description":"Review requires SSReview, a reason, current version and idempotency key."})
    Set result={"version":"silentshift-policy/1.1.0","rules":(rules),"automatic_transformations":false}
    Return ..JSON(result.%ToJSON())
}

ClassMethod Health() As %Status
{
    Try {
        Set sc=##class(Ens.Director).GetProductionStatus(.name,.state)
        $$$ThrowOnError(sc)
        Set running=(state=$$$eProductionStateRunning) && (name="SilentShift.Production")
        Set configured=($SYSTEM.Util.GetEnviron("SILENTSHIFT_LLM_API_KEY")'="") || ($SYSTEM.Util.GetEnviron("OPENAI_API_KEY")'="")
        Set production={"name":(name),"running":(running),"state_code":(state)}
        If name="" Do production.%Set("name","SilentShift.Production")
        Set agent={"configured":(configured),"last_success_at":null,"availability":"not_probed","model":($SYSTEM.Util.GetEnviron("SILENTSHIFT_MODEL"))}
        Do production.%Set("running",running,"boolean")
        Do agent.%Set("configured",configured,"boolean")
        Set lastSuccess=""
        &sql(SELECT MAX(RecordedAt) INTO :lastSuccess FROM SilentShift_Data.AuditEvent WHERE Kind = 'agent_returned')
        If SQLCODE<0 Throw ##class(%Exception.General).%New("APP_UNAVAILABLE")
        If lastSuccess'="" {
            Do agent.%Set("last_success_at",lastSuccess)
            Do agent.%Set("availability","previously_succeeded_not_probed_now")
        }
        Set components=[]
        // A running production does not prove each host or provider healthy.
        For host="Partner","Semantic","References","Investigator","Destination","Quarantine" Do components.%Push({"name":(host),"status":"not_probed"})
        Set permissions={}
        Do permissions.%Set("review",$SYSTEM.Security.Check("SSReview","USE"),"boolean")
        Set result={"build":($ZVERSION),"production":(production),"agent":(agent),"components":(components),"permissions":(permissions),"scope":"synthetic single-tenant contest demonstrator"}
        Return ..JSON(result.%ToJSON())
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Evaluations() As %Status
{
    Try {
        Set statement=##class(%SQL.Statement).%New()
        Set sc=statement.%Prepare("SELECT TOP 20 Body FROM SilentShift_Data.Evaluation ORDER BY CreatedAt DESC")
        $$$ThrowOnError(sc)
        Set rows=statement.%Execute(), items=[]
        While rows.%Next() {
            Do items.%Push(##class(%DynamicObject).%FromJSON(rows.%Get("Body")))
        }
        Set result={"items":(items),"limit":20}
        Return ..JSON(result.%ToJSON())
    } Catch error {
        Return ..ErrorResponse(error)
    }
}

ClassMethod Aggregate(artifactJSON As %String) As %String [ Language = python ]
{
    import json, sys
    if '/opt/silentshift/python' not in sys.path:
        sys.path.insert(0, '/opt/silentshift/python')
    from silentshift.engine import strict_loads
    from silentshift.evaluation import aggregate_native, load_dataset
    dataset = load_dataset('/opt/silentshift/fixtures/v1/scenarios.json')
    return json.dumps(aggregate_native(strict_loads(artifactJSON, max_bytes=2000000), dataset), allow_nan=False, separators=(',', ':'))
}

ClassMethod CaptureEvaluation() As %Status
{
    Set locked=0
    Try {
        Set request=..Body(.raw), runId=request.%Get("run_id"), ids=request.%Get("case_ids")
        If (request.%Size()'=2) || (runId'?36(1AN,1"-")) || '$ISOBJECT(ids) Return ..Fail(422,"INVALID_EVALUATION","Supply run_id and the five native case_ids.")
        If (ids.%ClassName(1)'="%Library.DynamicArray") || (ids.%Size()'=5) Return ..Fail(422,"INVALID_EVALUATION","A frozen evaluation requires five case IDs.")
        Set records=[],seen="|",verified=1
        Set data=..FixtureData()
        For i=0:1:ids.%Size()-1 {
            Set id=ids.%Get(i)
            If (id="") || (seen[("|"_id_"|")) Throw ##class(%Exception.General).%New("INVALID_EVALUATION")
            Set seen=seen_id_"|"
            Set record=##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            If record.message.%Get("correlation_id")'=runId Throw ##class(%Exception.General).%New("INVALID_EVALUATION")
            If record.%Get("dataset_version")'=data.%Get("dataset_version") Throw ##class(%Exception.General).%New("INVALID_EVALUATION")
            Set agent=record.%Get("agent"), trace=record.%Get("trace_id")
            If '$ISOBJECT(agent) Throw ##class(%Exception.General).%New("INVALID_EVALUATION")
            If (agent.%Get("mode")'="native-ai-hub") || (agent.%Get("status")'="returned") || (trace="") Set verified=0
            Set reads=agent.%Get("tool_reads")
            If '$ISOBJECT(reads) {
                Set verified=0
            } Else {
                For tool="message","contracts","related" If reads.%Get(tool)<1 Set verified=0
            }
            Do records.%Push(record)
        }
        Set artifact={"dataset_version":(data.%Get("dataset_version")),"iris_version":($ZVERSION),"production":"SilentShift.Production","records":(records)}
        Do artifact.%Set("native_verified",verified,"boolean")
        Set native=##class(%DynamicObject).%FromJSON(..Aggregate(artifact.%ToJSON()))
        Set canonicalIds=##class(SilentShift.Bridge).Canonical(ids.%ToJSON())
        Lock +^SilentShift.Lock("evaluation",runId):5
        If '$TEST Throw ##class(%Exception.General).%New("APP_UNAVAILABLE")
        Set locked=1,existing=##class(SilentShift.Data.Evaluation).%OpenId(runId)
        If $ISOBJECT(existing) {
            If existing.CaseIds'=canonicalIds Throw ##class(%Exception.General).%New("APP_CONFLICT")
            Set result=existing.Body
        } Else {
            Set created=##class(SilentShift.Bridge).Now()
            Set body={"id":(runId),"created_at":(created),"dataset_version":(data.%Get("dataset_version")),"case_ids":(ids),"native":(native)}
            Set entry=##class(SilentShift.Data.Evaluation).%New()
            Set entry.RunId=runId,entry.CreatedAt=created,entry.CaseIds=canonicalIds,entry.Body=body.%ToJSON()
            Set sc=entry.%Save()
            $$$ThrowOnError(sc)
            Set result=entry.Body
        }
        Lock -^SilentShift.Lock("evaluation",runId)
        Set locked=0
        Return ..JSON(result)
    } Catch error {
        If locked Lock -^SilentShift.Lock("evaluation",runId)
        Return ..ErrorResponse(error)
    }
}

}
