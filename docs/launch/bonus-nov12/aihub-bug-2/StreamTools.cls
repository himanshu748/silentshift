Class BugProbe.StreamTools Extends %AI.Tool
{
/// Control: the same payload, returned as a string.
Method ReturnText() As %String
{
    Return "Approved amendment: 1 CASE = 12 EA."
}
/// Return the complete evidence text as a character stream.
Method ReturnStream() As %Stream.GlobalCharacter
{
    Set stream = ##class(%Stream.GlobalCharacter).%New()
    Do stream.Write(..ReturnText())
    Do stream.Rewind()
    Return stream
}
/// Read an evidence stream, received from the tool caller.
Method ReadStream(data As %Stream.GlobalCharacter) As %String
{
    Return data.Read()
}
}
