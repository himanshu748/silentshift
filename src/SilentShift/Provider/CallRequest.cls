/// One real HTTP request. Raw bytes and authorization never enter this body.
Class SilentShift.Provider.CallRequest Extends Ens.Request
{
Property CallId As %String(MAXLEN = 80) [ Required ];
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property ProductionSessionId As %Integer;
Property InvocationSpanId As %String(MAXLEN = 80);
Property Round As %Integer;
Property Model As %String(MAXLEN = 160);
Property PromptVersion As %String(MAXLEN = 80);
Property Provider As %String(MAXLEN = 80) [ InitialExpression = "ollama/openai-compatible" ];
Property ExecutionMode As %String(MAXLEN = 32) [ InitialExpression = "live" ];
Property ReplayRecordId As %String(MAXLEN = 80);
Property ApplicationRetryCount As %Integer [ InitialExpression = 0 ];
Property ProviderRetryCount As %Integer;
Property FallbackUsed As %Boolean [ InitialExpression = 0 ];
Property BillingCost As %Numeric;
Property CostStatus As %String(MAXLEN = 32) [ InitialExpression = "unavailable" ];
Property StartedAt As %String(MAXLEN = 40);
Property RequestBytes As %Integer;
Property ToolNamesJSON As %String(MAXLEN = 512);

Method AsJSON() As %String
{
    Set tools = []
    If ..ToolNamesJSON '= "" Set tools = ##class(%DynamicArray).%FromJSON(..ToolNamesJSON)
    Set item = {"trace_schema":"silentshift-provider-call/1","granularity":"provider_http_call","event_kind":"provider_request","call_id":(..CallId),"case_id":(..CaseId),"production_session_id":(..ProductionSessionId),"invocation_span_id":(..InvocationSpanId),"round":(..Round),"model":(..Model),"prompt_version":(..PromptVersion),"started_at":(..StartedAt),"request_bytes":(..RequestBytes),"tool_names":(tools),"application_retry_count":0,"provider_retry_count":null,"fallback_used":false,"content_retained":false,"payload_storage":"IRISTEMP_nonjournaled_until_relay_completion","billing_cost":null,"usage_scope":"actual_http_response_only"}
    Do item.%Set("provider", ..Provider)
    Do item.%Set("execution_mode", ..ExecutionMode)
    Do item.%Set("replay_record_id", ..ReplayRecordId)
    If ..ExecutionMode = "recorded-replay" {
        Do item.%Set("granularity", "recorded_provider_response")
        Do item.%Set("usage_scope", "unavailable_for_replay")
        Do item.%Set("replay_scope", "Recorded assistant content; reconstructed tool/envelope messages; no upstream inference")
    }
    Return item.%ToJSON()
}
}
