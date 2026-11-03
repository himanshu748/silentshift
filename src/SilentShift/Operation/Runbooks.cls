Include %occStatus

Class SilentShift.Operation.Runbooks Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Retrieve(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId))
    If body.%Get("routing") '= "PROCESSING" Return $$$OK
    Try {
        Set query = ##class(SilentShift.Runbooks).QueryForCase(body)
        Set context = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Runbooks).Search(query))
    } Catch unavailable {
        // Procedures supplement the investigation. They cannot replace a
        // missing contract or turn a policy veto into permission to release.
        Set context = {"status": "unavailable", "implementation": "IRIS VECTOR_COSINE", "matches": [], "decision_authority": false, "failure_code": "RUNBOOK_RETRIEVAL_UNAVAILABLE"}
    }
    // Return data only. If this operation finishes after the caller's bounded
    // wait, it cannot race policy persistence or change the case's version.
    Set response.BodyJSON = context.%ToJSON()
    Return $$$OK
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Retrieve</Method></MapItem></MapItems>
}
}
