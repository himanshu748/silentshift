Class SilentShift.Data.CaseRecord Extends %Persistent
{
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property EventKey As %String(MAXLEN = 64) [ Required ];
Property Fingerprint As %String(MAXLEN = 64) [ Required ];
Property Source As %String(MAXLEN = 160);
Property EventId As %String(MAXLEN = 160);
Property ContractId As %String(MAXLEN = 160);
Property ScenarioId As %String(MAXLEN = 80);
Property ReceivedAt As %String(MAXLEN = 40);
Property RawPayload As %String(MAXLEN = 131072);
Property Body As %String(MAXLEN = 1048576);
Property ReferenceSnapshot As %String(MAXLEN = 131072);
Property Version As %Integer [ InitialExpression = 1 ];
Property Routing As %String(MAXLEN = 24) [ InitialExpression = "PROCESSING" ];
Index CaseKey On CaseId [ IdKey, Unique ];
Index EventUnique On EventKey [ Unique ];
Index ContractLookup On ContractId;
Index RoutingLookup On Routing;
Index ReceivedLookup On ReceivedAt;

Storage Default
{
<Data name="CaseRecordDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>EventKey</Value>
</Value>
<Value name="3">
<Value>Fingerprint</Value>
</Value>
<Value name="4">
<Value>Source</Value>
</Value>
<Value name="5">
<Value>EventId</Value>
</Value>
<Value name="6">
<Value>ContractId</Value>
</Value>
<Value name="7">
<Value>ScenarioId</Value>
</Value>
<Value name="8">
<Value>ReceivedAt</Value>
</Value>
<Value name="9">
<Value>RawPayload</Value>
</Value>
<Value name="10">
<Value>Body</Value>
</Value>
<Value name="11">
<Value>ReferenceSnapshot</Value>
</Value>
<Value name="12">
<Value>Version</Value>
</Value>
<Value name="13">
<Value>Routing</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.CaseRecordD</DataLocation>
<DefaultData>CaseRecordDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.CaseRecordD</IdLocation>
<IndexLocation>^SilentShift.Data.CaseRecordI</IndexLocation>
<StreamLocation>^SilentShift.Data.CaseRecordS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
