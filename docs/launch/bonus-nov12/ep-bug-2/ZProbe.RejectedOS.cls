/// Control: the same shape with an ObjectScript compile error.
Class ZProbe.RejectedOS
{

ClassMethod Good() As %String
{
    quit "Good() ran"
}

ClassMethod Bad() As %String
{
    quit (
}

}
