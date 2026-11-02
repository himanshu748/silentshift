Class SilentShift.Operation.Investigation Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Investigate(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set item = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId))
    Set assessment = item.%Get("assessment")
    Set sc = ##class(SilentShift.AI.Investigator).Run(request.CaseId, assessment.%ToJSON(), .raw, .metadataJSON)
    Set response.RecommendationJSON = raw, response.MetadataJSON = metadataJSON
    // An unavailable agent is a business outcome, not an automatic retry. The
    // process applies fail-closed policy to an empty proposal and holds the case.
    If $$$ISERR(sc) {
        Set metadata = {"mode": "native-ai-hub", "status": "failed", "failure_code": "AI_INVESTIGATION_FAILED"}
        If metadataJSON '= "" Set metadata = ##class(%DynamicObject).%FromJSON(metadataJSON)
        Do metadata.%Set("failure_code", "AI_INVESTIGATION_FAILED")
        Set response.MetadataJSON = metadata.%ToJSON(), response.RecommendationJSON = ""
    }
    Return $$$OK
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Investigate</Method></MapItem></MapItems>
}
}
