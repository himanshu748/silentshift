Include %occStatus

/// Partner file data enters the same Semantic production as REST ingress.
/// Only this server boundary constructs an envelope; file JSON has no metadata authority.
Class SilentShift.Service.PartnerFiles Extends Ens.BusinessService
{
Parameter ADAPTER = "SilentShift.Adapter.PartnerJSON";

ClassMethod Envelope(raw As %String) As %String
{
    If $LENGTH($ZCONVERT(raw, "O", "UTF8")) > 131072 Throw ##class(%Exception.General).%New("FILE_INPUT_TOO_LARGE")
    Set canonical = ##class(SilentShift.Bridge).Canonical(raw)
    Set message = ##class(%DynamicObject).%FromJSON(canonical)
    If 'message.%IsA("%DynamicObject") Throw ##class(%Exception.General).%New("FILE_MESSAGE_OBJECT_REQUIRED")
    // Reject an internal envelope outright, rather than silently reinterpreting it.
    For field = "message", "raw_payload", "scenario_id", "dataset_version", "clock", "fault", "references", "action", "review", "reviewer", "case_id" {
        If message.%IsDefined(field) Throw ##class(%Exception.General).%New("FILE_ENVELOPE_FORBIDDEN")
    }
    Set envelope = {"message": (message), "raw_payload": (raw)}
    Return envelope.%ToJSON()
}

Method OnProcessInput(pInput As %RegisteredObject, Output pOutput As %RegisteredObject, ByRef pHint As %String) As %Status
{
    Set pOutput = ##class(SilentShift.Reply).%New(), locked = 0, transaction = 0
    Try {
        If '$ISOBJECT(pInput) Throw ##class(%Exception.General).%New("FILE_STREAM_REQUIRED")
        If 'pInput.%IsA("%Stream.GlobalCharacter") Throw ##class(%Exception.General).%New("FILE_STREAM_REQUIRED")
        Set sc = pInput.Rewind()
        $$$ThrowOnError(sc)
        Set raw = pInput.Read(131073)
        Try {
            Set envelope = ..Envelope(raw)
        } Catch invalid {
            Set pOutput.BodyJSON = {"input_error": "FILE_INVALID_MESSAGE"}.%ToJSON()
            Return $$$OK
        }
        // A durable pending marker survives a crash before dispatch. Do not put
        // SendRequestAsync inside this transaction: Ens.Queue commits user transactions.
        TSTART
        Set transaction = 1
        Set sc = ##class(SilentShift.Store).CreateCase(envelope, .id, .duplicate)
        $$$ThrowOnError(sc)
        If 'duplicate Set ^SilentShift.PartnerFiles("dispatch", id) = "pending"
        TCOMMIT
        Set transaction = 0
        Lock +^SilentShift.Lock("file-dispatch", id):2
        If '$TEST Throw ##class(%Exception.General).%New("FILE_DISPATCH_BUSY")
        Set locked = 1, dispatch = $GET(^SilentShift.PartnerFiles("dispatch", id), "external")
        If dispatch = "pending" {
            // Once this marker is written, a crash is ambiguous. Never resubmit
            // automatically: an already queued job may still finish normally.
            Set ^SilentShift.PartnerFiles("dispatch", id) = "dispatching"
            Set request = ##class(SilentShift.Message).%New(), request.CaseId = id
            Set ..%SessionId = ""
            Set sc = ..SendRequestAsync("Semantic", request, "Partner JSON file")
            Set dispatch = $SELECT($$$ISOK(sc): "enqueued", 1: "uncertain")
            Set ^SilentShift.PartnerFiles("dispatch", id) = dispatch
            Set ^SilentShift.PartnerFiles("dispatch", id, "session_id") = ..%SessionId
        }
        Lock -^SilentShift.Lock("file-dispatch", id)
        Set locked = 0
        Set result = {"case_id": (id), "duplicate": false, "dispatch_status": (dispatch)}
        Do result.%Set("duplicate", duplicate, "boolean")
        Set pOutput.BodyJSON = result.%ToJSON()
        Return $$$OK
    } Catch error {
        If transaction, $TLEVEL TROLLBACK 1
        If locked Lock -^SilentShift.Lock("file-dispatch", id)
        // No parser/provider diagnostics, partner contents or filesystem paths.
        Return $$$ERROR($$$GeneralError, "FILE_INPUT_OR_DISPATCH_FAILED")
    }
}
}
