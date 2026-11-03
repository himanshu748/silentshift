Include (%occStatus, Ensemble)

/// Fresh adapterless service per HTTP call. The authenticated API sets the
/// original production session and PreserveSession before ProcessInput.
Class SilentShift.Provider.Ingress Extends Ens.BusinessService
{
Parameter ADAPTER = "";

Method OnProcessInput(pInput As %RegisteredObject, Output pOutput As %RegisteredObject, ByRef pHint As %String) As %Status
{
    If '$ISOBJECT(pInput) Return $$$ERROR($$$GeneralError,"PROVIDER_REQUEST_REQUIRED")
    If 'pInput.%IsA("SilentShift.Provider.CallRequest") Return $$$ERROR($$$GeneralError,"PROVIDER_REQUEST_REQUIRED")
    If (pInput.ProductionSessionId < 1) || (pInput.ProductionSessionId '= ..%SessionId) Return $$$ERROR($$$GeneralError,"PROVIDER_SESSION_MISMATCH")
    Set wait = ##class(SilentShift.AI.Investigator).WaitSeconds()+2
    Return ..SendRequestSync("ProviderForwarder",pInput,.pOutput,wait)
}
}
