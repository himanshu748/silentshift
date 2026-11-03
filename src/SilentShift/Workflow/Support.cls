Include %occStatus

/// Workflow identity and policy boundary. Native role membership is separate
/// from IRIS security roles; only the configured reviewer is enrolled.
Class SilentShift.Workflow.Support Extends %RegisteredObject
{
ClassMethod Configure() As %Status
{
    Set reviewer = $SYSTEM.Util.GetEnviron("SILENTSHIFT_IRIS_USERNAME")
    If ($NAMESPACE '= "SILENTSHIFT") || (reviewer = "") Return $$$ERROR($$$GeneralError, "Workflow configuration is incomplete")
    If '##class(EnsLib.Workflow.RoleDefinition).%ExistsId("ReviewWorklist") {
        Set sc = ##class(EnsLib.Workflow.RoleDefinition).CreateRole("ReviewWorklist")
        $$$ThrowOnError(sc)
    }
    If '##class(EnsLib.Workflow.UserDefinition).%ExistsId(reviewer) {
        Set sc = ##class(EnsLib.Workflow.UserDefinition).CreateUser(reviewer, "SilentShift authorized reviewer")
        $$$ThrowOnError(sc)
    }
    Set other = ""
    &sql(SELECT TOP 1 UserName INTO :other FROM EnsLib_Workflow.RoleMembership WHERE RoleName = 'ReviewWorklist' AND UserName <> :reviewer)
    If (SQLCODE < 0) || (other '= "") Return $$$ERROR($$$GeneralError, "Workflow role is not restricted to the configured reviewer")
    If '##class(EnsLib.Workflow.RoleMembership).%ExistsId("ReviewWorklist||"_reviewer) Return ##class(EnsLib.Workflow.RoleDefinition).AddUserToRole("ReviewWorklist", reviewer)
    Return $$$OK
}

ClassMethod Identity(reviewer As %String) As %Status
{
    If '$SYSTEM.Security.Check("SSReview", "U") Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: reviewer permission is required")
    If (reviewer = "") || (reviewer '= $USERNAME) || (reviewer '= $SYSTEM.Util.GetEnviron("SILENTSHIFT_IRIS_USERNAME")) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native workflow reviewer identity is invalid")
    If '##class(EnsLib.Workflow.RoleMembership).%ExistsId("ReviewWorklist||"_reviewer) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native workflow role membership is required")
    Set user = ##class(EnsLib.Workflow.UserDefinition).%OpenId(reviewer)
    If '$ISOBJECT(user) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native workflow reviewer is unavailable")
    If 'user.IsActive Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native workflow reviewer is inactive")
    Return $$$OK
}

ClassMethod Claim(id As %String, workflow As %DynamicObject, reviewer As %String, expectedVersion As %Integer, Output claim As %DynamicObject) As %Status
{
    Set sc = ..Identity(reviewer)
    If $$$ISERR(sc) Return sc
    If workflow.%Get("task_id") = "" Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native review task is still being created")
    Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(workflow.%Get("task_id"))
    If '$ISOBJECT(task) Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native review task is unavailable")
    If (task.CaseId '= id) || (task.%RoleName '= "ReviewWorklist") Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native review task scope is invalid")
    If task.%TaskStatus.IsComplete Return $$$ERROR($$$GeneralError, "APP_CONFLICT: native review task is already completed")
    If task.%TaskStatus.AssignedTo = "" {
        Set item = ##class(EnsLib.Workflow.Worklist).%OpenId(workflow.%Get("worklist_id"))
        If '$ISOBJECT(item) Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native review worklist is unavailable")
        If (item.UserGetObjectId() '= reviewer) || (item.TaskGetObjectId() '= task.%Id()) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native worklist scope is invalid")
        Set sc = ##class(EnsLib.Workflow.Engine).%TakeOwnershipForTask(item.%Id(), reviewer, .message)
        If $$$ISERR(sc) Return sc
        If message '= "" Return $$$ERROR($$$GeneralError, "APP_CONFLICT: native review task could not be claimed")
        Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(workflow.%Get("task_id"))
    }
    If task.%TaskStatus.AssignedTo '= reviewer Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native task is assigned to another reviewer")
    Set claim = {"task_id": (task.%Id()), "reviewer": (reviewer), "expected_case_version": (expectedVersion), "claimed_at": (##class(SilentShift.TraceEvent).UTC()), "native_assigned_to": (task.%TaskStatus.AssignedTo)}
    Return ##class(SilentShift.Store).AddEvent(id, "workflow_task_claimed", claim.%ToJSON())
}

ClassMethod AuthorizeCompletion(id As %String, taskId As %String, reviewer As %String, action As %String) As %Status
{
    Set sc = ..Identity(reviewer)
    If $$$ISERR(sc) Return sc
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Set workflow = body.%Get("workflow"), review = body.%Get("review")
    If '$ISOBJECT(workflow) || '$ISOBJECT(review) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: complete the authorized SilentShift review first")
    If (workflow.%Get("task_id") '= taskId) || (review.%Get("reviewer") '= reviewer) || (review.%Get("action") '= $ZCONVERT(action, "L")) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: native review completion does not match its receipt")
    Set key = ##class(SilentShift.Bridge).PairHash(id, review.%Get("idempotency_key"))
    Set receipt = ##class(SilentShift.Data.ReviewAction).%OpenId(key)
    If '$ISOBJECT(receipt) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: authorized review receipt is missing")
    Set recorded = ##class(%DynamicObject).%FromJSON(receipt.Body)
    For field = "action", "reason", "reviewer", "idempotency_key", "expected_version" {
        If recorded.%Get(field) '= review.%Get(field) Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: authorized review receipt differs")
    }
    If review.%Get("action") = "approve" {
        Set assessment = body.%Get("assessment"), proposal = body.%Get("policy_recommendation")
        Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessment.%ToJSON(), proposal.%ToJSON()))
        If 'policy.%Get("downstream_permitted") Return $$$ERROR($$$GeneralError, "APP_FORBIDDEN: deterministic policy forbids native workflow release")
    }
    Return $$$OK
}

/// Called only after the review receipt commits. Retrying the SAME review key
/// repairs a failed completion without repeating the decision or delivery.
ClassMethod SyncCompletion(id As %String, reviewer As %String) As %Status
{
    Try {
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), workflow = body.%Get("workflow")
        If '$ISOBJECT(workflow) Return $$$OK
        Set review = body.%Get("review"), taskId = workflow.%Get("task_id")
        Set sc = ..AuthorizeCompletion(id, taskId, reviewer, review.%Get("action"))
        $$$ThrowOnError(sc)
        Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(taskId)
        If '$ISOBJECT(task) Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native workflow completion is pending")
        If task.%TaskStatus.IsComplete, workflow.%IsDefined("native_time_completed") Return $$$OK
        If 'task.%TaskStatus.IsComplete {
            Set itemId = workflow.%Get("worklist_id")
            If ##class(EnsLib.Workflow.Worklist).%ExistsId(itemId) {
                Set sc = ##class(EnsLib.Workflow.Engine).%ProcessAction($ZCONVERT(review.%Get("action"), "U"), itemId, reviewer, .message)
                $$$ThrowOnError(sc)
                If message '= "" Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native workflow completion is pending")
            } Else {
                // Native CompleteTask removes worklist items before enqueueing
                // its deferred response. Recover a failed enqueue via the same
                // guarded native task callback, without inventing a receipt.
                Set sc = task.OnAction($ZCONVERT(review.%Get("action"), "U"))
                $$$ThrowOnError(sc)
                Set sc = task.%Save()
                $$$ThrowOnError(sc)
            }
        }
        Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(taskId)
        If 'task.%TaskStatus.IsComplete Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native workflow completion was not confirmed")
        Set data = {"status": "completed", "completed_by": (task.%UserName), "completion_action": (task.%Action), "completion_confirmed_at": (##class(SilentShift.TraceEvent).UTC()), "native_time_completed": (task.%TaskStatus.TimeCompleted)}
        Return ##class(SilentShift.Store).SetWorkflow(id, data.%ToJSON(), "workflow_task_completed")
    } Catch error {
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: review is committed; retry the same review key to finish native workflow synchronization")
    }
}
}
