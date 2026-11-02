/// At-most-once receipt for the included IRIS destination simulator only.
Class SilentShift.Data.Delivery Extends %Persistent
{
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property DeliveredAt As %String(MAXLEN = 40);
Property Payload As %String(MAXLEN = 131072);
Property PolicyVersion As %String(MAXLEN = 80);
Property CaseVersion As %Integer;
Index DeliveryUnique On CaseId [ IdKey, Unique ];
}
