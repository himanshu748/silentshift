/// Control: the same shape with a Python syntax error (ERROR #2605).
Class ZProbe.RejectedSyntax
{

ClassMethod Good() As %String
{
    quit "Good() ran"
}

ClassMethod Bad() As %String [ Language = python ]
{
    return (
}

}
