Include %occStatus

/// Adapterless push service called by the authenticated REST boundary.
Class SilentShift.Service.Partner Extends Ens.BusinessService
{
Parameter ADAPTER = "";
Method OnProcessInput(pInput As %String, Output pOutput As %String) As %Status
{
    Set pOutput = ""
    Try {
        Set envelope = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Canonical(pInput))
        Set request = ##class(SilentShift.Message).%New()
        If envelope.%Get("action") = "review" {
            Set id = envelope.%Get("case_id")
            Set reviewRequest = envelope.%Get("review")
            Set reviewed = ##class(SilentShift.Store).Review(id, reviewRequest.%ToJSON(), envelope.%Get("reviewer"))
            Set request.Action = "review_route"
        } Else {
            Set sc = ##class(SilentShift.Store).CreateCase(pInput, .id, .duplicate)
            If $$$ISERR(sc) Return sc
            If duplicate {
                Set pOutput = ##class(SilentShift.Store).CaseJSON(id)
                Return $$$OK
            }
        }
        Set request.CaseId = id
        // All callees have separate pools. The agent wait inside Semantic is 60s.
        Set sc = ..SendRequestSync("Semantic", request, .response, 90)
        If $$$ISERR(sc) Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: production did not complete; event remains persisted and held")
        Set pOutput = response.BodyJSON
        Return $$$OK
    } Catch error {
        Set text = $SYSTEM.Status.GetErrorText(error.AsStatus())
        If text [ "APP_" Return error.AsStatus()
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: production request failed")
    }
}
}
