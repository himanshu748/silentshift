/// Authored procedures provide context, never independent contract authority.
Class SilentShift.Data.Runbook Extends %Persistent
{
Property DocumentId As %String(MAXLEN = 100) [ Required ];
Property CorpusVersion As %String(MAXLEN = 80) [ Required ];
Property Title As %String(MAXLEN = 160) [ Required ];
Property Content As %String(MAXLEN = 1800) [ Required ];
Property ContentHash As %String(MAXLEN = 64) [ Required ];
Property EmbeddingModel As %String(MAXLEN = 120) [ Required ];
Property Embedding As %Library.Vector(DATATYPE = "DOUBLE", LEN = 384);
Index ByDocument On DocumentId [ Unique ];
}
