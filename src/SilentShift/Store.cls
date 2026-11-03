Include %occStatus

/// Durable SQL-backed state. No model tool is allowed to invoke mutations here.
Class SilentShift.Store Extends %RegisteredObject
{

ClassMethod CreateCase(envelopeJSON As %String, Output id As %String, Output duplicate As %Boolean) As %Status
{
    Set id = "", duplicate = 0, locked = 0
    Try {
        Set envelope = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Canonical(envelopeJSON))
        Set message = envelope.%Get("message")
        If '$ISOBJECT(message) Return $$$ERROR($$$GeneralError, "APP_INVALID: message must be an object")
        Set source = message.%Get("source"), eventId = message.%Get("event_id")
        If (source = "") || (eventId = "") || ($LENGTH(source) > 160) || ($LENGTH(eventId) > 160) Return $$$ERROR($$$GeneralError, "APP_INVALID: bounded source and event_id are required")
        Set canonical = ##class(SilentShift.Bridge).Canonical(message.%ToJSON())
        Set raw = envelope.%Get("raw_payload", message.%ToJSON())
        If $LENGTH(raw) > 131072 Return $$$ERROR($$$GeneralError, "APP_INVALID: payload exceeds 128 KiB")
        If ##class(SilentShift.Bridge).Canonical(raw) '= canonical Return $$$ERROR($$$GeneralError, "APP_INVALID: original payload differs from message")
        Set fingerprint = ##class(SilentShift.Bridge).Hash(canonical)
        Set key = ##class(SilentShift.Bridge).PairHash(source, eventId)
        Lock +^SilentShift.Lock("ingest", key):5
        If '$TEST Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: ingestion is busy")
        Set locked = 1, existing = ""
        &sql(SELECT CaseId INTO :existing FROM SilentShift_Data.CaseRecord WHERE EventKey = :key)
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: ingestion lookup failed"))
        If existing '= "" {
            Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(existing)
            Lock -^SilentShift.Lock("ingest", key)
            Set locked = 0
            If record.Fingerprint '= fingerprint Return $$$ERROR($$$GeneralError, "APP_CONFLICT: event key was reused with different content")
            Set id = existing, duplicate = 1
            Return $$$OK
        }
        Set id = $TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")
        Set received = ##class(SilentShift.Bridge).Now()
        Set scenarioId = envelope.%Get("scenario_id", "")
        Set body = {"id": (id), "event_id": (eventId), "source": (source), "received_at": (received), "message": (message), "raw_payload": (raw), "scenario_id": (scenarioId), "dataset_version": (envelope.%Get("dataset_version")), "clock": (envelope.%Get("clock", received)), "references": [], "assessment": null, "recommendation": null, "agent": null, "policy": null, "routing": "PROCESSING", "version": 1, "trace_id": "", "review": null, "synthetic": false}
        If scenarioId '= "" {
            Do body.%Set("synthetic", 1, "boolean")
            If $ISOBJECT(envelope.%Get("fault")) Do body.%Set("fault", envelope.%Get("fault"))
        }
        Set record = ##class(SilentShift.Data.CaseRecord).%New()
        Set record.CaseId = id, record.EventKey = key, record.Fingerprint = fingerprint
        Set record.Source = source, record.EventId = eventId, record.ContractId = message.%Get("contract_id")
        Set record.ScenarioId = scenarioId, record.ReceivedAt = received
        Set record.RawPayload = raw, record.Body = body.%ToJSON(), record.ReferenceSnapshot = ""
        TSTART
        Set sc = record.%Save()
        $$$ThrowOnError(sc)
        Set detail = {"source": (source), "event_id": (eventId), "synthetic": (scenarioId '= "")}
        Do detail.%Set("synthetic", scenarioId '= "", "boolean")
        Set sc = ..AddEvent(id, "message_received", detail.%ToJSON())
        $$$ThrowOnError(sc)
        TCOMMIT
        Lock -^SilentShift.Lock("ingest", key)
        Return $$$OK
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShift.Lock("ingest", key)
        Set id = ""
        Return $$$ERROR($$$GeneralError, "APP_INVALID: ingestion could not persist a valid event")
    }
}

ClassMethod CaseJSON(id As %String) As %String
{
    Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
    If '$ISOBJECT(record) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: investigation does not exist"))
    Set body = ##class(%DynamicObject).%FromJSON(record.Body), events = []
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT TOP 200 ID,Kind,RecordedAt,Detail FROM SilentShift_Data.AuditEvent WHERE CaseId = ? ORDER BY ID")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(id)
    If rows.%SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: SQL read failed"))
    While rows.%Next() {
        Set detail = ##class(%DynamicObject).%FromJSON(rows.%Get("Detail"))
        Set item = {"id": (rows.%Get("ID")), "kind": (rows.%Get("Kind")), "at": (rows.%Get("RecordedAt")), "detail": (detail)}
        Do events.%Push(item)
    }
    &sql(SELECT COUNT(*) INTO :eventCount FROM SilentShift_Data.AuditEvent WHERE CaseId = :id)
    &sql(SELECT COUNT(*) INTO :deliveryCount FROM SilentShift_Data.Delivery WHERE CaseId = :id)
    Do body.%Set("delivery_count", deliveryCount)
    Do body.%Set("events", events)
    Do body.%Set("audit_event_count", eventCount)
    Do body.%Set("events_truncated", eventCount > 200, "boolean")
    Return body.%ToJSON()
}

ClassMethod AddEvent(id As %String, kind As %String, detailJSON As %String) As %Status
{
    Try {
        If (id = "") || (kind = "") || ($LENGTH(kind) > 80) || ($LENGTH(detailJSON) > 32768) Return $$$ERROR($$$GeneralError, "APP_INVALID: audit record is invalid")
        // Native tool callbacks enter from the AI Hub runtime. Keep their
        // read/audit path in ObjectScript instead of nesting Embedded Python
        // inside that foreign-function callback. Details are bounded JSON
        // constructed by trusted server methods; ingress uses strict Python
        // validation before it can reach this internal audit method.
        Set canonical = ##class(%DynamicObject).%FromJSON(detailJSON).%ToJSON()
        Set event = ##class(SilentShift.Data.AuditEvent).%New()
        Set at = $TRANSLATE($ZDATETIME($ZTIMESTAMP,3,1,6), " ", "T")_"Z"
        Set event.CaseId = id, event.Kind = kind, event.RecordedAt = at, event.Detail = canonical
        Return event.%Save()
    } Catch error {
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: audit record could not be persisted")
    }
}

ClassMethod SaveCase(id As %String, caseJSON As %String) As %Status
{
    Set locked = 0
    Try {
        Lock +^SilentShift.Lock("case", id):5
        If '$TEST Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: investigation is busy")
        Set locked = 1, record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
        If '$ISOBJECT(record) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: investigation does not exist"))
        Set incoming = ##class(%DynamicObject).%FromJSON(caseJSON)
        Set current = ##class(%DynamicObject).%FromJSON(record.Body)
        If incoming.%Get("version") '= record.Version {
            Lock -^SilentShift.Lock("case", id)
            Return $$$ERROR($$$GeneralError, "APP_CONFLICT: investigation version changed")
        }
        // These fields can only be set at ingestion or by SnapshotReferences.
        For field = "id", "event_id", "source", "received_at", "message", "raw_payload", "scenario_id", "dataset_version", "clock", "synthetic", "references", "fault", "workflow" {
            If current.%IsDefined(field) {
                If field = "synthetic" {
                    Do incoming.%Set(field, current.%Get(field), "boolean")
                } Else {
                    Do incoming.%Set(field, current.%Get(field))
                }
            }
        }
        Do incoming.%Remove("events")
        Do incoming.%Remove("audit_event_count")
        Do incoming.%Remove("events_truncated")
        Set record.Version = record.Version + 1
        Do incoming.%Set("version", record.Version)
        Set record.Routing = incoming.%Get("routing", record.Routing)
        Set record.Body = incoming.%ToJSON()
        Set sc = record.%Save()
        Lock -^SilentShift.Lock("case", id)
        Return sc
    } Catch error {
        If locked Lock -^SilentShift.Lock("case", id)
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: investigation update failed")
    }
}

