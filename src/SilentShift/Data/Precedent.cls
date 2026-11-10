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

Storage Default
{
<Data name="PrecedentDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>SourceId</Value>
</Value>
<Value name="3">
<Value>SourceKey</Value>
</Value>
<Value name="4">
<Value>SourceType</Value>
</Value>
<Value name="5">
<Value>SourceScope</Value>
</Value>
<Value name="6">
<Value>SourceHash</Value>
</Value>
<Value name="7">
<Value>ContractId</Value>
</Value>
<Value name="8">
<Value>Kind</Value>
</Value>
<Value name="9">
<Value>Summary</Value>
</Value>
<Value name="10">
<Value>Outcome</Value>
</Value>
<Value name="11">
<Value>ResolvedAt</Value>
</Value>
<Value name="12">
<Value>IndexedAt</Value>
</Value>
<Value name="13">
<Value>ContentHash</Value>
</Value>
<Value name="14">
<Value>EmbeddingModel</Value>
</Value>
<Value name="15">
<Value>Synthetic</Value>
</Value>
<Value name="16">
<Value>Embedding</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.PrecedentD</DataLocation>
<DefaultData>PrecedentDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.PrecedentD</IdLocation>
<IndexLocation>^SilentShift.Data.PrecedentI</IndexLocation>
<StreamLocation>^SilentShift.Data.PrecedentS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
