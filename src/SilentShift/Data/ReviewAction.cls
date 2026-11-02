Class SilentShift.Data.ReviewAction Extends %Persistent
{
Property ReviewKey As %String(MAXLEN = 64) [ Required ];
Property CaseId As %String(MAXLEN = 80) [ Required ];
Property Fingerprint As %String(MAXLEN = 64);
Property Body As %String(MAXLEN = 32768);
Index ReviewUnique On ReviewKey [ IdKey, Unique ];
Index CaseLookup On CaseId;
}
