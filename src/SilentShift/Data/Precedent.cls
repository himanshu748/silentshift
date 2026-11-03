/// Actual resolved cases and approved amendments, never release authority.
Class SilentShift.Data.Precedent Extends %Persistent
{
Property PrecedentId As %String(MAXLEN = 80) [ Required ];
Property SourceId As %String(MAXLEN = 160) [ Required ];
Property SourceKey As %String(MAXLEN = 160) [ Required ];
Property SourceType As %String(MAXLEN = 24) [ Required ];
Property SourceScope As %String(MAXLEN = 80);
Property SourceHash As %String(MAXLEN = 64) [ Required ];
Property ContractId As %String(MAXLEN = 160) [ Required ];
Property Kind As %String(MAXLEN = 16) [ Required ];
Property Summary As %String(MAXLEN = 400) [ Required ];
Property Outcome As %String(MAXLEN = 24) [ Required ];
Property ResolvedAt As %String(MAXLEN = 40) [ Required ];
Property IndexedAt As %String(MAXLEN = 40) [ Required ];
Property ContentHash As %String(MAXLEN = 64) [ Required ];
Property EmbeddingModel As %String(MAXLEN = 120) [ Required ];
Property Synthetic As %Boolean;
Property Embedding As %Library.Vector(DATATYPE = "DOUBLE", LEN = 384);
Index PrecedentKey On PrecedentId [ IdKey, Unique ];
Index RetrievalScope On (ContractId, Kind, EmbeddingModel);
Index SourceLookup On (SourceType, SourceKey) [ Unique ];
}
