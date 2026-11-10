Include %occStatus

/// Source-bound local vectors. Precedents never replace a case's frozen
/// reference snapshot or deterministic policy.
Class SilentShift.Precedents Extends %RegisteredObject
{
Parameter MODEL = "all-minilm:22m";
Parameter DIMENSIONS = 384;

ClassMethod Timestamp(value As %String) As %String [ Language = python ]
{
    from datetime import datetime, timezone
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            return ''
        return stamp.astimezone(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')
    except (ValueError, TypeError, AttributeError, OverflowError):
        return ''
}

/// Fixed business fields only: no partner notes, raw answers or review prose.
ClassMethod BusinessText(value As %DynamicObject, kind As %String = "") As %String
{
    If kind = "" Set kind = value.%Get("kind")
    Set text = "kind: "_kind
    For field = "contract_id", "quantity", "unit", "amount", "amount_scale", "currency", "product_id", "business_unit" {
        Set type = value.%GetTypeOf(field)
        If (type = "string") || (type = "number") {
            Set scalar = $EXTRACT($TRANSLATE(value.%Get(field),$CHAR(9,10,13)," "),1,80)
            Set text = text_"; "_field_": "_scalar
        }
    }
    Return $EXTRACT(text,1,320)
}

ClassMethod QueryForCase(body As %DynamicObject) As %String
{
    Set message = body.%Get("message")
    If '$ISOBJECT(message) Throw ##class(%Exception.General).%New("PRECEDENT_MESSAGE_REQUIRED")
    If (message.%Get("kind") '= "order") && (message.%Get("kind") '= "payment") Throw ##class(%Exception.General).%New("PRECEDENT_KIND_REQUIRED")
    Return ..BusinessText(message)
}

/// Read-only native source validation, also used by the evidence inspector.
ClassMethod SourceDocument(sourceType As %String, sourceKey As %String) As %DynamicObject
{
    If sourceType = "resolved_case" Return ..CaseDocument(sourceKey)
    If sourceType = "approved_amendment" Return ..AmendmentDocument(sourceKey)
    Return ""
}

ClassMethod CaseDocument(id As %String) As %DynamicObject [ Private ]
{
    Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
    If '$ISOBJECT(record) Return ""
    If (record.Routing '= "DELIVERED") && (record.Routing '= "REJECTED") Return ""
    Set body = ##class(%DynamicObject).%FromJSON(record.Body), message = body.%Get("message"), assessment = body.%Get("assessment"), policy = body.%Get("policy")
    If '$ISOBJECT(message) || '$ISOBJECT(assessment) || '$ISOBJECT(policy) Return ""
    If (message.%Get("kind") '= "order") && (message.%Get("kind") '= "payment") Return ""
    If message.%Get("contract_id") '= record.ContractId Return ""
    If (body.%Get("id") '= id) || (body.%Get("routing") '= record.Routing) || (body.%Get("trace_id") = "") Return ""
    If record.Routing = "DELIVERED" {
        Set receipt = ##class(SilentShift.Data.Delivery).%OpenId(id)
        If '$ISOBJECT(receipt) Return ""
        If (receipt.CaseId '= id) || (receipt.Payload '= record.RawPayload) || assessment.%Get("critical") Return ""
        Set proposal = body.%Get("policy_recommendation",body.%Get("recommendation"))
        If '$ISOBJECT(proposal) Return ""
        Set current = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessment.%ToJSON(),proposal.%ToJSON()))
        If 'policy.%Get("downstream_permitted") || 'current.%Get("downstream_permitted") Return ""
        Set resolved = ..Timestamp(receipt.DeliveredAt)
    } Else {
        Set review = body.%Get("review")
        If '$ISOBJECT(review) || (review.%Get("action") '= "reject") Return ""
        Set key = ##class(SilentShift.Bridge).PairHash(id,review.%Get("idempotency_key")), receipt = ##class(SilentShift.Data.ReviewAction).%OpenId(key)
        If '$ISOBJECT(receipt) || (receipt.CaseId '= id) Return ""
        Set saved = ##class(%DynamicObject).%FromJSON(receipt.Body)
        For field = "action", "reason", "reviewer", "idempotency_key", "expected_version" {
            If saved.%Get(field) '= review.%Get(field) Return ""
        }
        If ##class(SilentShift.Data.Delivery).%ExistsId(id) || policy.%Get("downstream_permitted") Return ""
        Set statement = ##class(%SQL.Statement).%New(), sc = statement.%Prepare("SELECT TOP 1 RecordedAt,Detail FROM SilentShift_Data.AuditEvent WHERE CaseId = ? AND Kind = 'message_held' ORDER BY ID DESC")
        $$$ThrowOnError(sc)
        Set rows = statement.%Execute(id)
        If (rows.%SQLCODE < 0) || 'rows.%Next() Return ""
        Set detail = ##class(%DynamicObject).%FromJSON(rows.%Get("Detail"))
        If detail.%Get("route") '= "REJECTED" Return ""
        Set resolved = ..Timestamp(rows.%Get("RecordedAt"))
    }
    If resolved = "" Return ""
    Set summary = $EXTRACT(record.Routing_". "_..BusinessText(message)_". Assessment: "_assessment.%Get("classification"),1,400)
    Set document = {
        "source_type":"resolved_case",
        "source_id":(id),
        "source_key":(id),
        "source_scope":(record.ScenarioId),
        "source_hash":(record.Fingerprint),
        "contract_id":(record.ContractId),
        "kind":(message.%Get("kind")),
        "summary":(summary),
        "outcome":(record.Routing),
        "resolved_at":(resolved),
        "synthetic":null
    }
    If body.%GetTypeOf("synthetic") = "boolean" Do document.%Set("synthetic",body.%Get("synthetic"),"boolean")
    Return ..Seal(document)
}