ClassMethod ReferenceJSON(contractId As %String, scenarioId As %String = "") As %String
{
    Set statement = ##class(%SQL.Statement).%New()
    // IRIS stores the empty ObjectScript scope as SQL NULL. Bound equality to
    // an empty string does not retrieve the general-ingress approved catalog.
    Set sql = "SELECT TOP 101 Body FROM SilentShift_Data.Reference WHERE ContractId = ? AND ScenarioScope "
    Set sql = sql_$SELECT(scenarioId = "": "IS NULL", 1: "= ?")_" ORDER BY ReferenceId"
    Set sc = statement.%Prepare(sql)
    $$$ThrowOnError(sc)
    If scenarioId = "" {
        Set rows = statement.%Execute(contractId)
    } Else {
        Set rows = statement.%Execute(contractId, scenarioId)
    }
    Set result = []
    If rows.%SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: SQL read failed"))
    While rows.%Next() {
        Do result.%Push(##class(%DynamicObject).%FromJSON(rows.%Get("Body")))
    }
    If result.%Size() > 100 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: reference set exceeds safety limit"))
    Return result.%ToJSON()
}

ClassMethod SnapshotReferences(id As %String) As %Status
{
    Set locked = 0
    Try {
        Lock +^SilentShift.Lock("case", id):5
        If '$TEST Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: investigation is busy")
        Set locked = 1, record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
        If '$ISOBJECT(record) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: investigation does not exist"))
        If record.ReferenceSnapshot '= "" {
            Lock -^SilentShift.Lock("case", id)
            Return $$$OK
        }
        Set references = ..ReferenceJSON(record.ContractId, record.ScenarioId)
        Set body = ##class(%DynamicObject).%FromJSON(record.Body)
        Do body.%Set("references", ##class(%DynamicArray).%FromJSON(references))
        Set record.ReferenceSnapshot = references, record.Version = record.Version + 1
        Do body.%Set("version", record.Version)
        Set record.Body = body.%ToJSON()
        TSTART
        Set sc = record.%Save()
        $$$ThrowOnError(sc)
        Set detail = {"contract_id": (record.ContractId), "scenario_scope": (record.ScenarioId), "snapshot_immutable": true}
        Set sc = ..AddEvent(id, "references_retrieved", detail.%ToJSON())
        $$$ThrowOnError(sc)
        TCOMMIT
        Lock -^SilentShift.Lock("case", id)
        Return $$$OK
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShift.Lock("case", id)
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: reference snapshot failed")
    }
}

ClassMethod RelatedJSON(id As %String) As %String
{
    Set current = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
    If '$ISOBJECT(current) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: investigation does not exist"))
    Set statement = ##class(%SQL.Statement).%New()
    // Frozen scenarios are separate synthetic worlds, even when a contract ID
    // is reused. Never mix their histories into another scenario's context.
    Set sql = "SELECT TOP 3 CaseId,Body FROM SilentShift_Data.CaseRecord WHERE ContractId = ? AND CaseId <> ? AND ReceivedAt <= ? AND ScenarioId "
    Set sql = sql_$SELECT(current.ScenarioId = "": "IS NULL", 1: "= ?")_" ORDER BY ReceivedAt DESC,CaseId DESC"
    Set sc = statement.%Prepare(sql)
    $$$ThrowOnError(sc)
    If current.ScenarioId = "" {
        Set rows = statement.%Execute(current.ContractId, id, current.ReceivedAt)
    } Else {
        Set rows = statement.%Execute(current.ContractId, id, current.ReceivedAt, current.ScenarioId)
    }
    Set related = [], reviewed = []
    If rows.%SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: SQL read failed"))
    While rows.%Next() {
        Set candidate = ##class(%DynamicObject).%FromJSON(rows.%Get("Body"))
        Set assessment = candidate.%Get("assessment"), classification = "not_assessed"
        If $ISOBJECT(assessment) Set classification = assessment.%Get("classification")
        Set item = {"id": (candidate.%Get("id")), "received_at": (candidate.%Get("received_at")), "classification": (classification), "routing": (candidate.%Get("routing")), "review": (candidate.%Get("review")), "is_contract_authority": false}
        Do related.%Push(item)
        If $ISOBJECT(candidate.%Get("review")) Do reviewed.%Push(item)
    }
    Set result = {"related_records": (related), "reviewed_cases": (reviewed), "limit": 3, "history_is_contract_authority": false}
    Return result.%ToJSON()
}

ClassMethod ListCases(limit As %Integer = 50, offset As %Integer = 0) As %String
{
    Set limit = $SELECT(limit < 1: 1, limit > 200: 200, 1: limit), offset = $SELECT(offset < 0: 0, 1: offset)
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT CaseId FROM SilentShift_Data.CaseRecord ORDER BY ReceivedAt DESC,CaseId DESC")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(), items = [], index = 0
    If rows.%SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: SQL read failed"))
    While rows.%Next() {
        If index >= offset, items.%Size() < limit Do items.%Push(##class(%DynamicObject).%FromJSON(..CaseJSON(rows.%Get("CaseId"))))
        Set index = index + 1
        If items.%Size() >= limit Quit
    }
    &sql(SELECT COUNT(*) INTO :total FROM SilentShift_Data.CaseRecord)
    Set result = {"items": (items), "total": (total), "limit": (limit), "offset": (offset)}
    Do result.%Set("limit", limit, "number")
    Do result.%Set("offset", offset, "number")
    Return result.%ToJSON()
}

ClassMethod OverviewJSON() As %String
{
    &sql(SELECT COUNT(*) INTO :total FROM SilentShift_Data.CaseRecord)
    &sql(SELECT COUNT(*) INTO :held FROM SilentShift_Data.CaseRecord WHERE Routing = 'QUARANTINED')
    &sql(SELECT COUNT(*) INTO :reviews FROM SilentShift_Data.CaseRecord WHERE Routing = 'REVIEW')
    &sql(SELECT COUNT(*) INTO :delivered FROM SilentShift_Data.Delivery)
    &sql(SELECT COUNT(*) INTO :processing FROM SilentShift_Data.CaseRecord WHERE Routing = 'PROCESSING')
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT Body FROM SilentShift_Data.CaseRecord")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(), contradictions = 0
    If rows.%SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: SQL read failed"))
    While rows.%Next() {
        Set item = ##class(%DynamicObject).%FromJSON(rows.%Get("Body")), assessment = item.%Get("assessment")
        If $ISOBJECT(assessment), assessment.%Get("classification") = "VERIFIED_CONTRADICTION" Set contradictions = contradictions + 1
    }
    Set recentPage = ##class(%DynamicObject).%FromJSON(..ListCases(10, 0))
    Set result = {"processed": (total), "contradictions": (contradictions), "recent": (recentPage.%Get("items")), "total_processed": (total), "verified_contradictions": (contradictions), "pending_reviews": (reviews), "quarantined": (held), "delivered": (delivered), "processing": (processing)}
    Return result.%ToJSON()
}

/// Used only by the authenticated business service. Approval is a new,
/// independently constrained proposal; it never grants a policy bypass.
ClassMethod Review(id As %String, requestJSON As %String, reviewer As %String) As %String
{
    If '$SYSTEM.Security.Check("SSReview", "U") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_FORBIDDEN: reviewer permission is required"))
    If (reviewer = "") || (reviewer '= $USERNAME) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_FORBIDDEN: reviewer identity is invalid"))
    Set request = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Canonical(requestJSON))
    For field = "action", "reason", "idempotency_key" {
        If request.%GetTypeOf(field) '= "string" Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_INVALID: review text fields must be strings"))
    }
    If request.%GetTypeOf("expected_version") '= "number" Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_INVALID: review version must be an integer"))
    Set expectedVersion = request.%Get("expected_version") + 0
    If (expectedVersion < 1) || ((expectedVersion \ 1) '= expectedVersion) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_INVALID: review version must be a positive integer"))
    Set action = request.%Get("action"), reason = $ZSTRIP(request.%Get("reason"), "<>W"), token = request.%Get("idempotency_key")
    If (action '= "approve") && (action '= "reject") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_INVALID: review action is invalid"))
    If ($LENGTH(reason) < 3) || ($LENGTH(reason) > 2000) || (token = "") || ($LENGTH(token) > 160) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_INVALID: review requires a bounded reason and idempotency key"))
    Set reviewKey = ##class(SilentShift.Bridge).PairHash(id, token)
    Set fingerprint = ##class(SilentShift.Bridge).Hash(reviewer_":"_##class(SilentShift.Bridge).Canonical(requestJSON)), locked = 0
    Try {
        Lock +^SilentShift.Lock("case", id):5
        If '$TEST Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: investigation is busy"))
        Set locked = 1, prior = ##class(SilentShift.Data.ReviewAction).%OpenId(reviewKey)
        If $ISOBJECT(prior) {
            If prior.Fingerprint '= fingerprint Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: review key was reused with different content"))
            Lock -^SilentShift.Lock("case", id)
            Set locked = 0
            Set sc = ##class(SilentShift.Workflow.Support).SyncCompletion(id, reviewer)
            $$$ThrowOnError(sc)
            Return ..CaseJSON(id)
        }
        Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
        If '$ISOBJECT(record) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: investigation does not exist"))
        If request.%Get("expected_version") '= record.Version Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: investigation version changed"))
        If (record.Routing = "PROCESSING") || (record.Routing = "DELIVERED") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: investigation cannot be reviewed in its current state"))
        Set body = ##class(%DynamicObject).%FromJSON(record.Body), assessment = body.%Get("assessment")
        If '$ISOBJECT(assessment) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: no semantic assessment is available"))
        Set decision = $SELECT(action = "approve": "ALLOW", 1: "QUARANTINE")
        Set proposed = {"decision": (decision), "evidence_ids": (assessment.%Get("evidence_ids")), "explanation": (reason), "uncertainty": 0}
        Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessment.%ToJSON(), proposed.%ToJSON()))
        If action = "approve", 'policy.%Get("downstream_permitted") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_FORBIDDEN: deterministic policy forbids this release"))
        If action = "reject" {
            // An authorized human rejection is a workflow disposition, not a
            // model allegation of a verified semantic contradiction.
            Do policy.%Set("decision", "QUARANTINE")
            Do policy.%Set("decision_source", "authorized-human-rejection")
            Do policy.%Set("downstream_permitted", 0, "boolean")
            Do policy.%Set("release_eligible", 0, "boolean")
            Do policy.%Set("reasons", ["An authorized reviewer rejected this transaction."])
            Do policy.%Set("checks", [{"code": "HUMAN_REJECTION", "passed": true, "reason": "Reviewer identity, reason, version and idempotency were validated."}])
        }
        Set workflow = body.%Get("workflow")
        If $ISOBJECT(workflow) {
            If $ISOBJECT(body.%Get("review")) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: native workflow review is already decided; reuse its original review key"))
            // Claim only after version and deterministic policy validation.
            // Native claim persists independently; no user transaction spans
            // the native engine's deferred-response enqueue/completion path.
            Set sc = ##class(SilentShift.Workflow.Support).Claim(id, workflow, reviewer, record.Version, .claim)
            $$$ThrowOnError(sc)
            Do workflow.%Set("status", "completion_pending")
            Do workflow.%Set("claimed_by", reviewer)
            Do workflow.%Set("claimed_at", claim.%Get("claimed_at"))
            Do body.%Set("workflow", workflow)
        }
        Set review = {"action": (action), "reason": (reason), "reviewer": (reviewer), "at": (##class(SilentShift.Bridge).Now()), "idempotency_key": (token), "expected_version": (record.Version)}
        Do body.%Set("review", review)
        Do body.%Set("policy_recommendation", proposed)
        Do body.%Set("policy", policy)
        Set record.Version = record.Version + 1
        Do body.%Set("version", record.Version)
        Set record.Body = body.%ToJSON()
        Set receipt = ##class(SilentShift.Data.ReviewAction).%New()
        Set receipt.ReviewKey = reviewKey, receipt.CaseId = id, receipt.Fingerprint = fingerprint, receipt.Body = review.%ToJSON()
        TSTART
        Set sc = record.%Save()
        $$$ThrowOnError(sc)
        Set sc = receipt.%Save()
        $$$ThrowOnError(sc)
        Set sc = ..AddEvent(id, "review_action", review.%ToJSON())
        $$$ThrowOnError(sc)
        TCOMMIT
        Lock -^SilentShift.Lock("case", id)
        Set locked = 0
        Set sc = ##class(SilentShift.Workflow.Support).SyncCompletion(id, reviewer)
        $$$ThrowOnError(sc)
        Return ..CaseJSON(id)
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShift.Lock("case", id)
        // Only our stable application messages are allowed across this boundary.
        Set text = $SYSTEM.Status.GetErrorText(error.AsStatus())
        If text [ "APP_" Throw error
        Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_UNAVAILABLE: review could not be persisted"))
    }
}

/// Internal workflow metadata boundary. Native task/case association is fixed;
/// generic SaveCase updates cannot overwrite asynchronous workflow receipts.
ClassMethod SetWorkflow(id As %String, fieldsJSON As %String, eventKind As %String) As %Status
{
    Set locked = 0
    Try {
        If ($LENGTH(fieldsJSON) > 4096) || ($EXTRACT(eventKind, 1, 9) '= "workflow_") Return $$$ERROR($$$GeneralError, "APP_INVALID: workflow metadata is invalid")
        Set fields = ##class(%DynamicObject).%FromJSON(fieldsJSON)
        Lock +^SilentShift.Lock("case", id):5
        If '$TEST Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: workflow case update is busy")
        Set locked = 1, record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
        If '$ISOBJECT(record) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: workflow case does not exist"))
        // Review retains an OREF while a deferred response can update this row
        // in another job. Refresh under the case lock before merging receipts.
        Set sc = record.%Reload()
        $$$ThrowOnError(sc)
        Set body = ##class(%DynamicObject).%FromJSON(record.Body), workflow = body.%Get("workflow")
        If '$ISOBJECT(workflow) Set workflow = {}
        If fields.%IsDefined("task_id"), workflow.%Get("task_id") '= "", fields.%Get("task_id") '= workflow.%Get("task_id") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: workflow task association cannot change"))
        Set before = workflow.%ToJSON(), iterator = fields.%GetIterator()
        While iterator.%GetNext(.field, .value) {
            Do workflow.%Set(field, value, fields.%GetTypeOf(field))
        }
        If workflow.%ToJSON() = before {
            Lock -^SilentShift.Lock("case", id)
            Return $$$OK
        }
        Do body.%Set("workflow", workflow)
        Set record.Version = record.Version + 1
        Do body.%Set("version", record.Version)
        Set record.Body = body.%ToJSON()
        TSTART
        Set sc = record.%Save()
        $$$ThrowOnError(sc)
        Set sc = ..AddEvent(id, eventKind, fields.%ToJSON())
        $$$ThrowOnError(sc)
        TCOMMIT
        Lock -^SilentShift.Lock("case", id)
        Return $$$OK
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShift.Lock("case", id)
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native workflow metadata synchronization failed")
    }
}

/// Atomic simulator effect + receipt + case state, guarded again at the boundary.
ClassMethod Deliver(id As %String) As %Status
{
    Set locked = 0
    Try {
        Lock +^SilentShift.Lock("case", id):5
        If '$TEST Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: investigation is busy")
        Set locked = 1, record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
        If '$ISOBJECT(record) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_NOT_FOUND: investigation does not exist"))
        Set prior = ##class(SilentShift.Data.Delivery).%OpenId(id)
        If $ISOBJECT(prior) {
            Lock -^SilentShift.Lock("case", id)
            Return $$$OK
        }
        Set body = ##class(%DynamicObject).%FromJSON(record.Body), assessment = body.%Get("assessment"), savedPolicy = body.%Get("policy")
        Set recommendation = body.%Get("policy_recommendation", body.%Get("recommendation"))
        If '$ISOBJECT(assessment) || '$ISOBJECT(savedPolicy) || '$ISOBJECT(recommendation) Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: delivery evidence is incomplete"))
        Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessment.%ToJSON(), recommendation.%ToJSON()))
        If 'savedPolicy.%Get("downstream_permitted") || 'policy.%Get("downstream_permitted") || assessment.%Get("critical") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "APP_CONFLICT: delivery policy denied"))
        Set receipt = ##class(SilentShift.Data.Delivery).%New()
        Set receipt.CaseId = id, receipt.DeliveredAt = ##class(SilentShift.Bridge).Now(), receipt.Payload = record.RawPayload
        Set receipt.PolicyVersion = policy.%Get("policy_version"), receipt.CaseVersion = record.Version
        Set detail = {"destination": "iris-simulator", "case_id": (id), "at": (receipt.DeliveredAt), "policy_version": (receipt.PolicyVersion), "authorized_case_version": (record.Version)}
        Do body.%Set("delivery_receipt", detail)
        Do body.%Set("routing", "DELIVERED")
        Set record.Version = record.Version + 1, record.Routing = "DELIVERED"
        Do body.%Set("version", record.Version)
        Set record.Body = body.%ToJSON()
        TSTART
        Set sc = receipt.%Save()
        $$$ThrowOnError(sc)
        Set sc = record.%Save()
        $$$ThrowOnError(sc)
        Set sc = ..AddEvent(id, "message_delivered", detail.%ToJSON())
        $$$ThrowOnError(sc)
        TCOMMIT
        Lock -^SilentShift.Lock("case", id)
        Return $$$OK
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShift.Lock("case", id)
        Return $$$ERROR($$$GeneralError, "APP_CONFLICT: delivery remained blocked")
    }
}

ClassMethod Hold(id As %String) As %Status
{
    Set body = ##class(%DynamicObject).%FromJSON(..CaseJSON(id)), policy = body.%Get("policy")
    If body.%Get("routing") = "DELIVERED" Return $$$ERROR($$$GeneralError, "APP_CONFLICT: delivered message cannot be quarantined")
    If $ISOBJECT(policy), policy.%Get("downstream_permitted") Return $$$ERROR($$$GeneralError, "APP_CONFLICT: quarantine received an allow decision")
    Set route = "REVIEW"
    If $ISOBJECT(policy), policy.%Get("decision") = "QUARANTINE" Set route = "QUARANTINED"
    Set review = body.%Get("review")
    If $ISOBJECT(review), review.%Get("action") = "reject" Set route = "REJECTED"
    // Replaying an already-applied hold (including a review retry) must not
    // increment the case version or append another routing side effect.
    If body.%Get("routing") = route Return $$$OK
    Do body.%Set("routing", route)
    Set sc = ..SaveCase(id, body.%ToJSON())
    If $$$ISERR(sc) Return sc
    Set detail = {"route": (route), "downstream_effect": false}
    Return ..AddEvent(id, "message_held", detail.%ToJSON())
}
}
