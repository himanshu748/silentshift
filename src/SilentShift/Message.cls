Class SilentShift.Message Extends Ens.Request
{
Property CaseId As %String(MAXLEN = 80);
Property Action As %String(MAXLEN = 32) [ InitialExpression = "process" ];
}
