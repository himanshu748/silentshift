/// Actual measured evaluation artifacts only; no fixture model responses.
Class SilentShift.Data.Evaluation Extends %Persistent
{
Property RunId As %String(MAXLEN = 80) [ Required ];
Property CreatedAt As %String(MAXLEN = 40) [ Required ];
Property CaseIds As %String(MAXLEN = 2000) [ Required ];
Property Body As %String(MAXLEN = 3641144) [ Required ];
Index RunIdKey On RunId [ IdKey, Unique ];
}
