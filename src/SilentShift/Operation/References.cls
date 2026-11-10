Class SilentShift.Operation.References Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Resolve(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set sc = ##class(SilentShift.Store).SnapshotReferences(request.CaseId)
    If $$$ISOK(sc) Set response.BodyJSON = ##class(SilentShift.Store).SummaryJSON(request.CaseId)
    Return sc
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Resolve</Method></MapItem></MapItems>
}
}
