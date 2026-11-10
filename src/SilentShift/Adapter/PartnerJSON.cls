Include (%occStatus, Ensemble)

/// Trusted-operator UTF-8 JSON drop feed. Atomic rename .json.ready -> .json.work.
/// Terminal acknowledgments describe persisted outcomes, never transport guesses.
/// No files are deleted. .done/.hold, abandoned .tmp and held .work need operator retention.
Class SilentShift.Adapter.PartnerJSON Extends Ens.InboundAdapter
{
Parameter ROOT = "/var/opt/silentshift/partner-inbox";
Parameter OUTCOMEWAITMS = 600000;
Parameter SETTINGS = "CallInterval:Basic,BatchLimit:Basic,MaxBytes:Basic,MaxRetries:Basic";
Property BatchLimit As %Integer(MINVAL = 1, MAXVAL = 16) [ InitialExpression = 4 ];
Property MaxBytes As %Integer(MINVAL = 1024, MAXVAL = 131072) [ InitialExpression = 131072 ];
Property MaxRetries As %Integer(MINVAL = 1, MAXVAL = 5) [ InitialExpression = 3 ];

/// Read only one fixed operator-owned directory; no payload may choose a path.
ClassMethod SafeName(name As %String) As %Boolean
{
    If ($LENGTH(name) < 1) || ($LENGTH(name) > 80) Return 0
    If $TRANSLATE(name, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") '= "" Return 0
    If name'?1(1A,1N).79(1A,1N,1"-",1"_") Return 0
    Return 1
}

ClassMethod RootSafe() As %Boolean
{
    Return ##class(%File).DirectoryExists(..#ROOT) && (##class(%File).ResolvePath(..#ROOT) = ..#ROOT)
}

ClassMethod Regular(path As %String) As %Boolean
{
    If ##class(%File).GetDirectory(path) '= (..#ROOT_"/") Return 0
    If ##class(%File).ResolvePath(path) '= path Return 0
    Return (##class(%File).Attributes(path) \ 4096 # 16) = 8
}

ClassMethod EntryExists(path As %String) As %Boolean
{
    // Attributes also sees non-regular entries; never replace a dangling link.
    Return ##class(%File).Exists(path) || (##class(%File).Attributes(path) > 0)
}

ClassMethod ReadBytes(path As %String, maximum As %Integer) As %String
{
    If '..Regular(path) Throw ##class(%Exception.General).%New("FILE_NOT_REGULAR")
    If ##class(%File).GetFileSize(path) > maximum Throw ##class(%Exception.General).%New("FILE_INPUT_TOO_LARGE")
    Set stream = ##class(%Stream.FileBinary).%New()
    Set sc = stream.LinkToFile(path)
    $$$ThrowOnError(sc)
    Set length = maximum + 1, bytes = stream.Read(.length, .sc)
    Do stream.%Close()
    $$$ThrowOnError(sc)
    If $LENGTH(bytes) > maximum Throw ##class(%Exception.General).%New("FILE_INPUT_TOO_LARGE")
    Return bytes
}

/// Consume valid final rows even when FileSetFetch sets AtEnd=1 on that row.
/// The shared native iterator is bounded and exercised without model calls.
ClassMethod ListFiles(pattern As %String, maximum As %Integer = 256) As %DynamicArray
{
    Set files = [], maximum = $SELECT(maximum < 1: 1, maximum > 256: 256, 1: maximum)
    If (pattern [ "/") || (pattern [ "\") || (pattern [ "..") Throw ##class(%Exception.General).%New("FILE_SCAN_PATTERN_INVALID")
    Set sc = ##class(%File).FileSetExecute(.handle, ..#ROOT, pattern, "Name", 0)
    $$$ThrowOnError(sc)
    Try {
        For index = 1:1:maximum {
            Set sc = ##class(%File).FileSetFetch(.handle, .row, .atEnd)
            $$$ThrowOnError(sc)
            If row = "" Quit
            Do files.%Push($LISTGET(row, 1))
        }
        Set sc = ##class(%File).FileSetClose(handle)
        $$$ThrowOnError(sc)
    } Catch error {
        Set ignored = ##class(%File).FileSetClose(handle)
        Throw error
    }
    Return files
}

Method OnTask() As %Status
{
    Set ..BusinessHost.%WaitForNextCallInterval = 1
    If $SYSTEM.Util.GetEnviron("SILENTSHIFT_PARTNER_FILES_ENABLED") '= "1" Return $$$OK
    If '..RootSafe() Return $$$ERROR($$$GeneralError, "Partner inbox is absent or unsafe")
    Set count = 0, batch = $SELECT(..BatchLimit < 1: 1, ..BatchLimit > 16: 16, 1: ..BatchLimit)
    // Resume claimed work before accepting more inputs. Both loops are bounded.
    For pattern = "*.json.work", "*.json.ready" {
        Try {
            Set files = ..ListFiles(pattern, 256)
            For index = 0:1:files.%Size()-1 {
                If count >= batch Quit
                Set filename = ##class(%File).GetFilename(files.%Get(index))
                Set name = $EXTRACT(filename, 1, $LENGTH(filename) - $LENGTH($SELECT(pattern = "*.json.work": ".json.work", 1: ".json.ready")))
                If '..SafeName(name) Continue
                If $GET(^SilentShift.PartnerFiles("files", name, "held")) Continue
                Set count = count + 1
                Do ..ProcessFile(name, pattern = "*.json.ready")
            }
        } Catch error {
            Return $$$ERROR($$$GeneralError, "Partner inbox iteration failed")
        }
        If count >= batch Quit
    }
    Return $$$OK
}

Method ProcessFile(name As %String, ready As %Boolean) [ Private ]
{
    Set base = ..#ROOT_"/"_name_".json", work = base_".work", locked = 0
    Try {
        Lock +^SilentShift.Lock("partner-file", name):0
        If '$TEST Return
        Set locked = 1
        If ready {
            If '..Regular(base_".ready") Throw ##class(%Exception.General).%New("FILE_NOT_REGULAR")
            If ..EntryExists(work) {
                Lock -^SilentShift.Lock("partner-file", name)
                Return
            }
            If '##class(%File).Rename(base_".ready", work) Throw ##class(%Exception.General).%New("FILE_CLAIM_FAILED")
        }
        If '..Regular(work) Throw ##class(%Exception.General).%New("FILE_NOT_REGULAR")
        If $GET(^SilentShift.PartnerFiles("files", name, "ack")) '= "" {
            If $GET(^SilentShift.PartnerFiles("files", name, "sha256")) '= "" {
                Set bytes = ..ReadBytes(work, 131072)
                Set digest = $ZCONVERT($SYSTEM.Encryption.ToHex($SYSTEM.Encryption.SHAHash(256, bytes)), "L")
                If digest '= ^SilentShift.PartnerFiles("files", name, "sha256") Throw ##class(%Exception.General).%New("FILE_CONTENT_CHANGED")
            }
            Do ..FinishFile(name)
        } Else {
            Set maximum = $SELECT(..MaxBytes < 1024: 1024, ..MaxBytes > 131072: 131072, 1: ..MaxBytes)
            If ##class(%File).GetFileSize(work) > maximum {
                Do ..Reject(name, "FILE_INPUT_TOO_LARGE")
            } Else {
                Set bytes = ..ReadBytes(work, maximum)
                Set digest = $ZCONVERT($SYSTEM.Encryption.ToHex($SYSTEM.Encryption.SHAHash(256, bytes)), "L")
                If $GET(^SilentShift.PartnerFiles("files", name, "sha256"), digest) '= digest Throw ##class(%Exception.General).%New("FILE_CONTENT_CHANGED")
                Set ^SilentShift.PartnerFiles("files", name, "sha256") = digest
                Set ^SilentShift.PartnerFiles("files", name, "bytes") = $LENGTH(bytes)
                Set id = $GET(^SilentShift.PartnerFiles("files", name, "case_id"))
                If id = "" {
                    Set raw = $ZCONVERT(bytes, "I", "UTF8")
                    If $ZCONVERT(raw, "O", "UTF8") '= bytes Throw ##class(%Exception.General).%New("FILE_INVALID_UTF8")
                    Set stream = ##class(%Stream.GlobalCharacter).%New()
                    Set sc = stream.Write(raw)
                    $$$ThrowOnError(sc)
                    Set sc = ..BusinessHost.ProcessInput(stream, .reply)
                    $$$ThrowOnError(sc)
                    Set accepted = ##class(%DynamicObject).%FromJSON(reply.BodyJSON)
                    If accepted.%Get("input_error") = "FILE_INVALID_MESSAGE" {
                        Do ..Reject(name, "FILE_INVALID_MESSAGE")
                        Lock -^SilentShift.Lock("partner-file", name)
                        Return
                    }
                    Set id = accepted.%Get("case_id")
                    If id = "" Throw ##class(%Exception.General).%New("FILE_CASE_MISSING")
                    Set ^SilentShift.PartnerFiles("files", name, "case_id") = id
                    Set ^SilentShift.PartnerFiles("files", name, "dispatch") = accepted.%Get("dispatch_status")
                    Set ^SilentShift.PartnerFiles("files", name, "duplicate") = accepted.%Get("duplicate")
                    Set ^SilentShift.PartnerFiles("files", name, "wait_started") = $ZTIMESTAMP
                }
                If $GET(^SilentShift.PartnerFiles("files", name, "wait_started")) = "" Set ^SilentShift.PartnerFiles("files", name, "wait_started") = $ZTIMESTAMP
                Set item = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
                Set routing = item.%Get("routing")
                If routing '= "PROCESSING" {
                    If (routing '= "DELIVERED") && (routing '= "QUARANTINED") && (routing '= "REVIEW") && (routing '= "REJECTED") Throw ##class(%Exception.General).%New("FILE_UNKNOWN_ROUTE")
                    Set acknowledgment = ..Outcome(name, item)
                    Set ^SilentShift.PartnerFiles("files", name, "ack") = acknowledgment.%ToJSON()
                    Do ..FinishFile(name)
                } Else {
                    Set dispatch = $GET(^SilentShift.PartnerFiles("files", name, "dispatch"))
                    If (dispatch = "dispatching") || (dispatch = "uncertain") {
                        Do ..Reject(name, "FILE_DISPATCH_UNCERTAIN", id)
                    } ElseIf ##class(SilentShift.TraceEvent).ElapsedMS(^SilentShift.PartnerFiles("files", name, "wait_started")) > ..#OUTCOMEWAITMS {
                        // An unconfirmed outcome is an operator hold, never a
                        // routing verdict or a reason to resubmit existing work.
                        Do ..Reject(name, "FILE_OUTCOME_UNCONFIRMED", id)
                    }
                    // Enqueued work is durable; polling and ack failures never requeue it.
                }
            }
        }
        Lock -^SilentShift.Lock("partner-file", name)
    } Catch error {
        $$$LOGERROR("SS_FILE_RECOVERY_REQUIRED stage=partner-file case_id="_$GET(id))
        Set attempt = $INCREMENT(^SilentShift.PartnerFiles("files", name, "failures"))
        Set ^SilentShift.PartnerFiles("files", name, "error") = "FILE_OPERATOR_RECOVERY_REQUIRED"
        Set maximumRetries = $SELECT(..MaxRetries < 1: 1, ..MaxRetries > 5: 5, 1: ..MaxRetries)
        If attempt >= maximumRetries Set ^SilentShift.PartnerFiles("files", name, "held") = 1
        If locked Lock -^SilentShift.Lock("partner-file", name)
    }
}

Method Outcome(name As %String, item As %DynamicObject) As %DynamicObject [ Private ]
{
    Set policy = item.%Get("policy"), receipt = ""
    Set ack = {"protocol": "silentshift-partner-file/1", "file": (name_".json"), "status": "COMPLETED", "input_sha256": ($GET(^SilentShift.PartnerFiles("files", name, "sha256"))), "input_bytes": ($GET(^SilentShift.PartnerFiles("files", name, "bytes"))), "case_id": (item.%Get("id")), "routing": (item.%Get("routing")), "trace_id": (item.%Get("trace_id")), "policy_decision": (policy.%Get("decision")), "delivery_count": (item.%Get("delivery_count")), "delivery_receipt": null, "recorded_at": (##class(SilentShift.TraceEvent).UTC())}
    Do ack.%Set("duplicate_event", $GET(^SilentShift.PartnerFiles("files", name, "duplicate"), 0), "boolean")
    Set delivery = ##class(SilentShift.Data.Delivery).%OpenId(item.%Get("id"))
    If $ISOBJECT(delivery) {
        Set receipt = {"case_id": (delivery.CaseId), "delivered_at": (delivery.DeliveredAt), "policy_version": (delivery.PolicyVersion), "case_version": (delivery.CaseVersion), "destination": "included-iris-simulator"}
        Do ack.%Set("delivery_receipt", receipt)
    }
    Return ack
}

Method Reject(name As %String, code As %String, id As %String = "") [ Private ]
{
    Set ack = {"protocol": "silentshift-partner-file/1", "file": (name_".json"), "status": "REJECTED_INPUT", "error": (code), "case_id": (id), "input_bytes": (##class(%File).GetFileSize(..#ROOT_"/"_name_".json.work")), "input_sha256": null, "delivery_receipt": null, "recorded_at": (##class(SilentShift.TraceEvent).UTC())}
    If $GET(^SilentShift.PartnerFiles("files", name, "sha256")) '= "" Do ack.%Set("input_sha256", ^SilentShift.PartnerFiles("files", name, "sha256"))
    If id '= "" Do ack.%Set("status", "OPERATOR_HOLD")
    Set ^SilentShift.PartnerFiles("files", name, "ack") = ack.%ToJSON()
    Set ^SilentShift.PartnerFiles("files", name, "reject") = 1
    Do ..FinishFile(name)
}

Method FinishFile(name As %String) [ Private ]
{
    Set base = ..#ROOT_"/"_name_".json", target = base_".ack.json"
    Set encoded = $ZCONVERT(^SilentShift.PartnerFiles("files", name, "ack"), "O", "UTF8")
    If ..EntryExists(target) {
        If ..ReadBytes(target, 8192) '= encoded Throw ##class(%Exception.General).%New("FILE_ACK_COLLISION")
    } Else {
        Set temporary = base_".ack."_$TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")_".tmp"
        If ..EntryExists(temporary) Throw ##class(%Exception.General).%New("FILE_ACK_COLLISION")
        Set stream = ##class(%Stream.FileBinary).%New(), stream.Filename = temporary
        Set sc = stream.Write(encoded)
        $$$ThrowOnError(sc)
        Set sc = stream.%Save()
        $$$ThrowOnError(sc)
        Do stream.%Close()
        If '..Regular(temporary) Throw ##class(%Exception.General).%New("FILE_ACK_UNSAFE")
        If '##class(%File).Rename(temporary, target) Throw ##class(%Exception.General).%New("FILE_ACK_FAILED")
    }
    Set suffix = $SELECT($GET(^SilentShift.PartnerFiles("files", name, "reject")): ".hold", 1: ".done")
    If ..EntryExists(base_suffix) {
        If suffix '= ".done" Throw ##class(%Exception.General).%New("FILE_ARCHIVE_COLLISION")
        If '..Regular(base_suffix) Throw ##class(%Exception.General).%New("FILE_ARCHIVE_UNSAFE")
        If '##class(%File).Compare(base_".work", base_suffix) Throw ##class(%Exception.General).%New("FILE_ARCHIVE_COLLISION")
        // An identical redrop reuses its existing ack and retains both inputs.
        Set suffix = ".duplicate."_$TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")
    }
    If '##class(%File).Rename(base_".work", base_suffix) Throw ##class(%Exception.General).%New("FILE_ARCHIVE_FAILED")
    Set ^SilentShift.PartnerFiles("files", name, "completed") = 1
}
}
