Include %occStatus

Class SilentShiftPilot.ReferenceImport Extends %RegisteredObject
{
/// Trusted local operator import only. No REST route and no partner authority.
ClassMethod Import(path As %String) As %String
{
    Set locked = 0, initialLevel = $TLEVEL, stage = "preflight"
    Try {
        If $NAMESPACE '= "SILENTSHIFT" Throw ##class(%Exception.General).%New("Wrong namespace")
        If initialLevel Throw ##class(%Exception.General).%New("Import needs its own transaction")
        Set stream = ##class(%Stream.FileCharacter).%New()
        Set sc = stream.LinkToFile(path)
        $$$ThrowOnError(sc)
        If stream.Size > 131072 Throw ##class(%Exception.General).%New("Import too large")
        Set stage = "parse"
        Set bundle = ##class(%DynamicObject).%FromJSON(stream)
        If bundle.%Get("schema") '= "silentshift-csv-pilot/1" Throw ##class(%Exception.General).%New("Wrong bundle schema")
        Set refs = bundle.%Get("references")
        If '$ISOBJECT(refs) Throw ##class(%Exception.General).%New("Reference array required")
        If 'refs.%IsA("%DynamicArray") Throw ##class(%Exception.General).%New("Reference array required")
        If (refs.%Size() < 1) || (refs.%Size() > 20) Throw ##class(%Exception.General).%New("Invalid reference count")
        Lock +^SilentShiftPilotImport:5
        If '$TEST Throw ##class(%Exception.General).%New("Import busy")
        Set locked = 1, created = 0, reused = 0
        TSTART
        For index = 0:1:refs.%Size()-1 {
            Set stage = "validate-reference"
            Set ref = refs.%Get(index)
            Set referenceId = ref.%Get("id"), contractId = ref.%Get("contract_id")
            If (ref.%Get("authority") '= "approved") || ($Extract(contractId,1,9) '= "csv-line:") || ($Extract(referenceId,1,8) '= "csv-ref:") Throw ##class(%Exception.General).%New("Invalid pilot reference")
            Set provenance = ref.%Get("approval_provenance")
            If '$ISOBJECT(provenance) Throw ##class(%Exception.General).%New("Approval provenance required")
            If (provenance.%Get("approved_by") = "") || (provenance.%Get("approved_at") = "") Throw ##class(%Exception.General).%New("Approval provenance required")
            Set stage = "persist"
            Set body = ##class(SilentShift.Bridge).Canonical(ref.%ToJSON())
            Set key = ##class(SilentShift.Bridge).PairHash("",referenceId)
            Set record = ##class(SilentShift.Data.Reference).%OpenId(key)
            If $ISOBJECT(record) {
                If record.Body '= body Throw ##class(%Exception.General).%New("Immutable reference revision conflict")
                Set reused = reused + 1
            } Else {
                Set record = ##class(SilentShift.Data.Reference).%New()
                Set record.ReferenceKey = key, record.ReferenceId = referenceId, record.ContractId = contractId
                Set record.ScenarioScope = "", record.Body = body
                Set sc = record.%Save()
                $$$ThrowOnError(sc)
                Set created = created + 1
            }
        }
        TCOMMIT
        Lock -^SilentShiftPilotImport
        Set locked = 0, result = {"passed":true}
        Do result.%Set("created",created), result.%Set("reused",reused)
        Return result.%ToJSON()
    } Catch error {
        If $TLEVEL > initialLevel TROLLBACK 1
        If locked Lock -^SilentShiftPilotImport
        Set result = {"passed":false,"error":"PILOT_REFERENCE_IMPORT_REFUSED"}
        Do result.%Set("stage",stage)
        Return result.%ToJSON()
    }
}
}
