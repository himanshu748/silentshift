Include %occStatus

/// Observability only. This host cannot route, invoke a model, or read evidence.
Class SilentShift.Operation.AITrace Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";

Method Record(request As SilentShift.TraceEvent, Output response As Ens.Response) As %Status
{
    Set response = ##class(Ens.Response).%New()
    Try {
        If (request.ProductionSessionId '= ..%SessionId) || (request.CaseId = "") Return $$$ERROR($$$GeneralError, "AI trace association is invalid")
        Set detail = ##class(%DynamicObject).%FromJSON(request.AsJSON())
        Do detail.%Set("message_header_id", ..%RequestHeader.%Id())
        Do detail.%Set("source_config", ..%RequestHeader.SourceConfigName)
        Do detail.%Set("target_config", ..%RequestHeader.TargetConfigName)
        Do detail.%Set("recorded_at", ##class(SilentShift.TraceEvent).UTC())
        Set encoded = detail.%ToJSON()
        If $LENGTH($ZCONVERT(encoded, "O", "UTF8")) > 8192 Return $$$ERROR($$$GeneralError, "AI trace exceeds metadata limit")
        Return ##class(SilentShift.Store).AddEvent(request.CaseId, "ai_trace_event", encoded)
    } Catch error {
        Return $$$ERROR($$$GeneralError, "AI trace metadata could not be recorded")
    }
}

XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.TraceEvent"><Method>Record</Method></MapItem></MapItems>
}
}
