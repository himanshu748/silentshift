/// Native Workflow request associated with one newly held case/version.
Class SilentShift.Workflow.ReviewRequest Extends EnsLib.Workflow.TaskRequest
{
Property CaseId As %String(MAXLEN = 80);
Property CaseVersion As %Integer;
}
