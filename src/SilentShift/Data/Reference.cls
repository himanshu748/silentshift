Class SilentShift.Data.Reference Extends %Persistent
{
Property ReferenceKey As %String(MAXLEN = 64) [ Required ];
Property ReferenceId As %String(MAXLEN = 160) [ Required ];
Property ScenarioScope As %String(MAXLEN = 80);
Property ContractId As %String(MAXLEN = 160) [ Required ];
Property Body As %String(MAXLEN = 32768);
Index ReferenceKeyIndex On ReferenceKey [ IdKey, Unique ];
Index ReferenceLookup On (ScenarioScope, ContractId);
}
