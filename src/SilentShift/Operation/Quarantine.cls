Class SilentShift.Operation.Quarantine Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Hold(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set sc = ##class(SilentShift.Store).Hold(request.CaseId)
    If $$$ISOK(sc) Set response.BodyJSON = ##class(SilentShift.Store).SummaryJSON(request.CaseId)
    Return sc
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Hold</Method></MapItem></MapItems>
}
}
