/// Repro: an argument skipped in the call does not get its declared default in a Python method.
Class ZProbe.SkippedArg
{

ClassMethod Py(a As %String = "A", b As %String = "B") As %String [ Language = python ]
{
    return repr(a) + "|" + repr(b)
}

ClassMethod OS(a As %String = "A", b As %String = "B") As %String
{
    quit "'"_a_"'|'"_b_"'"
}

ClassMethod Run()
{
    write "python       Py()     -> ", ..Py(), !
    write "python       Py(,""Z"") -> ", ..Py(, "Z"), !
    write "python       Py(""X"",) -> ", ..Py("X", ), !
    write "objectscript OS(,""Z"") -> ", ..OS(, "Z"), !
    write "objectscript OS(""X"",) -> ", ..OS("X", ), !
}

}