ClassMethod AmendmentDocument(key As %String) As %DynamicObject [ Private ]
{
    Set record = ##class(SilentShift.Data.Reference).%OpenId(key)
    If '$ISOBJECT(record) Return ""
    Set value = ##class(%DynamicObject).%FromJSON(record.Body), priorId = value.%Get("amendment_of")
    If (value.%Get("authority") '= "approved") || (value.%GetTypeOf("amendment_of") '= "string") || (priorId = "") || ($LENGTH(priorId) > 160) Return ""
    If (value.%Get("id") '= record.ReferenceId) || (value.%Get("contract_id") '= record.ContractId) Return ""
    Set priorKey = ##class(SilentShift.Bridge).PairHash(record.ScenarioScope,priorId), prior = ##class(SilentShift.Data.Reference).%OpenId(priorKey)
    If '$ISOBJECT(prior) Return ""
    If (prior.ScenarioScope '= record.ScenarioScope) || (prior.ContractId '= record.ContractId) Return ""
    Set predecessor = ##class(%DynamicObject).%FromJSON(prior.Body)
    If (predecessor.%Get("id") '= priorId) || (predecessor.%Get("authority") '= "approved") || (predecessor.%Get("contract_id") '= record.ContractId) Return ""
    Set effective = ..Timestamp(value.%Get("effective_from")), previousFrom = ..Timestamp(predecessor.%Get("effective_from")), previousTo = ..Timestamp(predecessor.%Get("effective_to"))
    If (effective = "") || (previousFrom = "") || (previousTo = "") Return ""
    If (previousFrom = previousTo) || (previousFrom ] previousTo) Return ""
    If (previousFrom = effective) || (previousFrom ] effective) || (previousTo ] effective) Return ""
    If value.%GetTypeOf("effective_to") '= "null" {
        Set finish = ..Timestamp(value.%Get("effective_to"))
        If (finish = "") || (finish = effective) || (effective ] finish) Return ""
    }
    Set kind = $SELECT(value.%IsDefined("quantity") && value.%IsDefined("unit"):"order",value.%IsDefined("amount") && value.%IsDefined("currency"):"payment",1:"")
    If kind = "" Return ""
    Set summary = $EXTRACT("APPROVED_AMENDMENT. "_..BusinessText(value,kind)_". Effective from "_effective,1,400)
    Set document = {
        "source_type":"approved_amendment",
        "source_id":(record.ReferenceId),
        "source_key":(key),
        "source_scope":(record.ScenarioScope),
        "source_hash":(##class(SilentShift.Bridge).Hash(record.Body)),
        "contract_id":(record.ContractId),
        "kind":(kind),
        "summary":(summary),
        "outcome":"APPROVED_AMENDMENT",
        "resolved_at":(effective),
        "synthetic":null
    }
    If value.%GetTypeOf("synthetic") = "boolean" {
        Do document.%Set("synthetic",value.%Get("synthetic"),"boolean")
    } ElseIf record.ScenarioScope '= "" {
        // Scenario partitions are synthetic; unlabeled general rows stay null.
        Do document.%Set("synthetic",1,"boolean")
    }
    Return ..Seal(document)
}

