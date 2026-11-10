Include %occStatus

/// Evaluation-only: keep real retrieval, but do not learn from evaluated outcomes.
/// Never included in the IPM manifest or normal production definition.
Class SilentShift.Test.HeldoutPrecedents Extends SilentShift.Operation.Precedents
{
Method Execute(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    If request.Action = "index_precedent" {
        Set response=##class(SilentShift.Reply).%New()
        Set response.BodyJSON={"status":"skipped","reason":"evaluation-outcomes-are-not-precedents","decision_authority":false}.%ToJSON()
        Set ^SilentShiftHeldoutIndexSkips(request.CaseId)=1
        Return $$$OK
    }
    Return ##super(request,.response)
}
}
