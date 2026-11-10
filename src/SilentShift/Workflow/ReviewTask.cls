Include %occStatus

/// Actual native Workflow task. Completion requires an existing authorized
/// SilentShift review receipt; native worklist actions cannot bypass policy.
Class SilentShift.Workflow.ReviewTask Extends EnsLib.Workflow.TaskResponse
{
Property CaseId As %String(MAXLEN = 80);
Property CreatedCaseVersion As %Integer;
Property ReviewedCaseVersion As %Integer;
Property ReviewReason As %String(MAXLEN = 2000);
Property ReviewIdempotencyKey As %String(MAXLEN = 160);

Method OnNewTask(pRequest As EnsLib.Workflow.TaskRequest) As %Status
{
    Set locked = 0
    Try {
        If 'pRequest.%IsA("SilentShift.Workflow.ReviewRequest") Return $$$ERROR($$$GeneralError, "Workflow request type is invalid")
        Set id = pRequest.CaseId
        Lock +^SilentShift.Lock("workflow", id):5
        If '$TEST Return $$$ERROR($$$GeneralError, "Workflow creation is busy")
        Set locked = 1
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        Set existing = body.%Get("workflow")
        Set ..CaseId = id, ..CreatedCaseVersion = pRequest.CaseVersion
        If $ISOBJECT(existing), existing.%Get("task_id") '= "" {
            // Duplicate dispatch has no new worklist or routing authority.
            Set sc = ..CompleteTask("DUPLICATE_SUPPRESSED")
            Lock -^SilentShift.Lock("workflow", id)
            Return sc
        }
        If (body.%Get("routing") '= "REVIEW") && (body.%Get("routing") '= "QUARANTINED") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Workflow requires a held case"))
        TSTART
        Set sc = ##super(pRequest)
        $$$ThrowOnError(sc)
        Set sc = ..%Save()
        $$$ThrowOnError(sc)
        Set taskId = ..%Id(), reviewer = $SYSTEM.Util.GetEnviron("SILENTSHIFT_IRIS_USERNAME"), worklistId = ""
        &sql(SELECT ID INTO :worklistId FROM EnsLib_Workflow.Worklist WHERE Task = :taskId AND UserName = :reviewer)
        If (SQLCODE '= 0) || (worklistId = "") Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Native reviewer worklist was not created"))
        Set data = {"engine": "native-iris-workflow", "status": "pending", "role": "ReviewWorklist", "task_id": (taskId), "request_id": (pRequest.%Id()), "worklist_id": (worklistId), "created_case_version": (..CreatedCaseVersion), "created_at": (##class(SilentShift.TraceEvent).UTC()), "source_session_id": (..%TaskStatus.SessionId), "completion_received": false}
        Set sc = ##class(SilentShift.Store).SetWorkflow(id, data.%ToJSON(), "workflow_task_created")
        $$$ThrowOnError(sc)
        TCOMMIT
        Lock -^SilentShift.Lock("workflow", id)
        Return $$$OK
    } Catch error {
        If $TLEVEL TROLLBACK
        If locked Lock -^SilentShift.Lock("workflow", id)
        Return $$$ERROR($$$GeneralError, "Native workflow task creation failed")
    }
}

Method OnAction(pAction As %String) As %Status
{
    Set sc = ##class(SilentShift.Workflow.Support).AuthorizeCompletion(..CaseId, ..%Id(), ..%TaskStatus.AssignedTo, pAction)
    If $$$ISERR(sc) Return sc
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(..CaseId)), review = body.%Get("review")
    Set ..ReviewReason = review.%Get("reason"), ..ReviewIdempotencyKey = review.%Get("idempotency_key")
    Set ..ReviewedCaseVersion = review.%Get("expected_version")
    If ..%TaskStatus.IsComplete Return $$$OK
    Return ..CompleteTask($ZCONVERT(pAction, "U"))
}

Storage Default
{
<Data name="ReviewTaskDefaultData">
<Subscript>"ReviewTask"</Subscript>
<Value name="1">
<Value>CaseId</Value>
</Value>
<Value name="2">
<Value>CreatedCaseVersion</Value>
</Value>
<Value name="3">
<Value>ReviewedCaseVersion</Value>
</Value>
<Value name="4">
<Value>ReviewReason</Value>
</Value>
<Value name="5">
<Value>ReviewIdempotencyKey</Value>
</Value>
</Data>
<DefaultData>ReviewTaskDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
