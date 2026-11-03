Include (%occStatus, %outUnitTest)

/// Native trace inspection and regression checks. Never calls an LLM directly.
Class SilentShift.Test.TraceChecks Extends %UnitTest.TestCase
{
Method TestTypedMetadata()
{
    Set event = ##class(SilentShift.TraceEvent).%New()
    Set event.CaseId = "synthetic-test", event.SpanId = "synthetic-span"
    Set event.EventKind = "invocation_skipped", event.SpanKind = "investigation_preflight"
    Set data = ##class(%DynamicObject).%FromJSON(event.AsJSON())
    Do $$$AssertEquals(data.%Get("usage_scope"), "final_response_only")
    Do $$$AssertEquals(data.%GetTypeOf("session_totals"), "null")
    Do $$$AssertEquals(data.%GetTypeOf("provider_round_usage"), "null")
    Do $$$AssertEquals(data.%GetTypeOf("provider_retry_count"), "null")
    Do $$$AssertEquals(data.%GetTypeOf("billing_cost"), "null")
    Do $$$AssertTrue('data.%Get("content_retained"))
}

ClassMethod LocalRouteSafe() As %Boolean
{
    Set url = $SYSTEM.Util.GetEnviron("SILENTSHIFT_LLM_BASE_URL")
    Set local = (url = "http://localhost:11434/v1/") || (url = "http://127.0.0.1:11434/v1/") || (url = "http://host.lima.internal:11434/v1/") || (url = "http://host.docker.internal:11434/v1/") || (url = "http://ollama:11434/v1/")
    Return local && ($ZCONVERT($SYSTEM.Util.GetEnviron("SILENTSHIFT_MODEL"), "L") [ "qwen3")
}

/// Redacted export from real native headers and their typed persistent bodies.
ClassMethod InspectCase(id As %String) As %String
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Set agent = body.%Get("agent"), policy = body.%Get("policy"), headers = [], spans = []
    Set summary = {"model": (agent.%Get("model")), "status": (agent.%Get("status")), "failure_code": (agent.%Get("failure_code")), "failure_stage": (agent.%Get("failure_stage")), "prompt_version": (agent.%Get("prompt_version")), "trace": (agent.%Get("trace")), "response_usage": (agent.%Get("response_usage")), "usage_scope": (agent.%Get("usage_scope")), "tool_reads": (agent.%Get("tool_reads"))}
    Do summary.%Set("model_invoked", agent.%Get("model_invoked", 0), "boolean")
    Set result = {"case_id": (id), "scenario_id": (body.%Get("scenario_id")), "trace_id": (body.%Get("trace_id")), "routing": (body.%Get("routing")), "delivery_count": (body.%Get("delivery_count")), "policy_decision": (policy.%Get("decision")), "agent": (summary), "native_headers": (headers), "trace_payloads": (spans)}
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT TOP 100 ID,SessionId,SourceConfigName,TargetConfigName,MessageBodyClassName,MessageBodyId,TimeCreated,TimeProcessed FROM Ens.MessageHeader WHERE SessionId = ? ORDER BY ID")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(+body.%Get("trace_id"))
    If rows.%SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Trace header read failed"))
    While rows.%Next() {
        Set header = {"id": (rows.%Get("ID")), "session_id": (rows.%Get("SessionId")), "source": (rows.%Get("SourceConfigName")), "target": (rows.%Get("TargetConfigName")), "body_class": (rows.%Get("MessageBodyClassName")), "body_id": (rows.%Get("MessageBodyId")), "created_at": (rows.%Get("TimeCreated")), "processed_at": (rows.%Get("TimeProcessed"))}
        Do headers.%Push(header)
        If rows.%Get("MessageBodyClassName") = "SilentShift.TraceEvent" {
            Set event = ##class(SilentShift.TraceEvent).%OpenId(rows.%Get("MessageBodyId"))
            If '$ISOBJECT(event) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Trace body is unavailable"))
            Set payload = ##class(%DynamicObject).%FromJSON(event.AsJSON())
            Do payload.%Set("message_header_id", rows.%Get("ID"))
            Do spans.%Push(payload)
        }
    }
    Set audits = [], events = body.%Get("events")
    For index = 0:1:events.%Size()-1 {
        Set item = events.%Get(index)
        If item.%Get("kind") = "ai_trace_event" Do audits.%Push(item.%Get("detail"))
    }
    Do result.%Set("trace_audits", audits)
    Do result.%Set("trace_audit_count", audits.%Size())
    Return result.%ToJSON()
}

/// Third isolated case exercises the pre-model failure trace with no inference.
ClassMethod RunBudgetCase(Output id As %String) As %Status
{
    Set id = "", guarded = 0, limits = 0
    For offset = 0:1:160 {
        Set line = $TEXT(Run+offset^SilentShift.AI.Investigator.1)
        If line [ "EVIDENCE_REFERENCE_LIMIT" Set guarded = 1
        If (line [ "approvedCount > 10") && (line [ "peerCount > 10") Set limits = 1
        If line [ "%AI.Provider" Quit
    }
    If 'guarded || 'limits Return $$$ERROR($$$GeneralError, "Compiled evidence budget guard is required")
    Set uuid = $TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")
    Set scope = "trace-budget-"_uuid, contractId = "SYNTHETIC:TRACE:"_uuid
    Set now = ##class(SilentShift.TraceEvent).UTC()
    For index = 1:1:11 {
        Set referenceId = "synthetic:trace:"_uuid_":"_index
        Set reference = {"id": (referenceId), "contract_id": (contractId), "authority": "approved", "effective_from": "2026-01-01T00:00:00Z", "effective_to": null, "business_unit": "SYNTHETIC", "product_id": "SYNTHETIC", "quantity": "20", "unit": "EA", "timestamp_semantics": "event_time", "synthetic": true}
        Set record = ##class(SilentShift.Data.Reference).%New()
        Set record.ReferenceKey = ##class(SilentShift.Bridge).PairHash(scope, referenceId), record.ReferenceId = referenceId
        Set record.ScenarioScope = scope, record.ContractId = contractId, record.Body = reference.%ToJSON()
        Set sc = record.%Save()
        $$$ThrowOnError(sc)
    }
    Set message = {"event_id": (uuid), "correlation_id": (uuid), "source": "silentshift-native-trace-test", "kind": "order", "occurred_at": (now), "contract_id": (contractId), "business_unit": "SYNTHETIC", "product_id": "SYNTHETIC", "quantity": "20", "unit": "EA", "notes": "Synthetic trace budget regression; model must not be called."}
    Set envelope = {"message": (message), "raw_payload": (message.%ToJSON()), "scenario_id": (scope), "dataset_version": "silentshift-trace/1", "clock": (now)}
    Set stream = ##class(%Stream.GlobalCharacter).%New(), sc = stream.Write(envelope.%ToJSON())
    $$$ThrowOnError(sc)
    Set sc = ##class(Ens.Director).CreateBusinessService("Partner", .service)
    $$$ThrowOnError(sc)
    Set sc = service.ProcessInput(stream, .reply)
    $$$ThrowOnError(sc)
    Set result = ##class(%DynamicObject).%FromJSON(reply.BodyJSON), id = result.%Get("id")
    Return $$$OK
}
}
