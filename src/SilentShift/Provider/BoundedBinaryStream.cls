Include %occStatus

/// Temporary response sink with a hard byte cap before each allocation. A
/// caller that ignores Write's error still cannot append more response bytes.
Class SilentShift.Provider.BoundedBinaryStream Extends %Stream.TmpBinary
{
Property ByteLimit As %Integer [ InitialExpression = 262144 ];
Property Exceeded As %Boolean [ InitialExpression = 0 ];

Method Write(data As %String = "") As %Status
{
    If ..Exceeded Return $$$ERROR($$$GeneralError,"PROVIDER_RESPONSE_BOUNDS")
    If (..ByteLimit < 1) || ((..Size+$LENGTH(data)) > ..ByteLimit) {
        Set ..Exceeded = 1
        Return $$$ERROR($$$GeneralError,"PROVIDER_RESPONSE_BOUNDS")
    }
    Return ##super(data)
}
}
