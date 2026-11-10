Include (%occStatus, Ensemble)

/// Durable async business process: waits for the native deferred task response
/// without keeping an HTTP call or operation job waiting for a human.
Class SilentShift.Workflow.Coordinator Extends Ens.BusinessProcess
{
Method OnRequest(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New()
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId))
    Set workflow = body.%Get("workflow")
    If (body.%Get("routing") '= "REVIEW") && (body.%Get("routing") '= "QUARANTINED") Return $$$OK
    If $ISOBJECT(workflow), workflow.%Get("task_id") '= "" Return $$$OK
    Set task = ##class(SilentShift.Workflow.ReviewRequest).%New()
    Set task.CaseId = request.CaseId, task.CaseVersion = body.%Get("version")
    Set task.%TaskHandler = "SilentShift.Workflow.ReviewTask"
    Set task.%Subject = "SilentShift semantic review: "_request.CaseId
    Set task.%Message = "Review the independently retrieved case evidence in SilentShift. Native completion requires its authorized policy-checked review receipt."
    Set task.%Actions = "APPROVE,REJECT"
    Set assessment = body.%Get("assessment")
    If $ISOBJECT(assessment), assessment.%Get("classification") = "VERIFIED_CONTRADICTION" Set task.%Actions = "REJECT"
    Set task.%UserName = "", task.%Title = ""
    Set sc = ..SendRequestAsync("ReviewWorklist", task, 1, "semantic-human-review", "Native semantic review task")
    If $$$ISERR(sc) $$$LOGERROR("SS_WORKFLOW_DISPATCH_FAILED stage=workflow-dispatch case_id="_request.CaseId)
    Return sc
}

Method OnResponse(request As SilentShift.Message, ByRef response As SilentShift.Reply, callrequest As %Persistent, callresponse As %Persistent, pCompletionKey As %String) As %Status
{
    If '$ISOBJECT(callresponse) {
        $$$LOGERROR("SS_WORKFLOW_ASSOCIATION_INVALID stage=workflow-completion case_id="_request.CaseId)
        Return $$$ERROR($$$GeneralError, "Native workflow returned no response")
    }
    If 'callresponse.%IsA("SilentShift.Workflow.ReviewTask") {
        $$$LOGERROR("SS_WORKFLOW_ASSOCIATION_INVALID stage=workflow-completion case_id="_request.CaseId)
        Return $$$ERROR($$$GeneralError, "Native workflow response type is invalid")
    }
    If callresponse.%Action = "DUPLICATE_SUPPRESSED" Return $$$OK
    If (callresponse.CaseId '= request.CaseId) || 'callresponse.%TaskStatus.IsComplete {
        $$$LOGERROR("SS_WORKFLOW_ASSOCIATION_INVALID stage=workflow-completion case_id="_request.CaseId)
        Return $$$ERROR($$$GeneralError, "Native workflow completion association is invalid")
    }
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(request.CaseId)), workflow = body.%Get("workflow")
    If '$ISOBJECT(workflow) {
        $$$LOGERROR("SS_WORKFLOW_ASSOCIATION_INVALID stage=workflow-completion case_id="_request.CaseId)
        Return $$$ERROR($$$GeneralError, "Native workflow case association is missing")
    }
    If workflow.%Get("task_id") '= callresponse.%Id() {
        $$$LOGERROR("SS_WORKFLOW_ASSOCIATION_INVALID stage=workflow-completion case_id="_request.CaseId)
        Return $$$ERROR($$$GeneralError, "Native workflow task association differs")
    }
    Set headerId = ""
    If $ISOBJECT(..%CurrentResponseHeader) Set headerId = ..%CurrentResponseHeader.%Id()
    Set data = {"status": "completed", "completion_received": true, "completion_header_id": (headerId), "completion_action": (callresponse.%Action), "completed_by": (callresponse.%UserName), "completion_received_at": (##class(SilentShift.TraceEvent).UTC()), "completion_response_id": (callresponse.%Id())}
    Set sc = ##class(SilentShift.Store).SetWorkflow(request.CaseId, data.%ToJSON(), "workflow_completion_received")
    If $$$ISERR(sc) $$$LOGERROR("SS_WORKFLOW_SAVE_FAILED stage=workflow-completion case_id="_request.CaseId)
    If $$$ISOK(sc) Set response.BodyJSON = ##class(SilentShift.Store).CaseJSON(request.CaseId)
    Return sc
}
}
