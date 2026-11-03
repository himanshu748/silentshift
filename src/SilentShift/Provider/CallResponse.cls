/// The actual forwarding outcome; always returned with an OK framework status.
Class SilentShift.Provider.CallResponse Extends Ens.Response
{
Property CallId As %String(MAXLEN = 80);
Property CaseId As %String(MAXLEN = 80);
Property ProductionSessionId As %Integer;
Property InvocationSpanId As %String(MAXLEN = 80);
Property Round As %Integer;
Property Model As %String(MAXLEN = 160);
Property PromptVersion As %String(MAXLEN = 80);
Property StartedAt As %String(MAXLEN = 40);
Property FinishedAt As %String(MAXLEN = 40);
Property DurationMS As %Integer;
Property HTTPStatus As %Integer;
Property UpstreamHTTPStatus As %Integer;
Property ResponseBytes As %Integer;
Property ErrorCode As %String(MAXLEN = 64);
Property ToolCallsJSON As %String(MAXLEN = 4096);
Property FinishReason As %String(MAXLEN = 32);
Property PromptTokens As %Integer;
Property CompletionTokens As %Integer;
Property TotalTokens As %Integer;

Method AsJSON() As %String
{
    Set calls = [], usage = {}, upstream = ""
    If ..ToolCallsJSON '= "" Set calls = ##class(%DynamicArray).%FromJSON(..ToolCallsJSON)
    Set item = {"trace_schema":"silentshift-provider-call/1","granularity":"provider_http_call","event_kind":"provider_response","call_id":(..CallId),"case_id":(..CaseId),"production_session_id":(..ProductionSessionId),"invocation_span_id":(..InvocationSpanId),"round":(..Round),"model":(..Model),"prompt_version":(..PromptVersion),"started_at":(..StartedAt),"finished_at":(..FinishedAt),"duration_ms":(..DurationMS),"http_status":(..HTTPStatus),"upstream_http_status":null,"response_bytes":(..ResponseBytes),"error_code":(..ErrorCode),"tool_calls":(calls),"finish_reason":(..FinishReason),"application_retry_count":0,"provider_retry_count":null,"fallback_used":false,"content_retained":false,"billing_cost":null,"usage_scope":"actual_http_response_only","response_usage":null}
    If ..UpstreamHTTPStatus '= "" Do item.%Set("upstream_http_status", ..UpstreamHTTPStatus, "number")
    If ..PromptTokens '= "" Do usage.%Set("prompt_tokens", ..PromptTokens, "number")
    If ..CompletionTokens '= "" Do usage.%Set("completion_tokens", ..CompletionTokens, "number")
    If ..TotalTokens '= "" Do usage.%Set("total_tokens", ..TotalTokens, "number")
    If usage.%Size() Do item.%Set("response_usage", usage)
    Return item.%ToJSON()
}
}
