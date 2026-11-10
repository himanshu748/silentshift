Include %occStatus

/// CSV validation runs in Embedded Python. Only SSImport can add authority.
Class SilentShift.CSV Extends %RegisteredObject
{
ClassMethod Prepare(raw As %String, commit As %Boolean = 0) As %String [ Language = python ]
{
    import iris, json, sys, csv
    iris.cls('SilentShift.Bridge').Import()
    from silentshift.csv_orders import prepare_request
    try:
        result = prepare_request(raw, commit=bool(commit))
    except (ValueError, TypeError, RecursionError, csv.Error):
        raise ValueError('APP_INVALID: CSV format, preview or authority confirmation') from None
    return json.dumps(result, allow_nan=False, separators=(',', ':'), ensure_ascii=False)
}

/// Read back existing identities before any import. A changed event is a
/// conflict, not permission to mint a new case or overwrite a reference.
ClassMethod Preview(raw As %String, commit As %Boolean = 0) As %DynamicObject
{
    Set prepared = ##class(%DynamicObject).%FromJSON(..Prepare(raw,commit))
    Set bundle = prepared.%Get("bundle"), records = bundle.%Get("records")
    For index=0:1:records.%Size()-1 {
        Set row = records.%Get(index), message = row.%Get("message")
        Set key = ##class(SilentShift.Bridge).PairHash(message.%Get("source"),message.%Get("event_id"))
        Set existing = ""
        &sql(SELECT CaseId INTO :existing FROM SilentShift_Data.CaseRecord WHERE EventKey = :key)
        If SQLCODE<0 Throw ##class(%Exception.General).%New("APP_UNAVAILABLE")
        Do row.%Set("existing_case", "", "null")
        If existing'="" {
            Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(existing)
            Set fingerprint = ##class(SilentShift.Bridge).Hash(##class(SilentShift.Bridge).Canonical(message.%ToJSON()))
            If record.Fingerprint'=fingerprint Throw ##class(%Exception.General).%New("APP_CONFLICT: CSV event identity")
            Set data = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(existing))
            Set summary = {}
            For field="id","routing","trace_id","delivery_count" Do summary.%Set(field,data.%Get(field))
            Set agent = data.%Get("agent"), observation = {"status":null,"failure_code":null,"tool_reads":null}
            If $ISOBJECT(agent) {
                For field="status","failure_code","tool_reads" Do observation.%Set(field,agent.%Get(field))
            }
            Do summary.%Set("agent",observation)
            Do row.%Set("existing_case",summary)
        }
    }
    Set result = {"preview_hash":(prepared.%Get("preview_hash")),"feed_sha256":(bundle.%Get("feed_sha256")),"approved_sha256":(bundle.%Get("approved_sha256")),"records":(records),"references":(bundle.%Get("references")),"mode":"per-line-simulator","atomic_order_delivery":false,"order_completeness":"not_verified"}
    If commit {
        // Reparse the originals for the write, without readback annotations.
        Set clean = ##class(%DynamicObject).%FromJSON(..Prepare(raw,1))
        Set input = ##class(%DynamicObject).%FromJSON(raw)
        Set imported = ..ImportReferences(clean.%Get("bundle"),clean.%Get("preview_hash"),clean.%Get("reason"),input.%Get("orders_csv"),input.%Get("approved_csv"))
        Do result.%Set("import",imported)
    }
    Return result
}

/// One transaction owns immutable references and their import receipt. There
/// are no file paths, external URLs, model calls or delivery effects here.
ClassMethod ImportReferences(bundle As %DynamicObject, importId As %String, reason As %String, ordersCSV As %String, approvedCSV As %String) As %DynamicObject [ Private ]
{
    If '$SYSTEM.Security.Check("SSImport","USE") Throw ##class(%Exception.General).%New("APP_FORBIDDEN")
    If $TLEVEL Throw ##class(%Exception.General).%New("APP_UNAVAILABLE: nested CSV import")
    Set locked = 0
    Try {
        Set refs = bundle.%Get("references"), created = 0, reused = 0
        Set at = ##class(SilentShift.Bridge).Now()
        // Share the existing CLI import lock: neither path can race a revision.
        Lock +^SilentShiftPilotImport:5
        If '$TEST Throw ##class(%Exception.General).%New("APP_UNAVAILABLE: CSV import busy")
        Set locked = 1
        TSTART
        For index=0:1:refs.%Size()-1 {
            Set ref = refs.%Get(index), referenceId = ref.%Get("id")
            Set body = ##class(SilentShift.Bridge).Canonical(ref.%ToJSON())
            Set key = ##class(SilentShift.Bridge).PairHash("",referenceId)
            Set record = ##class(SilentShift.Data.Reference).%OpenId(key)
            If $ISOBJECT(record) {
                If record.Body'=body Throw ##class(%Exception.General).%New("APP_CONFLICT: immutable reference revision")
                Set reused = reused + 1
            } Else {
                Set record = ##class(SilentShift.Data.Reference).%New()
                Set record.ReferenceKey = key, record.ReferenceId = referenceId
                Set record.ContractId = ref.%Get("contract_id"), record.ScenarioScope = "", record.Body = body
                Set sc = record.%Save()
                $$$ThrowOnError(sc)
                Set created = created + 1
            }
        }
        If '$DATA(^SilentShift.CSVImports(importId)) {
            Set receipt = {"id":(importId),"imported_by":($USERNAME),"imported_at":(at),"reason":(reason),"reference_count":(refs.%Size()),"feed_sha256":(bundle.%Get("feed_sha256")),"approved_sha256":(bundle.%Get("approved_sha256")),"records":(bundle.%Get("records"))}
            Set ^SilentShift.CSVImports(importId) = receipt.%ToJSON()
        }
        // Preserve exact UTF-8 text, including BOM and CRLF, separately from
        // the metadata returned to viewers. No path or partner-controlled
        // authority is stored as executable input. Repeats cannot replace it.
        If $DATA(^SilentShift.CSVSources(importId,"orders")) {
            If (^SilentShift.CSVSources(importId,"orders")'=ordersCSV) || (^SilentShift.CSVSources(importId,"approved")'=approvedCSV) Throw ##class(%Exception.General).%New("APP_CONFLICT: immutable CSV source")
        } Else {
            Set ^SilentShift.CSVSources(importId,"orders") = ordersCSV
            Set ^SilentShift.CSVSources(importId,"approved") = approvedCSV
            Set ^SilentShift.CSVSources(importId,"retained_at") = at
            Set ^SilentShift.CSVSources(importId,"retained_by") = $USERNAME
        }
        Set receipt = ##class(%DynamicObject).%FromJSON(^SilentShift.CSVImports(importId))
        TCOMMIT
        Lock -^SilentShiftPilotImport
        Set locked = 0
        Return {"created":(created),"reused":(reused),"receipt":(receipt),"source_retained":true}
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShiftPilotImport
        Throw error
    }
}
}
