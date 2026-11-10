/// At-most-once receipt for the included IRIS destination simulator only.
Class SilentShift.Data.Delivery Extends %Persistent
{
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property DeliveredAt As %String(MAXLEN = 40);
Property Payload As %String(MAXLEN = 131072);
Property PolicyVersion As %String(MAXLEN = 80);
Property CaseVersion As %Integer;
Index DeliveryUnique On CaseId [ IdKey, Unique ];

Storage Default
{
<Data name="DeliveryDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>DeliveredAt</Value>
</Value>
<Value name="3">
<Value>Payload</Value>
</Value>
<Value name="4">
<Value>PolicyVersion</Value>
</Value>
<Value name="5">
<Value>CaseVersion</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.DeliveryD</DataLocation>
<DefaultData>DeliveryDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.DeliveryD</IdLocation>
<IndexLocation>^SilentShift.Data.DeliveryI</IndexLocation>
<StreamLocation>^SilentShift.Data.DeliveryS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
