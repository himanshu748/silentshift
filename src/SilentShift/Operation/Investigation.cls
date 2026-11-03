Class SilentShift.Operation.Investigation Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Investigate(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set item = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId))
    // A queued investigation can outlive the caller's bounded wait. Never
    // begin fresh model work for a case the process has already contained.
    If item.%Get("routing") '= "PROCESSING" {
        Set metadata = {"mode": "native-ai-hub", "status": "failed", "failure_code": "CASE_NO_LONGER_PROCESSING"}
        Set response.MetadataJSON = metadata.%ToJSON()
        Set ignored = ##class(SilentShift.Store).AddEvent(request.CaseId, "agent_request_expired", metadata.%ToJSON())
        Return $$$OK
    }
    Set assessment = item.%Get("assessment")
    Set sc = ##class(SilentShift.AI.Investigator).Run(request.CaseId, assessment.%ToJSON(), .raw, .metadataJSON)
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
    Set detail = {"status": (metadata.%Get("status")), "failure_stage": (metadata.%Get("failure_stage")), "model": (metadata.%Get("model")), "tool_reads": (metadata.%Get("tool_reads"))}
    Set ignored = ##class(SilentShift.Store).AddEvent(request.CaseId, "agent_operation_finished", detail.%ToJSON())
    Return $$$OK
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Investigate</Method></MapItem></MapItems>
}
}
