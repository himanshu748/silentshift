/// Repro: the compiler rejects this class (ERROR #2607), but the class is still installed and runnable.
Class ZProbe.Rejected
{

ClassMethod Good() As %String
{
    quit "Good() ran"
}

ClassMethod Bad(Output x As %String) As %String [ Language = python ]
{
    return "Bad() ran"
}

}
