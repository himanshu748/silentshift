Include %occStatus

Class SilentShift.Operation.Investigation Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Property TraceCaseId As %String;
Property TraceInvocationId As %String;
Property TraceModel As %String;
Property TraceRunStarted As %String;
Property TraceChatStarted As %String;
Property TraceBuffer As %DynamicArray;
Property TraceEnqueued As %Integer;
Property TraceEnqueueFailures As %Integer;
Property TraceCaptureFailures As %Integer;

Method Investigate(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Do ..ResetObservation(request.CaseId)
    Set item = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId))
    // A queued investigation can outlive the caller's bounded wait. Never
    // begin fresh model work for a case the process has already contained.
    If item.%Get("routing") '= "PROCESSING" {
        Set metadata = {"mode": "native-ai-hub", "status": "failed", "failure_code": "CASE_NO_LONGER_PROCESSING"}
        Do metadata.%Set("model_invoked", 0, "boolean")
        Do ..FinishObservation(metadata)
        Set response.MetadataJSON = metadata.%ToJSON()
        Set ignored = ##class(SilentShift.Store).AddEvent(request.CaseId, "agent_request_expired", metadata.%ToJSON())
        Return $$$OK
    }
    Set assessment = item.%Get("assessment")
    Set sc = ##class(SilentShift.AI.Investigator).Run(request.CaseId, assessment.%ToJSON(), .raw, .metadataJSON, $THIS)
    Set response.RecommendationJSON = raw, response.MetadataJSON = metadataJSON
    // An unavailable agent is a business outcome, not an automatic retry. The
    // process applies fail-closed policy to an empty proposal and holds the case.
    If $$$ISERR(sc) {
        Set metadata = {"mode": "native-ai-hub", "status": "failed", "failure_code": "AI_INVESTIGATION_FAILED"}
        If metadataJSON '= "" Set metadata = ##class(%DynamicObject).%FromJSON(metadataJSON)
        If 'metadata.%IsDefined("failure_code") Do metadata.%Set("failure_code", "AI_INVESTIGATION_FAILED")
        Set response.MetadataJSON = metadata.%ToJSON(), response.RecommendationJSON = ""
    }
    Set metadata = ##class(%DynamicObject).%FromJSON(response.MetadataJSON)
    If 'metadata.%IsDefined("elapsed_ms") Do metadata.%Set("elapsed_ms", ##class(SilentShift.TraceEvent).ElapsedMS(..TraceRunStarted), "number")
    Do ..FinishObservation(metadata)
    Set response.MetadataJSON = metadata.%ToJSON()
    Set detail = {"status": (metadata.%Get("status")), "failure_stage": (metadata.%Get("failure_stage")), "model": (metadata.%Get("model")), "tool_reads": (metadata.%Get("tool_reads"))}
    Set ignored = ##class(SilentShift.Store).AddEvent(request.CaseId, "agent_operation_finished", detail.%ToJSON())
    Return $$$OK
}

Method ResetObservation(caseId As %String) [ Private ]
{
    Set ..TraceCaseId = caseId, ..TraceInvocationId = $TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")
    Set ..TraceRunStarted = $ZTIMESTAMP, ..TraceChatStarted = "", ..TraceBuffer = []
    Set ..TraceModel = $EXTRACT($SYSTEM.Util.GetEnviron("SILENTSHIFT_MODEL"), 1, 160)
    If ..TraceModel = "" Set ..TraceModel = "qwen3-silentshift:4b-instruct"
    Set ..TraceEnqueued = 0, ..TraceEnqueueFailures = 0, ..TraceCaptureFailures = 0
}

/// Called before Chat, outside native callbacks. SendRequestAsync preserves the
/// current interoperability SessionId; a missing end then remains inspectable.
Method BeginChat(model As %String, started As %String)
{
    Set ..TraceChatStarted = started, ..TraceModel = model
    Set event = ..NewTrace("invocation_started", "agent_invocation", ..TraceInvocationId)
    Set event.ModelInvoked = (event.ExecutionMode = "live"), event.Status = "started"
    Set event.StartedAt = ##class(SilentShift.TraceEvent).UTC(started)
    Do ..EnqueueTrace(event)
}

