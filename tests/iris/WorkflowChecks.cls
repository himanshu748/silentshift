Include %occStatus

/// Inspect actual native Workflow rows/messages; never simulates a task.
Class SilentShift.Test.WorkflowChecks Extends %RegisteredObject
{
ClassMethod Inspect(id As %String) As %String
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), workflow = body.%Get("workflow")
    Set result = {"case_id": (id), "routing": (body.%Get("routing")), "version": (body.%Get("version")), "delivery_count": (body.%Get("delivery_count")), "policy": (body.%Get("policy")), "review": (body.%Get("review")), "workflow": (workflow), "trace_id": (body.%Get("trace_id")), "native_headers": [], "workflow_events": []}
    Set agent = body.%Get("agent")
    If $ISOBJECT(agent) {
        Set summary = {"caller_status": (agent.%Get("status")), "caller_failure_code": (agent.%Get("failure_code")), "model_invoked": null}
        If agent.%GetTypeOf("model_invoked") = "boolean" Do summary.%Set("model_invoked", agent.%Get("model_invoked"), "boolean")
        Do result.%Set("agent_summary", summary)
    }
    If '$ISOBJECT(workflow) Return result.%ToJSON()
    Set taskId = workflow.%Get("task_id")
    If taskId = "" Return result.%ToJSON()
    Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(taskId)
    If '$ISOBJECT(task) Return result.%ToJSON()
    Set native = {"task_id": (task.%Id()), "case_id": (task.CaseId), "created_case_version": (task.CreatedCaseVersion), "reviewed_case_version": (task.ReviewedCaseVersion), "role": (task.%RoleName), "assigned_to": (task.%TaskStatus.AssignedTo), "user": (task.%UserName), "action": (task.%Action), "status": (task.%Status), "is_complete": false, "time_created": (task.%TaskStatus.TimeCreated), "time_completed": (task.%TaskStatus.TimeCompleted), "session_id": (task.%TaskStatus.SessionId), "source": (task.%TaskStatus.Source), "request_id": (task.%TaskStatus.Request.%Id()), "review_reason": (task.ReviewReason), "review_idempotency_key": (task.ReviewIdempotencyKey)}
    Do native.%Set("is_complete", task.%TaskStatus.IsComplete, "boolean")
    &sql(SELECT COUNT(*) INTO :count FROM EnsLib_Workflow.Worklist WHERE Task = :taskId)
    If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Native worklist read failed"))
    Do native.%Set("worklist_count", count)
    &sql(SELECT COUNT(*) INTO :members FROM EnsLib_Workflow.RoleMembership WHERE RoleName = 'ReviewWorklist')
    If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Native role membership read failed"))
    Do native.%Set("role_membership_count", members)
    Do result.%Set("native_task", native)
    Set headers = result.%Get("native_headers"), events = result.%Get("workflow_events")
    Set stmt = ##class(%SQL.Statement).%New(), sc = stmt.%Prepare("SELECT TOP 100 ID,SessionId,SourceConfigName,TargetConfigName,MessageBodyClassName,MessageBodyId FROM Ens.MessageHeader WHERE SessionId = ? ORDER BY ID")
    $$$ThrowOnError(sc)
    Set rows = stmt.%Execute(task.%TaskStatus.SessionId)
    While rows.%Next() {
        Do headers.%Push({"id": (rows.%Get("ID")), "session_id": (rows.%Get("SessionId")), "source": (rows.%Get("SourceConfigName")), "target": (rows.%Get("TargetConfigName")), "body_class": (rows.%Get("MessageBodyClassName")), "body_id": (rows.%Get("MessageBodyId"))})
    }
    Set audits = body.%Get("events")
    For index = 0:1:audits.%Size()-1 {
        Set event = audits.%Get(index)
        If $EXTRACT(event.%Get("kind"), 1, 9) = "workflow_" Do events.%Push(event)
    }
    Return result.%ToJSON()
}

/// Administrative test of the task callback's independent authorization gate.
/// No policy decision/receipt exists yet, so native completion must be denied.
ClassMethod BypassDenied(id As %String) As %Boolean
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), workflow = body.%Get("workflow")
    Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(workflow.%Get("task_id"))
    Set before = task.%TaskStatus.IsComplete
    Set sc = task.OnAction("APPROVE")
    Return $$$ISERR(sc) && 'before && 'task.%TaskStatus.IsComplete
}

/// Deliberate native deferred-response production mismatch on a NEW synthetic
/// safe boundary case only. No production code hook or framework patch.
ClassMethod ArmCompletionFault(id As %String) As %Status
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    If 'body.%Get("synthetic") || ($EXTRACT(body.%Get("scenario_id"), 1, 13) '= "trace-budget-") Return $$$ERROR($$$GeneralError, "Fault injection requires a new synthetic boundary case")
    If $ISOBJECT(body.%Get("review")) Return $$$ERROR($$$GeneralError, "Fault injection cannot modify a decided case")
    If $DATA(^SilentShift.TestWorkflowFault(id, "original")) Return $$$ERROR($$$GeneralError, "Fault injection is already recorded for this case")
    Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(body.%Get("workflow").%Get("task_id"))
    If '$ISOBJECT(task) Return $$$ERROR($$$GeneralError, "Native fault target is missing")
    If task.%TaskStatus.IsComplete Return $$$ERROR($$$GeneralError, "Native fault target is already complete")
    Set original = task.%TaskStatus.ResponseToken
    Set ^SilentShift.TestWorkflowFault(id, "original") = original
    Set ^SilentShift.TestWorkflowFault(id, "task_id") = task.%Id()
    Set task.%TaskStatus.ResponseToken = $PIECE(original, "|", 1)_"|SilentShift_SYNTHETIC_MISSING_PRODUCTION"
    Return task.%Save()
}

ClassMethod RestoreCompletionToken(id As %String) As %Status
{
    If '$DATA(^SilentShift.TestWorkflowFault(id, "original")) Return $$$ERROR($$$GeneralError, "Native fault backup is unavailable")
    Set task = ##class(SilentShift.Workflow.ReviewTask).%OpenId(^SilentShift.TestWorkflowFault(id, "task_id"))
    If '$ISOBJECT(task) Return $$$ERROR($$$GeneralError, "Native fault task is unavailable")
    Set task.%TaskStatus.ResponseToken = ^SilentShift.TestWorkflowFault(id, "original")
    Set sc = task.%Save()
    If $$$ISOK(sc) Set ^SilentShift.TestWorkflowFault(id, "restored_at") = ##class(SilentShift.TraceEvent).UTC()
    Return sc
}
}
