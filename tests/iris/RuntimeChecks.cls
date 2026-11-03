Include (%occStatus, %outUnitTest)

/// Native regression checks. These create and retain labeled synthetic records.
/// They never modify the frozen fixture catalog, call an LLM, or delete data.
/// The standalone driver and %UnitTest methods share the same assertions.
Class SilentShift.Test.RuntimeChecks Extends %UnitTest.TestCase
{

Method TestApprovedReferenceLimit()
{
    Set sc = ..ExerciseReferenceLimit("approved", .result)
    Do $$$AssertStatusOK(sc)
    If $$$ISOK(sc) Do ..AssertChecks(result)
}

Method TestPeerReferenceLimit()
{
    Set sc = ..ExerciseReferenceLimit("peer", .result)
    Do $$$AssertStatusOK(sc)
    If $$$ISOK(sc) Do ..AssertChecks(result)
}

Method AssertChecks(result As %DynamicObject) [ Private ]
{
    Set iterator = result.%Get("checks").%GetIterator()
    While iterator.%GetNext(.name, .passed) {
        Do $$$AssertTrue(passed, name)
    }
}

/// Entry point without %UnitTest.Manager's global setup/cleanup side effects.
/// Only this test class needs compilation. Both test cases remain persisted.
ClassMethod RunBoundaries(Output reportJSON As %String) As %Status
{
    Set report = {"suite": "native-reference-boundaries/1", "runner": "native-driver-shared-with-unit-test", "synthetic": true, "model_calls_requested": false, "data_deleted": false, "iris_version": ($ZVERSION), "cases": []}
    Set reportJSON = report.%ToJSON()
    Try {
        Set sc = ..RequireCompiledGuard()
        $$$ThrowOnError(sc)
        Set sc = ##class(Ens.Director).GetProductionStatus(.production, .state)
        $$$ThrowOnError(sc)
        If (production '= "SilentShift.Production") || (state '= 1) Return $$$ERROR($$$GeneralError, "Boundary tests require the running SilentShift production")
        Do report.%Set("production", production)
        Do report.%Set("created_at", ##class(SilentShift.Bridge).Now())
        Set cases = report.%Get("cases"), passed = 1
        For authority = "approved", "peer" {
            Set sc = ..ExerciseReferenceLimit(authority, .result)
            Do cases.%Push(result)
            If $$$ISERR(sc) Set passed = 0
            If 'result.%Get("passed") Set passed = 0
        }
        Do report.%Set("passed", passed, "boolean")
        Set reportJSON = report.%ToJSON()
        If 'passed Return $$$ERROR($$$GeneralError, "Native reference boundary assertions failed")
        Return $$$OK
    } Catch error {
        Do report.%Set("passed", 0, "boolean")
        Do report.%Set("error", "NATIVE_BOUNDARY_EXECUTION_FAILED")
        Set reportJSON = report.%ToJSON()
        Return $$$ERROR($$$GeneralError, "Native boundary test preflight or execution failed")
    }
}

/// Fail before constructing a case if the compiled native pre-provider guard
/// is absent. Checking the compiled routine avoids trusting uncompiled source.
ClassMethod RequireCompiledGuard() As %Status [ Private ]
{
    If $NAMESPACE '= "SILENTSHIFT" Return $$$ERROR($$$GeneralError, "Boundary tests require SILENTSHIFT")
    Set guardLine = 0, providerLine = 0, limitsLine = 0, falseLine = 0
    For offset = 0:1:200 {
        Set line = $TEXT(Run+offset^SilentShift.AI.Investigator.1)
        If line [ "EVIDENCE_REFERENCE_LIMIT" Set guardLine = offset
        If (line [ "approvedCount > 10") && (line [ "peerCount > 10") Set limitsLine = offset
        If (line [ "model_invoked") && (line [ "false") Set falseLine = offset
        If line [ "%AI.Provider" {
            Set providerLine = offset
            Quit
        }
    }
    If (guardLine < 1) || (limitsLine < 1) || (falseLine < 1) || (providerLine <= guardLine) Return $$$ERROR($$$GeneralError, "Compiled pre-provider evidence limit guard is required; no case was sent")
    Return $$$OK
}

ClassMethod ExerciseReferenceLimit(authority As %String, Output result As %DynamicObject) As %Status [ Private ]
{
    Set result = {"authority": (authority), "synthetic": true, "checks": {}, "passed": false}
    Try {
        Set sc = ..RequireCompiledGuard()
        $$$ThrowOnError(sc)
        If (authority '= "approved") && (authority '= "peer") Return $$$ERROR($$$GeneralError, "Unknown test reference authority")
        Set runId = $TRANSLATE($SYSTEM.Util.CreateGUID(), "{}", "")
        Set scope = "native-boundary-"_authority_"-"_runId
        Set contractId = "SYNTHETIC:BOUNDARY:"_authority_":"_runId
        Set occurred = ##class(SilentShift.Bridge).Now()
        Do result.%Set("scope", scope)
        Do result.%Set("contract_id", contractId)
        For index = 1:1:11 {
            Set refId = "synthetic:boundary:"_runId_":"_authority_":"_index
            Set reference = {"id": (refId), "contract_id": (contractId), "authority": (authority), "effective_from": "2026-01-01T00:00:00Z", "effective_to": null, "business_unit": "SYNTHETIC-TEST", "product_id": "SYNTHETIC-BOUNDARY", "quantity": "20", "unit": "EA", "timestamp_semantics": "event_time", "synthetic": true, "test_suite": "native-reference-boundaries/1"}
            Set record = ##class(SilentShift.Data.Reference).%New()
            Set record.ReferenceKey = ##class(SilentShift.Bridge).PairHash(scope, refId)
            Set record.ReferenceId = refId, record.ScenarioScope = scope
            Set record.ContractId = contractId, record.Body = reference.%ToJSON()
            Set sc = record.%Save()
            $$$ThrowOnError(sc)
        }

        Set message = {"event_id": ("synthetic-boundary-"_runId), "correlation_id": ("synthetic-boundary-"_runId), "source": "silentshift-native-boundary-test", "kind": "order", "occurred_at": (occurred), "contract_id": (contractId), "business_unit": "SYNTHETIC-TEST", "product_id": "SYNTHETIC-BOUNDARY", "quantity": "20", "unit": "EA", "notes": "Labeled synthetic no-LLM native reference-limit regression; retain as test evidence."}
        Set envelope = {"message": (message), "raw_payload": (message.%ToJSON()), "scenario_id": (scope), "dataset_version": "silentshift-native-boundary/1", "clock": (occurred)}
        Set input = ##class(%Stream.GlobalCharacter).%New()
        Set sc = input.Write(envelope.%ToJSON())
        $$$ThrowOnError(sc)
        Set sc = ##class(Ens.Director).CreateBusinessService("Partner", .service)
        $$$ThrowOnError(sc)
        Set sc = service.ProcessInput(input, .reply)
        $$$ThrowOnError(sc)
        If '$ISOBJECT(reply) Return $$$ERROR($$$GeneralError, "Partner returned no native reply")
        Set response = ##class(%DynamicObject).%FromJSON(reply.BodyJSON)
        Set id = response.%Get("id")
        Do result.%Set("case_id", id)
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        Set references = body.%Get("references"), metadata = body.%Get("agent"), policy = body.%Get("policy")
        Set trace = body.%Get("trace_id"), assessment = body.%Get("assessment")
        Set count = references.%Size(), allAuthority = 1
        For index = 0:1:count-1 {
            If references.%Get(index).%Get("authority") '= authority Set allAuthority = 0
        }
        Set traceNumber = +trace
        &sql(SELECT COUNT(*) INTO :partnerTrace FROM Ens.MessageHeader WHERE SessionId = :traceNumber AND SourceConfigName = 'Partner' AND TargetConfigName = 'Semantic')
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Native Partner trace query failed"))
        &sql(SELECT COUNT(*) INTO :investigatorTrace FROM Ens.MessageHeader WHERE SessionId = :traceNumber AND SourceConfigName = 'Semantic' AND TargetConfigName = 'Investigator')
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Native Investigator trace query failed"))
        &sql(SELECT COUNT(*) INTO :deliveryCount FROM SilentShift_Data.Delivery WHERE CaseId = :id)
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Delivery count query failed"))
        &sql(SELECT COUNT(*) INTO :toolReads FROM SilentShift_Data.AuditEvent WHERE CaseId = :id AND Kind = 'agent_tool_read')
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Tool audit query failed"))
        &sql(SELECT COUNT(*) INTO :chatReturns FROM SilentShift_Data.AuditEvent WHERE CaseId = :id AND Kind = 'native_chat_returned')
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Chat audit query failed"))
        &sql(SELECT COUNT(*) INTO :semanticComplete FROM SilentShift_Data.AuditEvent WHERE CaseId = :id AND Kind = 'semantic_check_completed')
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Semantic audit query failed"))
        &sql(SELECT COUNT(*) INTO :heldEvents FROM SilentShift_Data.AuditEvent WHERE CaseId = :id AND Kind = 'message_held')
        If SQLCODE < 0 Throw ##class(%Exception.StatusException).CreateFromStatus($$$ERROR($$$GeneralError, "Routing audit query failed"))

        Set checks = result.%Get("checks")
        Do checks.%Set("snapshot_contains_all_11_references", (count = 11) && allAuthority, "boolean")
        Do checks.%Set("isolated_synthetic_scope", (body.%Get("scenario_id") = scope) && (body.%GetTypeOf("synthetic") = "boolean") && body.%Get("synthetic"), "boolean")
        Do checks.%Set("native_partner_to_semantic_trace", (traceNumber > 0) && (partnerTrace > 0), "boolean")
        Do checks.%Set("native_semantic_to_investigator_trace", investigatorTrace > 0, "boolean")
        Do checks.%Set("semantic_assessment_completed", (semanticComplete = 1) && (assessment.%Get("classification") '= "INVALID_MESSAGE") && 'assessment.%Get("critical"), "boolean")
        Do checks.%Set("routed_to_review", (body.%Get("routing") = "REVIEW") && (heldEvents = 1), "boolean")
        Do checks.%Set("policy_denies_delivery", (policy.%Get("decision") = "REQUEST_REVIEW") && 'policy.%Get("downstream_permitted"), "boolean")
        Do checks.%Set("no_delivery_rows", (deliveryCount = 0) && (body.%Get("delivery_count") = 0), "boolean")
        Do checks.%Set("specific_evidence_limit_failure", (metadata.%Get("failure_code") = "EVIDENCE_REFERENCE_LIMIT") && (metadata.%Get("failure_stage") = "evidence-budget-check"), "boolean")
        Do checks.%Set("model_not_invoked_boolean", (metadata.%GetTypeOf("model_invoked") = "boolean") && 'metadata.%Get("model_invoked"), "boolean")
        Do checks.%Set("no_tool_or_chat_audits", (toolReads = 0) && (chatReturns = 0), "boolean")
        Do checks.%Set("no_model_proposal", '$ISOBJECT(body.%Get("recommendation")) && (metadata.%Get("raw_response", "") = ""), "boolean")
        Set evidenceBudget = metadata.%Get("evidence_budget")
        Do checks.%Set("observed_reference_budget", $ISOBJECT(evidenceBudget) && (evidenceBudget.%Get(authority) = 11) && (evidenceBudget.%Get("maximum_each") = 10), "boolean")
        Set passed = 1, iterator = checks.%GetIterator()
        While iterator.%GetNext(.name, .value) {
            If 'value Set passed = 0
        }
        Do result.%Set("passed", passed, "boolean")
        Do result.%Set("reference_count", count)
        Do result.%Set("trace_id", trace)
        Do result.%Set("partner_trace_rows", partnerTrace)
        Do result.%Set("investigator_trace_rows", investigatorTrace)
        Do result.%Set("routing", body.%Get("routing"))
        Do result.%Set("delivery_count", deliveryCount)
        Do result.%Set("agent_tool_read_count", toolReads)
        Do result.%Set("native_chat_returned_count", chatReturns)
        Do result.%Set("agent", metadata)
        Return $$$OK
    } Catch error {
        Do result.%Set("error", "NATIVE_BOUNDARY_CASE_FAILED")
        Return $$$ERROR($$$GeneralError, "Native boundary case could not complete")
    }
}

}