ClassMethod Seal(document As %DynamicObject) As %DynamicObject [ Private ]
{
    Do document.%Set("precedent_id","prec:"_##class(SilentShift.Bridge).PairHash(document.%Get("source_type"),document.%Get("source_key")))
    Do document.%Set("content_sha256",##class(SilentShift.Bridge).Hash(document.%ToJSON()))
    Return document
}

ClassMethod IndexResolvedCase(id As %String, Output report As %String) As %Status
{
    Set report = ""
    Try {
        If $TLEVEL Return $$$ERROR($$$GeneralError,"PRECEDENT_INDEX_TRANSACTION_FORBIDDEN")
        Set document = ..CaseDocument(id)
        If '$ISOBJECT(document) Return $$$ERROR($$$GeneralError,"PRECEDENT_RESOLVED_SOURCE_REQUIRED")
        Set documents = [], ignored = documents.%Push(document)
        Return ..Persist(documents,.report)
    } Catch error {
        Return $$$ERROR($$$GeneralError,"PRECEDENT_INDEX_UNAVAILABLE")
    }
}

ClassMethod IndexAmendments(Output report As %String) As %Status
{
    Set report = ""
    Try {
        If $TLEVEL Return $$$ERROR($$$GeneralError,"PRECEDENT_INDEX_TRANSACTION_FORBIDDEN")
        Set statement = ##class(%SQL.Statement).%New(), sc = statement.%Prepare("SELECT TOP 1001 ReferenceKey FROM SilentShift_Data.Reference ORDER BY ReferenceKey")
        $$$ThrowOnError(sc)
        Set rows = statement.%Execute(), documents = [], scanned = 0
        If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_REFERENCE_READ_FAILED")
        While rows.%Next() {
            Set scanned = scanned+1
            If scanned > 1000 Throw ##class(%Exception.General).%New("PRECEDENT_REFERENCE_SCAN_LIMIT")
            Set document = ..AmendmentDocument(rows.%Get("ReferenceKey"))
            If $ISOBJECT(document) Do documents.%Push(document)
            If documents.%Size() > 100 Throw ##class(%Exception.General).%New("PRECEDENT_AMENDMENT_LIMIT")
        }
        Return ..Persist(documents,.report)
    } Catch error {
        Return $$$ERROR($$$GeneralError,"PRECEDENT_AMENDMENT_INDEX_UNAVAILABLE")
    }
}

ClassMethod IndexHistory(Output report As %String, maxCases As %Integer = 100) As %Status
{
    Set report = ""
    Try {
        If $TLEVEL || (maxCases < 1) || (maxCases > 100) Return $$$ERROR($$$GeneralError,"PRECEDENT_HISTORY_LIMIT")
        Set statement = ##class(%SQL.Statement).%New(), sc = statement.%Prepare("SELECT TOP 100 CaseId FROM SilentShift_Data.CaseRecord WHERE Routing IN ('DELIVERED','REJECTED') ORDER BY ReceivedAt DESC,CaseId DESC")
        $$$ThrowOnError(sc)
        Set rows = statement.%Execute(), documents = [], scanned = 0
        If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_HISTORY_READ_FAILED")
        While rows.%Next() {
            Quit:scanned>=maxCases
            Set scanned = scanned+1, document = ..CaseDocument(rows.%Get("CaseId"))
            If $ISOBJECT(document) Do documents.%Push(document)
        }
        Set sc = ..Persist(documents,.report)
        If $$$ISOK(sc) {
            Set detail = ##class(%DynamicObject).%FromJSON(report)
            Do detail.%Set("scanned_cases",scanned,"number"), detail.%Set("case_limit",maxCases,"number")
            Set report = detail.%ToJSON()
        }
        Return sc
    } Catch error {
        Return $$$ERROR($$$GeneralError,"PRECEDENT_HISTORY_INDEX_UNAVAILABLE")
    }
}

ClassMethod Seed(Output report As %String, maxCases As %Integer = 100) As %Status
{
    Set report = ""
    Set sc = ..IndexAmendments(.amendments)
    If $$$ISERR(sc) Return sc
    Set sc = ..IndexHistory(.history,maxCases)
    If $$$ISERR(sc) Return sc
    Set report = {
        "status":"indexed",
        "model":(..#MODEL),
        "dimensions":(..#DIMENSIONS),
        "approved_amendments":(##class(%DynamicObject).%FromJSON(amendments)),
        "resolved_cases":(##class(%DynamicObject).%FromJSON(history)),
        "decision_authority":false
    }.%ToJSON()
    Return $$$OK
}

/// Embeddings happen outside transactions/locks in batches of at most 16.
/// A per-source lock then serializes each single-statement SQL upsert.
ClassMethod Persist(documents As %DynamicArray, Output report As %String) As %Status [ Private ]
{
    Set report = "", locked = 0
    Try {
        If $TLEVEL || (documents.%Size() > 100) Return $$$ERROR($$$GeneralError,"PRECEDENT_INDEX_LIMIT")
        Set select = ##class(%SQL.Statement).%New(), sc = select.%Prepare(("SELECT PrecedentId,ContentHash,EmbeddingModel,CASE WHEN Embedding IS NULL THEN 0 ELSE 1 END AS VectorPresent FROM"_
            " SilentShift_Data.Precedent WHERE PrecedentId = ?"))
        $$$ThrowOnError(sc)
        Set insert = ##class(%SQL.Statement).%New(), sc = insert.%Prepare(("INSERT INTO SilentShift_Data.Precedent"_
            " (PrecedentId,SourceId,SourceKey,SourceType,SourceScope,SourceHash,ContractId,Kind,Summary,Outcome,ResolvedAt,IndexedAt,"_
            "ContentHash,EmbeddingModel,Synthetic,Embedding) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,TO_VECTOR(?,DOUBLE))"))
        $$$ThrowOnError(sc)
        Set update = ##class(%SQL.Statement).%New(), sc = update.%Prepare(("UPDATE SilentShift_Data.Precedent SET"_
            " SourceId=?,SourceKey=?,SourceType=?,SourceScope=?,SourceHash=?,ContractId=?,Kind=?,Summary=?,Outcome=?,ResolvedAt=?,Ind"_
            "exedAt=?,ContentHash=?,EmbeddingModel=?,Synthetic=?,Embedding=TO_VECTOR(?,DOUBLE) WHERE PrecedentId=?"))
        $$$ThrowOnError(sc)
        Set work = [], unchanged = 0, written = 0, calls = 0
        For index = 0:1:documents.%Size()-1 {
            Set document = documents.%Get(index), found = select.%Execute(document.%Get("precedent_id"))
            If found.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_READ_FAILED")
            Set same = 0
            If found.%Next() Set same = (found.%Get("ContentHash") = document.%Get("content_sha256")) && (found.%Get("EmbeddingModel") = ..#MODEL) && found.%Get("VectorPresent")
            If same { Set unchanged = unchanged+1 } Else { Do work.%Push(document) }
        }
        For first = 0:16:work.%Size()-1 {
            Set texts = [], last = $SELECT(first+15 < work.%Size():first+15,1:work.%Size()-1)
            For index = first:1:last Do texts.%Push(work.%Get(index).%Get("summary"))
            Set generated = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Embed(texts.%ToJSON(),"",..#MODEL)), vectors = generated.%Get("vectors")
            If (generated.%Get("model") '= ..#MODEL) || (generated.%Get("dimensions") '= ..#DIMENSIONS) || (vectors.%Size() '= texts.%Size()) {
                Throw ##class(%Exception.General).%New("PRECEDENT_EMBEDDING_CONTRACT")
            }
            Set calls = calls+1
            For index = first:1:last {
                Set document = work.%Get(index), id = document.%Get("precedent_id"), vector = vectors.%Get(index-first).%ToJSON()
                Lock +^SilentShift.Lock("precedent-index",id):5
                If '$TEST Throw ##class(%Exception.General).%New("PRECEDENT_INDEX_BUSY")
                Set locked = 1, found = select.%Execute(id)
                If found.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_READ_FAILED")
                Set synthetic = $SELECT(document.%GetTypeOf("synthetic")="boolean":document.%Get("synthetic"),1:"")
                Set at = ##class(SilentShift.TraceEvent).UTC()
                If found.%Next() {
                    Set result = update.%Execute(document.%Get("source_id"),document.%Get("source_key"),document.%Get("source_type"),
                        document.%Get("source_scope"),document.%Get("source_hash"),document.%Get("contract_id"),document.%Get("kind"),document.%Get("summary"),
                        document.%Get("outcome"),document.%Get("resolved_at"),at,document.%Get("content_sha256"),..#MODEL,synthetic,vector,id)
                } Else {
                    Set result = insert.%Execute(id,document.%Get("source_id"),document.%Get("source_key"),document.%Get("source_type"),
                        document.%Get("source_scope"),document.%Get("source_hash"),document.%Get("contract_id"),document.%Get("kind"),document.%Get("summary"),
                        document.%Get("outcome"),document.%Get("resolved_at"),at,document.%Get("content_sha256"),..#MODEL,synthetic,vector)
                }
                If result.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_WRITE_FAILED")
                Lock -^SilentShift.Lock("precedent-index",id)
                Set locked = 0, written = written+1
            }
        }
        Set report = {
            "status":"indexed",
            "model":(..#MODEL),
            "dimensions":(..#DIMENSIONS),
            "eligible_sources":(documents.%Size()),
            "written":(written),
            "unchanged":(unchanged),
            "local_embedding_requests":(calls),
            "decision_authority":false
        }.%ToJSON()
        Return $$$OK
    } Catch error {
        If locked Lock -^SilentShift.Lock("precedent-index",id)
        Return $$$ERROR($$$GeneralError,"PRECEDENT_PERSIST_UNAVAILABLE")
    }
}

ClassMethod Unavailable(caseId As %String) As %String
{
    Return {
        "status":"unavailable",
        "case_id":(caseId),
        "implementation":"IRIS VECTOR_COSINE",
        "model":(..#MODEL),
        "dimensions":(..#DIMENSIONS),
        "matches":[],
        "decision_authority":false,
        "failure_code":"PRECEDENT_RETRIEVAL_UNAVAILABLE"
    }.%ToJSON()
}

ClassMethod SearchForCase(body As %DynamicObject) As %String
{
    Set id = body.%Get("id")
    Try {
        Set message = body.%Get("message"), received = ..Timestamp(body.%Get("received_at"))
        If (id = "") || ($LENGTH(id) > 80) || (received = "") || '$ISOBJECT(message) Throw ##class(%Exception.General).%New("PRECEDENT_CASE_SCOPE_REQUIRED")
        Set texts = [], ignored = texts.%Push(..QueryForCase(body))
        Set generated = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Embed(texts.%ToJSON(),"",..#MODEL))
        If (generated.%Get("model") '= ..#MODEL) || (generated.%Get("dimensions") '= ..#DIMENSIONS) Throw ##class(%Exception.General).%New("PRECEDENT_EMBEDDING_CONTRACT")
        Set vector = generated.%Get("vectors").%Get(0).%ToJSON(), statement = ##class(%SQL.Statement).%New()
        Set sc = statement.%Prepare(("SELECT TOP 3"_
            " PrecedentId,SourceId,SourceType,ContractId,Kind,Summary,Outcome,Synthetic,VECTOR_COSINE(Embedding,TO_VECTOR(?,DOUBLE))"_
            " AS Similarity FROM SilentShift_Data.Precedent WHERE ContractId=? AND Kind=? AND EmbeddingModel=? AND Embedding IS NOT"_
            " NULL AND (SourceType='approved_amendment' OR (SourceType='resolved_case' AND SourceId<>? AND ResolvedAt<=?)) ORDER BY"_
            " Similarity DESC,PrecedentId"))
        $$$ThrowOnError(sc)
        Set rows = statement.%Execute(vector,message.%Get("contract_id"),message.%Get("kind"),..#MODEL,id,received), matches = []
        If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_SEARCH_FAILED")
        While rows.%Next() {
            Set rawScore = rows.%Get("Similarity")
            If '$ISVALIDNUM(rawScore) Throw ##class(%Exception.General).%New("PRECEDENT_SCORE_REQUIRED")
            Set score = rawScore+0
            If (score < -1.000001) || (score > 1.000001) Throw ##class(%Exception.General).%New("PRECEDENT_SCORE_INVALID")
            // Preserve the mathematical cosine interval at floating-point
            // epsilon only; keep the actual SQL value when normalization acts.
            If score > 1 Set score = 1
            If score < -1 Set score = -1
            Set item = {
                "precedent_id":(rows.%Get("PrecedentId")),
                "source_id":(rows.%Get("SourceId")),
                "source_type":(rows.%Get("SourceType")),
                "contract_id":(rows.%Get("ContractId")),
                "kind":(rows.%Get("Kind")),
                "summary":(rows.%Get("Summary")),
                "outcome":(rows.%Get("Outcome")),
                "decision_authority":false,
                "synthetic":null
            }
            Do item.%Set("similarity",score,"number")
            If score '= rawScore Do item.%Set("raw_similarity",rawScore,"number")
            If rows.%Get("Synthetic") '= "" Do item.%Set("synthetic",rows.%Get("Synthetic"),"boolean")
            Do matches.%Push(item)
        }
        Return {"status":"retrieved","case_id":(id),"implementation":"IRIS VECTOR_COSINE","model":(..#MODEL),"dimensions":(..#DIMENSIONS),"matches":(matches),"decision_authority":false}.%ToJSON()
    } Catch unavailable {
        Return ..Unavailable(id)
    }
}
}
