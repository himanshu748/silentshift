Include %occStatus

/// Embedding/vector SQL stay outside agent callbacks. This host returns
/// evidence only; Semantic alone persists the case context.
Class SilentShift.Operation.Precedents Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Execute(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    If request.Action = "index_precedent" {
        Set sc = ##class(SilentShift.Precedents).IndexResolvedCase(request.CaseId,.report)
        If $$$ISERR(sc) Set report = {"status":"unavailable","case_id":(request.CaseId),"failure_code":"PRECEDENT_INDEX_UNAVAILABLE","decision_authority":false}.%ToJSON()
        Set response.BodyJSON = report, response.MetadataJSON = report
        Return $$$OK
    }
    Try {
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId))
        If body.%Get("routing") '= "PROCESSING" Return $$$OK
        Set response.BodyJSON = ##class(SilentShift.Precedents).SearchForCase(body)
    } Catch unavailable {
        Set response.BodyJSON = ##class(SilentShift.Precedents).Unavailable(request.CaseId)
    }
    Return $$$OK
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Execute</Method></MapItem></MapItems>
}
}
