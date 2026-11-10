/// Native host response. Internal routing acknowledgments are compact; Partner returns the full case.
Class SilentShift.Reply Extends Ens.Response
{
Property BodyJSON As %String(MAXLEN = 1048576);
Property RecommendationJSON As %String(MAXLEN = 8192);
Property MetadataJSON As %String(MAXLEN = 32768);
}
