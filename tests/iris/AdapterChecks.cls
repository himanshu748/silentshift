Include (%occStatus, %outUnitTest)

/// No model calls. Test helpers inspect only this feed's metadata and native headers.
Class SilentShift.Test.AdapterChecks Extends %UnitTest.TestCase
{
Method TestContracts()
{
    Set checks = ..Contracts(), iterator = checks.%GetIterator()
    While iterator.%GetNext(.name, .passed) {
        Do $$$AssertTrue(passed, name)
    }
}

Method TestIterator()
{
    Set report = ..IteratorContracts(), checks = report.%Get("checks"), iterator = checks.%GetIterator()
    While iterator.%GetNext(.name, .passed) {
        Do $$$AssertTrue(passed, name)
    }
}

/// Retained, labeled non-input probe files exercise the SAME bounded iterator
/// used by OnTask. These .probe files cannot create cases or invoke a model.
ClassMethod IteratorContracts() As %DynamicObject
{
    If '##class(SilentShift.Adapter.PartnerJSON).RootSafe() Throw ##class(%Exception.General).%New("Safe mounted inbox required")
    Set root = ##class(SilentShift.Adapter.PartnerJSON).#ROOT
    Set prefix = "iterator-"_$TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")
    For index = 1:1:3 {
        Set target = root_"/"_prefix_"-"_index_".probe"
        If ##class(SilentShift.Adapter.PartnerJSON).EntryExists(target) Throw ##class(%Exception.General).%New("Iterator probe collision")
        Set stream = ##class(%Stream.FileBinary).%New(), stream.Filename = target
        Set sc = stream.Write("Synthetic native iterator probe; not a partner input.")
        $$$ThrowOnError(sc)
        Set sc = stream.%Save()
        $$$ThrowOnError(sc)
        Do stream.%Close()
    }
    Set sc = ##class(%File).FileSetExecute(.handle, root, prefix_"-1.probe", "Name", 0)
    $$$ThrowOnError(sc)
    Set sc = ##class(%File).FileSetFetch(.handle, .row, .atEnd)
    $$$ThrowOnError(sc)
    Set validLastRow = (row '= "") && (atEnd = 1)
    Set sc = ##class(%File).FileSetClose(handle)
    $$$ThrowOnError(sc)
    Set one = ##class(SilentShift.Adapter.PartnerJSON).ListFiles(prefix_"-1.probe", 4)
    Set bounded = ##class(SilentShift.Adapter.PartnerJSON).ListFiles(prefix_"*.probe", 2)
    Set all = ##class(SilentShift.Adapter.PartnerJSON).ListFiles(prefix_"*.probe", 4)
    Set clamped = ##class(SilentShift.Adapter.PartnerJSON).ListFiles(prefix_"*.probe", 0)
    Set checks = {"installed_api_last_row_has_at_end": false, "production_iterator_keeps_single_last_row": false, "production_iterator_keeps_all_three": false, "production_iterator_obeys_two_row_cap": false, "zero_limit_clamped_to_one": false}
    Do checks.%Set("installed_api_last_row_has_at_end", validLastRow, "boolean")
    Do checks.%Set("production_iterator_keeps_single_last_row", (one.%Size() = 1) && (one.%Get(0) = (root_"/"_prefix_"-1.probe")), "boolean")
    Do checks.%Set("production_iterator_keeps_all_three", all.%Size() = 3, "boolean")
    Do checks.%Set("production_iterator_obeys_two_row_cap", bounded.%Size() = 2, "boolean")
    Do checks.%Set("zero_limit_clamped_to_one", clamped.%Size() = 1, "boolean")
    Do checks.%Set("safe_probe_is_regular", ##class(SilentShift.Adapter.PartnerJSON).Regular(root_"/"_prefix_"-1.probe"), "boolean")
    Return {"suite": "native-file-iterator/1", "probe_prefix": (prefix), "retained_probe_files": 3, "model_calls_requested": false, "checks": (checks)}
}

/// Pure contract checks shared with the standalone driver; no manager cleanup.
ClassMethod Contracts() As %DynamicObject
{
    Set checks = {}
    Do checks.%Set("ordinary_name", ##class(SilentShift.Adapter.PartnerJSON).SafeName("partner-01_A"), "boolean")
    Set index = 0
    For name = "", "..", "../order", "/tmp/order", "a.b", "a b", "a"_$CHAR(10)_"b", $CHAR(233), "-starts-with-dash", $JUSTIFY("a", 81) {
        Set index = index + 1
        Do checks.%Set("unsafe_name_"_index, '##class(SilentShift.Adapter.PartnerJSON).SafeName(name), "boolean")
    }
    Set raw = " {""source"":""synthetic"", ""event_id"":""test""} "
    Set envelope = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Service.PartnerFiles).Envelope(raw))
    Do checks.%Set("envelope_only_two_fields", envelope.%Size() = 2, "boolean")
    Do checks.%Set("original_preserved", envelope.%Get("raw_payload") = raw, "boolean")
    Do checks.%Set("no_partner_clock", 'envelope.%IsDefined("clock"), "boolean")
    For field = "message", "raw_payload", "scenario_id", "dataset_version", "clock", "fault", "references", "action", "review", "reviewer", "case_id" {
        Set value = {}, rejected = 0
        Do value.%Set(field, "untrusted")
        Try {
            Set ignored = ##class(SilentShift.Service.PartnerFiles).Envelope(value.%ToJSON())
        } Catch error {
            Set rejected = 1
        }
        Do checks.%Set("reserved_"_field, rejected, "boolean")
    }
    Set index = 0
    For raw = "{", "[]", "null", "{""event_id"":""a"",""event_id"":""b""}" {
        Set index = index + 1, rejected = 0
        Try {
            Set ignored = ##class(SilentShift.Service.PartnerFiles).Envelope(raw)
        } Catch error {
            Set rejected = 1
        }
        Do checks.%Set("invalid_json_"_index, rejected, "boolean")
    }
    Return checks
}

ClassMethod LocalReady() As %Boolean
{
    If $SYSTEM.Util.GetEnviron("SILENTSHIFT_PARTNER_FILES_ENABLED") '= "1" Return 0
    If '##class(SilentShift.Adapter.PartnerJSON).RootSafe() Return 0
    Set url = $SYSTEM.Util.GetEnviron("SILENTSHIFT_LLM_BASE_URL")
    Set local = (url = "http://localhost:11434/v1/") || (url = "http://127.0.0.1:11434/v1/") || (url = "http://host.lima.internal:11434/v1/") || (url = "http://host.docker.internal:11434/v1/") || (url = "http://ollama:11434/v1/")
    Return local && ($ZCONVERT($SYSTEM.Util.GetEnviron("SILENTSHIFT_MODEL"), "L") [ "qwen3")
}

/// Existing-case inspection never invokes ProcessInput or calls a model.
ClassMethod Inspect(name As %String) As %String
{
    If '##class(SilentShift.Adapter.PartnerJSON).SafeName(name) Throw ##class(%Exception.General).%New("Unsafe test basename")
    Set id = $GET(^SilentShift.PartnerFiles("files", name, "case_id")), headers = []
    Set result = {"file": (name), "case_id": (id), "held": false, "failures": ($GET(^SilentShift.PartnerFiles("files", name, "failures"), 0)), "completed": false, "dispatch_status": ($GET(^SilentShift.PartnerFiles("files", name, "dispatch"))), "input_sha256": ($GET(^SilentShift.PartnerFiles("files", name, "sha256"))), "input_bytes": ($GET(^SilentShift.PartnerFiles("files", name, "bytes"))), "headers": (headers)}
    Do result.%Set("held", $GET(^SilentShift.PartnerFiles("files", name, "held"), 0), "boolean")
    Do result.%Set("completed", $GET(^SilentShift.PartnerFiles("files", name, "completed"), 0), "boolean")
    If id '= "" {
        Set item = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        Do result.%Set("trace_id", item.%Get("trace_id"))
        Do result.%Set("scenario_id", item.%Get("scenario_id"))
        Do result.%Set("clock", item.%Get("clock"))
        Do result.%Set("received_at", item.%Get("received_at"))
        Do result.%Set("reference_count", item.%Get("references").%Size())
        Set statement = ##class(%SQL.Statement).%New()
        Set sc = statement.%Prepare("SELECT TOP 100 ID,SessionId,SourceConfigName,TargetConfigName,MessageBodyClassName FROM Ens.MessageHeader WHERE SessionId = ? ORDER BY ID")
        $$$ThrowOnError(sc)
        Set rows = statement.%Execute(+item.%Get("trace_id"))
        If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("Native header inspection failed")
        While rows.%Next() {
            Do headers.%Push({"id": (rows.%Get("ID")), "session_id": (rows.%Get("SessionId")), "source": (rows.%Get("SourceConfigName")), "target": (rows.%Get("TargetConfigName")), "body_class": (rows.%Get("MessageBodyClassName"))})
        }
    }
    Return result.%ToJSON()
}

/// Fixed operator recovery, never dispatches. Resume ack/read retries after repairing the inbox.
ClassMethod ResumeHeld(name As %String) As %Status
{
    If '##class(SilentShift.Adapter.PartnerJSON).SafeName(name) Return $$$ERROR($$$GeneralError, "Unsafe test basename")
    Lock +^SilentShift.Lock("partner-file", name):1
    If '$TEST Return $$$ERROR($$$GeneralError, "File is busy")
    Kill ^SilentShift.PartnerFiles("files", name, "held"), ^SilentShift.PartnerFiles("files", name, "failures")
    Lock -^SilentShift.Lock("partner-file", name)
    Return $$$OK
}
}
