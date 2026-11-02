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
}
