Include Ensemble

Class SilentShift.Operation.Quarantine Extends Ens.BusinessOperation
{
Parameter INVOCATION = "Queue";
Method Hold(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set sc = ##class(SilentShift.Store).Hold(request.CaseId)
    If $$$ISOK(sc) Set response.BodyJSON = ##class(SilentShift.Store).SummaryJSON(request.CaseId)
    // Export is downstream of the committed route. An unavailable gateway or
    // invalid receipt never changes the routing status returned to the process.
    If $$$ISOK(sc) {
        Try {
            Set exportRequest = ##class(SilentShift.PEX.Support).Request(request.CaseId)
            Set exportStatus = ..SendRequestSync("ReceiptExporter", exportRequest, .exportResponse, 5)
            If $$$ISERR(exportStatus) {
                $$$LOGWARNING("Java PEX receipt export unavailable; committed route preserved")
            } ElseIf '$ISOBJECT(exportResponse) {
                $$$LOGWARNING("Java PEX receipt response missing; committed route preserved")
            } ElseIf 'exportResponse.SignatureValid {
                $$$LOGWARNING("Java PEX receipt signature invalid; committed route preserved")
            }
        } Catch exportError {
            $$$LOGWARNING("Java PEX receipt export failed; committed route preserved")
        }
    }
    Return sc
}
XData MessageMap
{
<MapItems><MapItem MessageType="SilentShift.Message"><Method>Hold</Method></MapItem></MapItems>
}
}
