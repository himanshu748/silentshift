Class SilentShift.Data.ReviewAction Extends %Persistent
{
Property ReviewKey As %String(MAXLEN = 64) [ Required ];
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property Fingerprint As %String(MAXLEN = 64);
Property Body As %String(MAXLEN = 32768);
Index ReviewUnique On ReviewKey [ IdKey, Unique ];
Index CaseLookup On CaseId;

Storage Default
{
<Data name="ReviewActionDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>CaseId</Value>
</Value>
<Value name="3">
<Value>Fingerprint</Value>
</Value>
<Value name="4">
<Value>Body</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.ReviewActionD</DataLocation>
<DefaultData>ReviewActionDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.ReviewActionD</IdLocation>
<IndexLocation>^SilentShift.Data.ReviewActionI</IndexLocation>
<StreamLocation>^SilentShift.Data.ReviewActionS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
