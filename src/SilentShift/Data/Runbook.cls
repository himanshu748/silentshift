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

Storage Default
{
<Data name="RunbookDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>DocumentId</Value>
</Value>
<Value name="3">
<Value>CorpusVersion</Value>
</Value>
<Value name="4">
<Value>Title</Value>
</Value>
<Value name="5">
<Value>Content</Value>
</Value>
<Value name="6">
<Value>ContentHash</Value>
</Value>
<Value name="7">
<Value>EmbeddingModel</Value>
</Value>
<Value name="8">
<Value>Embedding</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.RunbookD</DataLocation>
<DefaultData>RunbookDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.RunbookD</IdLocation>
<IndexLocation>^SilentShift.Data.RunbookI</IndexLocation>
<StreamLocation>^SilentShift.Data.RunbookS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
