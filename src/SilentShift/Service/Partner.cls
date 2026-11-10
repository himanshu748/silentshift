Include %occStatus

/// Adapterless push service called by the authenticated REST boundary.
Class SilentShift.Service.Partner Extends Ens.BusinessService
{
Parameter ADAPTER = "";
Method OnProcessInput(pInput As %RegisteredObject, Output pOutput As %RegisteredObject, ByRef pHint As %String) As %Status
{
    Set pOutput = ##class(SilentShift.Reply).%New()
    Try {
        If '$ISOBJECT(pInput) Return $$$ERROR($$$GeneralError, "APP_INVALID: ingestion requires a character stream")
        If 'pInput.%IsA("%Stream.GlobalCharacter") Return $$$ERROR($$$GeneralError, "APP_INVALID: ingestion requires a global character stream")
        If pInput.Size > 1048576 Return $$$ERROR($$$GeneralError, "APP_INVALID: ingestion envelope exceeds 1 MiB")
        Set sc = pInput.Rewind()
        $$$ThrowOnError(sc)
        Set payload = pInput.Read(1048577)
        If $LENGTH(payload) > 1048576 Return $$$ERROR($$$GeneralError, "APP_INVALID: ingestion envelope exceeds 1 MiB")
        Set envelope = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Canonical(payload))
        Set request = ##class(SilentShift.Message).%New()
        If envelope.%Get("action") = "review" {
            Set id = envelope.%Get("case_id")
            Set reviewRequest = envelope.%Get("review")
            Do ##class(SilentShift.Store).Review(id, reviewRequest.%ToJSON(), envelope.%Get("reviewer"))
            Set request.Action = "review_route"
        } Else {
            Set sc = ##class(SilentShift.Store).CreateCase(payload, .id, .duplicate)
            If $$$ISERR(sc) Return sc
            If duplicate {
                Set pOutput.BodyJSON = ##class(SilentShift.Store).CaseJSON(id)
                Return $$$OK
            }
        }
        Set request.CaseId = id
        // Separate pools; allow the explicit agent budget plus bounded
        // reference/procedure/routing waits and native task linkage overhead.
        Set outerWait = ##class(SilentShift.AI.Investigator).WaitSeconds() + 35
        Set sc = ..SendRequestSync("Semantic", request, .response, outerWait)
        If $$$ISERR(sc) Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: production did not complete; event remains persisted and held")
        Set pOutput.BodyJSON = response.BodyJSON
        Return $$$OK
    } Catch error {
        Set text = $SYSTEM.Status.GetErrorText(error.AsStatus())
        If text [ "APP_" Return error.AsStatus()
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: production request failed")
    }
}
}
