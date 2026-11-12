Class BugProbe.Tools Extends %AI.Tool
{
Method Echo(text As %String) As %String { Return text }
Method Optional(n As %Integer = 7, word As %String = "fallback") As %DynamicObject
{ Return {"n":(n),"word":(word)} }
Method ArrayEcho(items As %DynamicArray) As %DynamicArray { Return items }
Method ObjectEcho(value As %DynamicObject) As %DynamicObject { Return value }
Method BinaryEcho(data As %Binary) As %Binary { Return data }
Method ReadStream(data As %Stream.GlobalCharacter) As %String { Return data.Read() }
Method ReturnStream() As %Stream.GlobalCharacter
{ Set s=##class(%Stream.GlobalCharacter).%New() Do s.Write("hello stream") Do s.Rewind() Return s }
Query QueryDefault(value As %String = "fallback") As %SQLQuery [ SqlProc ]
{ SELECT :value AS Value }
}
