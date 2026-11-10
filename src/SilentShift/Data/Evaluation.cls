/// Actual measured evaluation artifacts only; no fixture model responses.
Class SilentShift.Data.Evaluation Extends %Persistent
{
Property RunId As %String(MAXLEN = 80) [ Required ];
Property CreatedAt As %String(MAXLEN = 40) [ Required ];
Property CaseIds As %String(MAXLEN = 2000) [ Required ];
Property Body As %String(MAXLEN = 3641144) [ Required ];
Index RunIdKey On RunId [ IdKey, Unique ];

Storage Default
{
<Data name="EvaluationDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>CreatedAt</Value>
</Value>
<Value name="3">
<Value>CaseIds</Value>
</Value>
<Value name="4">
<Value>Body</Value>
</Value>
</Data>
<DataLocation>^SilentShift.Data.EvaluationD</DataLocation>
<DefaultData>EvaluationDefaultData</DefaultData>
<IdLocation>^SilentShift.Data.EvaluationD</IdLocation>
<IndexLocation>^SilentShift.Data.EvaluationI</IndexLocation>
<StreamLocation>^SilentShift.Data.EvaluationS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