/// Server-bound tool observer. Native callbacks only append bounded metadata;
/// production dispatch is deferred until Chat exits. No tool text is retained.
Method CaptureTool(caseId As %String, eventKind As %String, toolName As %String, spanId As %String, started As %String, finished As %String = "", records As %Integer = 0, truncated As %Boolean = 0, failureCode As %String = "")
{
    Try {
        If (caseId '= ..TraceCaseId) || '$ISOBJECT(..TraceBuffer) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Trace scope mismatch"))
        If (toolName '= "GetCurrentMessage") && (toolName '= "GetApprovedContracts") && (toolName '= "GetRelatedRecords") && (toolName '= "find_similar_precedents") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Trace tool is not allowed"))
        If ..TraceBuffer.%Size() >= 24 {
            Set ..TraceCaptureFailures = ..TraceCaptureFailures + 1
            Return
        }
        Set item = {"event_kind": (eventKind), "tool_name": (toolName), "span_id": (spanId), "started": (started), "finished": (finished), "records": (records), "truncated": false, "failure_code": (failureCode)}
        Do item.%Set("truncated", truncated, "boolean")
        Do ..TraceBuffer.%Push(item)
    } Catch error {
        Set ..TraceCaptureFailures = ..TraceCaptureFailures + 1
    }
}

Method NewTrace(eventKind As %String, spanKind As %String, spanId As %String) As SilentShift.TraceEvent [ Private ]
{
    Set event = ##class(SilentShift.TraceEvent).%New()
    Set event.CaseId = ..TraceCaseId, event.ProductionSessionId = ..%SessionId
    Set event.EventKind = eventKind, event.SpanKind = spanKind, event.SpanId = spanId
    Set event.ExecutionMode = ##class(SilentShift.Provider.Lease).ExecutionMode()
    Set event.Model = ..TraceModel, event.PromptVersion = ##class(SilentShift.AI.Investigator).#PROMPTVERSION
    Return event
}

Method EnqueueTrace(event As SilentShift.TraceEvent) [ Private ]
{
    Try {
        If $LENGTH($ZCONVERT(event.AsJSON(), "O", "UTF8")) > 8192 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Trace metadata too large"))
        Set sc = ..SendRequestAsync("AITrace", event, event.EventKind_" "_event.ToolName)
        $$$ThrowOnError(sc)
        Set ..TraceEnqueued = ..TraceEnqueued + 1
    } Catch error {
        Set ..TraceEnqueueFailures = ..TraceEnqueueFailures + 1
    }
}

Method FinishObservation(metadata As %DynamicObject) [ Private ]
{
    Set ..TraceCaptureFailures = ..TraceCaptureFailures + metadata.%Get("tool_trace_capture_failures", 0)
    For index = 0:1:..TraceBuffer.%Size()-1 {
        Set item = ..TraceBuffer.%Get(index)
        Set event = ..NewTrace(item.%Get("event_kind"), "tool", item.%Get("span_id"))
        Set event.ParentSpanId = ..TraceInvocationId, event.ModelInvoked = (event.ExecutionMode = "live"), event.Buffered = 1
        Set event.ToolName = item.%Get("tool_name"), event.StartedAt = ##class(SilentShift.TraceEvent).UTC(item.%Get("started"))
        Set event.Status = "started", event.EvidenceTruncated = item.%Get("truncated")
        Set event.FailureCode = item.%Get("failure_code")
        If item.%Get("finished") '= "" {
            Set event.FinishedAt = ##class(SilentShift.TraceEvent).UTC(item.%Get("finished"))
            Set event.DurationMS = ##class(SilentShift.TraceEvent).ElapsedMS(item.%Get("started"), item.%Get("finished"))
            Set event.RecordCount = item.%Get("records")
            Set event.Status = $SELECT(event.EventKind = "tool_failed": "failed", event.EvidenceTruncated: "incomplete", 1: "completed")
        }
        Do ..EnqueueTrace(event)
    }
    Set invoked = metadata.%Get("native_chat_invoked", metadata.%Get("model_invoked", 0))
    Set returned = metadata.%Get("native_chat_returned", 0)
    Set kind = $SELECT('invoked: "invocation_skipped", returned: "invocation_completed", 1: "invocation_failed")
    Set event = ..NewTrace(kind, $SELECT(invoked: "agent_invocation", 1: "investigation_preflight"), ..TraceInvocationId)
    Set event.ModelInvoked = metadata.%Get("model_invoked", 0), event.NativeChatReturned = returned
    Set event.Status = $SELECT('invoked: "skipped", 1: metadata.%Get("status", "failed"))
    Set started = $SELECT(invoked: ..TraceChatStarted, 1: ..TraceRunStarted)
    Set event.StartedAt = ##class(SilentShift.TraceEvent).UTC(started)
    Set event.FinishedAt = metadata.%Get("chat_finished_at", ##class(SilentShift.TraceEvent).UTC())
    Set event.DurationMS = metadata.%Get("chat_elapsed_ms", ##class(SilentShift.TraceEvent).ElapsedMS(started))
    Set event.FailureCode = metadata.%Get("failure_code"), event.FailureStage = metadata.%Get("failure_stage")
    Set usage = metadata.%Get("response_usage")
    If $ISOBJECT(usage) {
        If usage.%GetTypeOf("prompt_tokens") = "number" Set event.FinalPromptTokens = usage.%Get("prompt_tokens")
        If usage.%GetTypeOf("completion_tokens") = "number" Set event.FinalCompletionTokens = usage.%Get("completion_tokens")
        If usage.%GetTypeOf("total_tokens") = "number" Set event.FinalTotalTokens = usage.%Get("total_tokens")
    }
    If $ISOBJECT(metadata.%Get("evidence_budget")) Set event.EvidenceBudgetJSON = metadata.%Get("evidence_budget").%ToJSON()
    Do ..EnqueueTrace(event)
    Set trace = {"mode": "native-interoperability", "granularity": "agent_invocation_and_tool", "invocation_id": (..TraceInvocationId), "prompt_version": (event.PromptVersion), "enqueued_events": (..TraceEnqueued), "enqueue_failures": (..TraceEnqueueFailures), "capture_failures": (..TraceCaptureFailures), "persistence_status": "async_unverified", "sdk_provider_round_metadata_available": false, "provider_http_trace_available": true}
    Do metadata.%Set("trace", trace)
    Do metadata.%Set("usage_scope", $SELECT(event.ExecutionMode = "recorded-replay":"unavailable_for_replay",1:"final_response_only"))
    Do metadata.%Set("session_totals", "", "null")
    Do metadata.%Set("provider_round_usage", "", "null")
    Do metadata.%Set("provider_retry_count", "", "null")
    Do metadata.%Set("application_retry_count", 0, "number")
    Do metadata.%Set("fallback_used", 0, "boolean")
    If (..TraceEnqueueFailures + ..TraceCaptureFailures) > 0 {
        Set ignored = ##class(SilentShift.Store).AddEvent(..TraceCaseId, "ai_trace_incomplete", trace.%ToJSON())
    }
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Investigate</Method></MapItem></MapItems>
}
}
