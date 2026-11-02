/// Application code only appends rows; no update/delete endpoint is provided.
Class SilentShift.Data.AuditEvent Extends %Persistent
{
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property Kind As %String(MAXLEN = 80) [ Required ];
Property RecordedAt As %String(MAXLEN = 40);
Property Detail As %String(MAXLEN = 32768);
Index CaseLookup On CaseId;
}
