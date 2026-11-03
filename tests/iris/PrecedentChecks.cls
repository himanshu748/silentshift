Include %occStatus

/// Actual vector/source inspection only: no embedding, LLM, indexing or writes.
Class SilentShift.Test.PrecedentChecks Extends %RegisteredObject
{
ClassMethod Contracts() As %String
{
    Set body = {"message":{"kind":"order","contract_id":"C-1","quantity":"20","unit":"CASE","notes":"UNTRUSTED_PRECEDENT_MARKER"}}
    Set query = ##class(SilentShift.Precedents).QueryForCase(body), unavailable = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Precedents).Unavailable("synthetic-case"))
    Set checks = {"query_has_structured_values":false,"query_excludes_partner_notes":false,"query_is_bounded":false,"unavailable_is_non_authority":false,"unknown_source_rejected":false}
    Do checks.%Set("query_has_structured_values",(query [ "20") && (query [ "CASE"),"boolean")
    Do checks.%Set("query_excludes_partner_notes",'(query [ "UNTRUSTED_PRECEDENT_MARKER"),"boolean")
    Do checks.%Set("query_is_bounded",$LENGTH(query)<=320,"boolean")
    Do checks.%Set("unavailable_is_non_authority",(unavailable.%Get("status")="unavailable") && 'unavailable.%Get("decision_authority") && (unavailable.%Get("matches").%Size()=0),"boolean")
    Do checks.%Set("unknown_source_rejected",'$ISOBJECT(##class(SilentShift.Precedents).SourceDocument("untrusted_type","unknown")),"boolean")
    Return checks.%ToJSON()
}

ClassMethod Row(id As %String) As %DynamicObject [ Private ]
{
    Set row = ##class(SilentShift.Data.Precedent).%OpenId(id)
    If '$ISOBJECT(row) Return {"precedent_id":(id),"source_binding_valid":false}
    Set source = ##class(SilentShift.Precedents).SourceDocument(row.SourceType,row.SourceKey), valid = $ISOBJECT(source)
    If valid {
        For field = "precedent_id", "source_id", "source_key", "source_type", "source_scope", "source_hash", "contract_id", "kind", "summary", "outcome", "resolved_at", "content_sha256" {
            Set property = $CASE(field,"precedent_id":"PrecedentId","source_id":"SourceId","source_key":"SourceKey","source_type":"SourceType","source_scope":"SourceScope","source_hash":"SourceHash","contract_id":"ContractId","kind":"Kind","summary":"Summary","outcome":"Outcome","resolved_at":"ResolvedAt","content_sha256":"ContentHash")
            If source.%Get(field) '= $PROPERTY(row,property) Set valid = 0
        }
    }
    Set result = {"precedent_id":(row.PrecedentId),"source_id":(row.SourceId),"source_type":(row.SourceType),"source_scope":(row.SourceScope),"source_hash":(row.SourceHash),"contract_id":(row.ContractId),"kind":(row.Kind),"summary":(row.Summary),"outcome":(row.Outcome),"resolved_at":(row.ResolvedAt),"indexed_at":(row.IndexedAt),"content_sha256":(row.ContentHash),"embedding_model":(row.EmbeddingModel),"synthetic":null,"source_binding_valid":false}
    Do result.%Set("source_binding_valid",valid,"boolean")
    If row.Synthetic '= "" Do result.%Set("synthetic",row.Synthetic,"boolean")
    Return result
}

ClassMethod Corpus() As %String
{
    Set statement = ##class(%SQL.Statement).%New(), sc = statement.%Prepare("SELECT TOP 201 PrecedentId,VECTOR_COSINE(Embedding,Embedding) AS SelfSimilarity FROM SilentShift_Data.Precedent ORDER BY PrecedentId")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(), items = [], count = 0
    If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_CORPUS_READ_FAILED")
    While rows.%Next() {
        Set count = count+1
        If count > 200 Throw ##class(%Exception.General).%New("PRECEDENT_INSPECTION_LIMIT")
        Set item = ..Row(rows.%Get("PrecedentId")), rawScore = rows.%Get("SelfSimilarity")
        Do item.%Set("native_self_similarity",rawScore+0,"number")
        Do item.%Set("native_nonzero_vector",$ISVALIDNUM(rawScore) && (rawScore>=0.999999) && (rawScore<=1.000001),"boolean")
        Do items.%Push(item)
    }
    Set property = ##class(%Dictionary.CompiledProperty).%OpenId("SilentShift.Data.Precedent||Embedding")
    If '$ISOBJECT(property) Throw ##class(%Exception.General).%New("PRECEDENT_VECTOR_METADATA_REQUIRED")
    Return {"items":(items),"count":(count),"actual_property_type":(property.Type),"dimensions":(property.Parameters.GetAt("LEN")+0),"datatype":(property.Parameters.GetAt("DATATYPE")),"model":"all-minilm:22m","embedding_requests":0,"model_calls":0}.%ToJSON()
}

ClassMethod InspectCase(id As %String) As %String
{
    Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
    If '$ISOBJECT(record) Throw ##class(%Exception.General).%New("PRECEDENT_CASE_REQUIRED")
    Set before = record.Body, body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), context = body.%Get("precedent_context"), sources = [], headers = []
    If $ISOBJECT(context) {
        Set matches = context.%Get("matches")
        For index = 0:1:matches.%Size()-1 Do sources.%Push(..Row(matches.%Get(index).%Get("precedent_id")))
    }
    Set statement = ##class(%SQL.Statement).%New(), sc = statement.%Prepare("SELECT TOP 100 ID,SourceConfigName,TargetConfigName,MessageBodyClassName,MessageBodyId FROM Ens.MessageHeader WHERE SessionId=? AND (SourceConfigName='Precedents' OR TargetConfigName='Precedents') ORDER BY ID")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(+body.%Get("trace_id"))
    If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("PRECEDENT_HEADER_READ_FAILED")
    While rows.%Next() {
        Do headers.%Push({"id":(rows.%Get("ID")),"source":(rows.%Get("SourceConfigName")),"target":(rows.%Get("TargetConfigName")),"body_class":(rows.%Get("MessageBodyClassName")),"body_id":(rows.%Get("MessageBodyId"))})
    }
    Set sc = record.%Reload()
    $$$ThrowOnError(sc)
    Set agent = body.%Get("agent"), result = {"case_id":(id),"trace_id":(body.%Get("trace_id")),"routing":(body.%Get("routing")),"delivery_count":(body.%Get("delivery_count")),"context":(context),"source_rows":(sources),"native_headers":(headers),"case_unchanged":false,"embedding_requests":0,"model_calls":0}
    If $ISOBJECT(agent) Do result.%Set("tool_reads",agent.%Get("tool_reads"))
    Do result.%Set("case_unchanged",record.Body=before,"boolean")
    Return result.%ToJSON()
}

/// A real retrieved DELIVERED case is deliberately misleading for a current
/// critical contradiction. Even ALLOW with current valid citations is vetoed.
ClassMethod MisleadingCannotRelease(id As %String) As %String
{
    Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
    If '$ISOBJECT(record) Throw ##class(%Exception.General).%New("PRECEDENT_CASE_REQUIRED")
    Set before = record.Body, body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), assessment = body.%Get("assessment"), context = body.%Get("precedent_context"), delivered = []
    If $ISOBJECT(context) {
        Set matches = context.%Get("matches")
        For index = 0:1:matches.%Size()-1 {
            Set item = matches.%Get(index)
            If (item.%Get("source_type")="resolved_case") && (item.%Get("outcome")="DELIVERED") Do delivered.%Push(item.%Get("precedent_id"))
        }
    }
    Set proposal = {"decision":"ALLOW","evidence_ids":(assessment.%Get("evidence_ids")),"explanation":"A similar historical case was delivered; deliberately test the policy veto.","uncertainty":0}
    Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessment.%ToJSON(),proposal.%ToJSON()))
    Set sc = record.%Reload()
    $$$ThrowOnError(sc)
    Set checks = {"actual_misleading_delivered_precedent":false,"current_case_is_critical":false,"allow_schema_and_citations_valid":false,"deterministic_veto":false,"actual_case_held_without_delivery":false,"case_unchanged":false}
    Do checks.%Set("actual_misleading_delivered_precedent",delivered.%Size()>0,"boolean")
    Do checks.%Set("current_case_is_critical",assessment.%Get("critical"),"boolean")
    Set gates = policy.%Get("checks")
    For index = 0:1:gates.%Size()-1 {
        Set gate = gates.%Get(index)
        If gate.%Get("code") = "RECOMMENDATION_VALID" Do checks.%Set("allow_schema_and_citations_valid",gate.%Get("passed"),"boolean")
    }
    Do checks.%Set("deterministic_veto",(policy.%Get("decision")="QUARANTINE") && 'policy.%Get("downstream_permitted"),"boolean")
    Do checks.%Set("actual_case_held_without_delivery",(body.%Get("routing")="QUARANTINED") && (body.%Get("delivery_count")=0),"boolean")
    Do checks.%Set("case_unchanged",record.Body=before,"boolean")
    Return {"case_id":(id),"misleading_precedent_ids":(delivered),"proposal":(proposal),"actual_policy":(policy),"checks":(checks),"embedding_requests":0,"model_calls":0}.%ToJSON()
}
}
