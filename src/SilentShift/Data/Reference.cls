Class SilentShift.Data.Reference Extends %Persistent
{
Property ReferenceKey As %String(MAXLEN = 64) [ Required ];
Property ReferenceId As %String(MAXLEN = 160) [ Required ];
Property ScenarioScope As %String(MAXLEN = 80);
Property ContractId As %String(MAXLEN = 160) [ Required ];
Property Body As %String(MAXLEN = 32768);
Index ReferenceKeyIndex On ReferenceKey [ IdKey, Unique ];
Index ReferenceLookup On (ScenarioScope, ContractId);

Storage Default
{
<Data name="ReferenceDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>ReferenceId</Value>
</Value>
<Value name="3">
<Value>ScenarioScope</Value>
</Value>
<Value name="4">
<Value>ContractId</Value>
</Value>
<Value name="5">
<Value>Body</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.ReferenceD</DataLocation>
<DefaultData>ReferenceDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.ReferenceD</IdLocation>
<IndexLocation>^SilentShift.Data.ReferenceI</IndexLocation>
<StreamLocation>^SilentShift.Data.ReferenceS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
