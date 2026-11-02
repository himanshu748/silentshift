Class SilentShift.Operation.Destination Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Deliver(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set sc = ##class(SilentShift.Store).Deliver(request.CaseId)
    If $$$ISOK(sc) Set response.BodyJSON = ##class(SilentShift.Store).CaseJSON(request.CaseId)
    Return sc
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Deliver</Method></MapItem></MapItems>
}
}
