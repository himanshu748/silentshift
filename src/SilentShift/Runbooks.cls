Include %occStatus

/// Native vector retrieval for supporting procedures; it never selects the
/// authoritative contracts and never decides a transaction's permitted route.
Class SilentShift.Runbooks Extends %RegisteredObject
{
ClassMethod Seed(base As %String = "", model As %String = "") As %Status
{
    Set initialLevel = $TLEVEL
    Try {
        Set corpus = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).RunbookJSON())
        Set documents = corpus.%Get("documents"), texts = []
        If (documents.%Size() < 1) || (documents.%Size() > 16) Return $$$ERROR($$$GeneralError, "RUNBOOK_CORPUS_LIMIT")
        For index = 0:1:documents.%Size()-1 {
            Set document = documents.%Get(index)
            Do texts.%Push(document.%Get("title")_". "_document.%Get("text"))
        }
        // Embedding work happens before a transaction and never in callbacks.
        Set generated = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Embed(texts.%ToJSON(), base, model))
        Set vectors = generated.%Get("vectors")
        Set select = ##class(%SQL.Statement).%New()
        Set sc = select.%Prepare("SELECT ID FROM SilentShift_Data.Runbook WHERE DocumentId = ?")
        $$$ThrowOnError(sc)
        Set insert = ##class(%SQL.Statement).%New()
        Set sc = insert.%Prepare("INSERT INTO SilentShift_Data.Runbook (DocumentId, CorpusVersion, Title, Content, ContentHash, EmbeddingModel, Embedding) VALUES (?, ?, ?, ?, ?, ?, TO_VECTOR(?,DOUBLE))")
        $$$ThrowOnError(sc)
        Set update = ##class(%SQL.Statement).%New()
        Set sc = update.%Prepare("UPDATE SilentShift_Data.Runbook SET CorpusVersion = ?, Title = ?, Content = ?, ContentHash = ?, EmbeddingModel = ?, Embedding = TO_VECTOR(?,DOUBLE) WHERE DocumentId = ?")
        $$$ThrowOnError(sc)
        TSTART
        For index = 0:1:documents.%Size()-1 {
            Set document = documents.%Get(index), id = document.%Get("id"), text = document.%Get("text")
            Set digest = ##class(SilentShift.Bridge).Hash(document.%ToJSON())
            Set vector = vectors.%Get(index).%ToJSON(), found = select.%Execute(id)
            If found.%SQLCODE < 0 Throw ##class(%Exception.General).%New("RUNBOOK_SQL_FAILED")
            If found.%Next() {
                Set result = update.%Execute(corpus.%Get("version"), document.%Get("title"), text, digest, generated.%Get("model"), vector, id)
            } Else {
                Set result = insert.%Execute(id, corpus.%Get("version"), document.%Get("title"), text, digest, generated.%Get("model"), vector)
            }
            If result.%SQLCODE < 0 Throw ##class(%Exception.General).%New("RUNBOOK_SQL_FAILED")
        }
        TCOMMIT
        Return $$$OK
    } Catch error {
        If $TLEVEL > initialLevel TROLLBACK 1
        Return $$$ERROR($$$GeneralError, "RUNBOOK_SEED_FAILED")
    }
}

ClassMethod Search(query As %String, base As %String = "", model As %String = "") As %String
{
    If (query = "") || ($LENGTH(query) > 1024) Throw ##class(%Exception.General).%New("RUNBOOK_QUERY_LIMIT")
    Set texts = [], ignored = texts.%Push(query)
    Set generated = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Embed(texts.%ToJSON(), base, model))
    Set vector = generated.%Get("vectors").%Get(0).%ToJSON()
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT TOP 2 DocumentId, CorpusVersion, Title, Content, ContentHash, EmbeddingModel, VECTOR_COSINE(Embedding,TO_VECTOR(?,DOUBLE)) AS Similarity FROM SilentShift_Data.Runbook WHERE EmbeddingModel = ? ORDER BY Similarity DESC, DocumentId")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(vector, generated.%Get("model")), matches = []
    If rows.%SQLCODE < 0 Throw ##class(%Exception.General).%New("RUNBOOK_SEARCH_FAILED")
    While rows.%Next() {
        Set score = rows.%Get("Similarity") + 0
        If score >= 0.35 {
            Set item = {"id": (rows.%Get("DocumentId")), "title": (rows.%Get("Title")), "guidance": (rows.%Get("Content")), "corpus_version": (rows.%Get("CorpusVersion")), "content_sha256": (rows.%Get("ContentHash")), "embedding_model": (rows.%Get("EmbeddingModel")), "decision_authority": false}
            Do item.%Set("similarity", score, "number")
            Do matches.%Push(item)
        }
    }
    Set result = {"status": "retrieved", "implementation": "IRIS VECTOR_COSINE", "model": (generated.%Get("model")), "dimensions": 384, "minimum_similarity": 0.35, "matches": (matches), "decision_authority": false, "scope": "Supporting procedures only; approved contract evidence and deterministic policy remain authoritative."}
    Return result.%ToJSON()
}

ClassMethod QueryForCase(body As %DynamicObject) As %String
{
    Set assessment = body.%Get("assessment"), message = body.%Get("message")
    Set query = message.%Get("kind")_" investigation "_assessment.%Get("classification")
    Set findings = assessment.%Get("findings")
    For index = 0:1:findings.%Size()-1 {
        Set finding = findings.%Get(index)
        Set query = query_" "_finding.%Get("field")_" "_finding.%Get("code")
    }
    // Query only structured finding codes, never partner notes/instructions.
    Return $EXTRACT($REPLACE($ZCONVERT(query, "L"), "_", " "), 1, 1024)
}
}
