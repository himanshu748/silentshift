/// Application code only appends rows; no update/delete endpoint is provided.
Class SilentShift.Data.AuditEvent Extends %Persistent
{
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property Kind As %String(MAXLEN = 80) [ Required ];
Property RecordedAt As %String(MAXLEN = 40);
Property Detail As %String(MAXLEN = 32768);
Index CaseLookup On CaseId;

Storage Default
{
<Data name="AuditEventDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>CaseId</Value>
</Value>
<Value name="3">
<Value>Kind</Value>
</Value>
<Value name="4">
<Value>RecordedAt</Value>
</Value>
<Value name="5">
<Value>Detail</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.AuditEventD</DataLocation>
<DefaultData>AuditEventDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.AuditEventD</IdLocation>
<IndexLocation>^SilentShift.Data.AuditEventI</IndexLocation>
<StreamLocation>^SilentShift.Data.AuditEventS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
