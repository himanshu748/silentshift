/// Bounded observability message. Contains metadata, never prompts/tool output.
/// Usage is the final response only; internal provider rounds remain unknown.
Class SilentShift.TraceEvent Extends Ens.Request
{
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property ProductionSessionId As %Integer;
Property EventKind As %String(MAXLEN = 40) [ Required ];
Property SpanKind As %String(MAXLEN = 40) [ Required ];
Property SpanId As %String(MAXLEN = 80) [ Required ];
Property ParentSpanId As %String(MAXLEN = 80);
Property Model As %String(MAXLEN = 160);
Property ExecutionMode As %String(MAXLEN = 32) [ InitialExpression = "live" ];
Property PromptVersion As %String(MAXLEN = 80);
Property Attempt As %Integer [ InitialExpression = 1 ];
Property ApplicationRetryCount As %Integer [ InitialExpression = 0 ];
Property FallbackUsed As %Boolean [ InitialExpression = 0 ];
Property ModelInvoked As %Boolean [ InitialExpression = 0 ];
Property NativeChatReturned As %Boolean [ InitialExpression = 0 ];
Property Status As %String(MAXLEN = 32);
Property StartedAt As %String(MAXLEN = 40);
Property FinishedAt As %String(MAXLEN = 40);
Property DurationMS As %Integer;
Property FinalPromptTokens As %Integer;
Property FinalCompletionTokens As %Integer;
Property FinalTotalTokens As %Integer;
Property ToolName As %String(MAXLEN = 80);
Property RecordCount As %Integer;
Property EvidenceTruncated As %Boolean [ InitialExpression = 0 ];
Property FailureCode As %String(MAXLEN = 80);
Property FailureStage As %String(MAXLEN = 80);
Property Buffered As %Boolean [ InitialExpression = 0 ];
Property EvidenceBudgetJSON As %String(MAXLEN = 512);

Method AsJSON() As %String
{
    Set item = {"trace_schema": "silentshift-ai-trace/1", "granularity": "agent_invocation_and_tool", "case_id": (..CaseId), "production_session_id": (..ProductionSessionId), "event_kind": (..EventKind), "span_kind": (..SpanKind), "span_id": (..SpanId), "parent_span_id": (..ParentSpanId), "model": (..Model), "prompt_version": (..PromptVersion), "attempt": (..Attempt), "application_retry_count": (..ApplicationRetryCount), "provider_retry_count": null, "fallback_used": false, "model_invoked": false, "native_chat_returned": false, "status": (..Status), "started_at": (..StartedAt), "finished_at": (..FinishedAt), "duration_ms": null, "usage_scope": "final_response_only", "final_response_usage": null, "session_totals": null, "provider_round_usage": null, "provider_round_count": null, "billing_cost": null, "cost_status": "unavailable", "tool_name": (..ToolName), "record_count": null, "evidence_truncated": false, "failure_code": (..FailureCode), "failure_stage": (..FailureStage), "buffered_until_chat_exit": false, "content_retained": false}
    Do item.%Set("execution_mode", ..ExecutionMode)
    If ..ExecutionMode = "recorded-replay" Do item.%Set("usage_scope", "unavailable_for_replay")
    Do item.%Set("fallback_used", ..FallbackUsed, "boolean")
    Do item.%Set("model_invoked", ..ModelInvoked, "boolean")
    Do item.%Set("native_chat_returned", ..NativeChatReturned, "boolean")
    Do item.%Set("evidence_truncated", ..EvidenceTruncated, "boolean")
    Do item.%Set("buffered_until_chat_exit", ..Buffered, "boolean")
    If ..DurationMS '= "" Do item.%Set("duration_ms", ..DurationMS, "number")
    If ..RecordCount '= "" Do item.%Set("record_count", ..RecordCount, "number")
    Set usage = {}
    If ..FinalPromptTokens '= "" Do usage.%Set("prompt_tokens", ..FinalPromptTokens, "number")
    If ..FinalCompletionTokens '= "" Do usage.%Set("completion_tokens", ..FinalCompletionTokens, "number")
    If ..FinalTotalTokens '= "" Do usage.%Set("total_tokens", ..FinalTotalTokens, "number")
    If usage.%Size() > 0 Do item.%Set("final_response_usage", usage)
    If ..EvidenceBudgetJSON '= "" Do item.%Set("evidence_budget", ##class(%DynamicObject).%FromJSON(..EvidenceBudgetJSON))
    Return item.%ToJSON()
}

/// Native helpers are also safe inside an agent callback; no language re-entry.
ClassMethod UTC(stamp As %String = "") As %String
{
    If stamp = "" Set stamp = $ZTIMESTAMP
    Return $TRANSLATE($ZDATETIME(stamp, 3, 1, 6), " ", "T")_"Z"
}

ClassMethod ElapsedMS(started As %String, finished As %String = "") As %String
{
    If started = "" Return ""
    If finished = "" Set finished = $ZTIMESTAMP
    Set seconds = (($PIECE(finished, ",", 1) - $PIECE(started, ",", 1)) * 86400) + $PIECE(finished, ",", 2) - $PIECE(started, ",", 2)
    If seconds < 0 Return ""
    Return $JUSTIFY(seconds * 1000, 0, 0) + 0
}
}
