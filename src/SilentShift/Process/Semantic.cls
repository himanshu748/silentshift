Include %occStatus

/// Native orchestration: each operation is a real queued host with its own pool.
Class SilentShift.Process.Semantic Extends Ens.BusinessProcess
{
Method OnRequest(request As SilentShift.Message, Output response As SilentShift.Reply) As %Status
{
    Set response = ##class(SilentShift.Reply).%New(), id = request.CaseId, stage = "start"
    Try {
        If request.Action '= "review_route" {
            Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            Do body.%Set("trace_id", ..%SessionId_"")
            Set sc = ##class(SilentShift.Store).SaveCase(id, body.%ToJSON())
            $$$ThrowOnError(sc)
            Set schemaJSON = ##class(SilentShift.Bridge).Assess(body.%Get("raw_payload"), "[]", body.%Get("clock"))
            Set schemaAssessment = ##class(%DynamicObject).%FromJSON(schemaJSON)
            Set detail = {"schema_version": (schemaAssessment.%Get("schema_version"))}
            Set sc = ##class(SilentShift.Store).AddEvent(id, $SELECT(schemaAssessment.%Get("classification") = "INVALID_MESSAGE": "schema_rejected", 1: "schema_validated"), detail.%ToJSON())
            $$$ThrowOnError(sc)
            Set sourceMessage = body.%Get("message")
            Set detail = {"contract_id": (sourceMessage.%Get("contract_id"))}
            Set sc = ##class(SilentShift.Store).AddEvent(id, "semantic_check_started", detail.%ToJSON())
            $$$ThrowOnError(sc)
            Set stage = "reference-retrieval"
            Set sc = ..SendRequestSync("References", request, .referenceReply, 10)
            $$$ThrowOnError(sc)
            Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            Set message = body.%Get("message"), references = body.%Get("references")
            Set stage = "semantic-assessment"
            Set assessmentJSON = ##class(SilentShift.Bridge).Assess(body.%Get("raw_payload"), references.%ToJSON(), body.%Get("clock"))
            Set assessment = ##class(%DynamicObject).%FromJSON(assessmentJSON)
            Do body.%Set("assessment", assessment)
            Set sc = ##class(SilentShift.Store).SaveCase(id, body.%ToJSON())
            $$$ThrowOnError(sc)
            Set detail = {"classification": (assessment.%Get("classification")), "critical": (assessment.%Get("critical")), "schema_version": (assessment.%Get("schema_version"))}
            Do detail.%Set("critical", assessment.%Get("critical"), "boolean")
            Set sc = ##class(SilentShift.Store).AddEvent(id, "semantic_check_completed", detail.%ToJSON())
            $$$ThrowOnError(sc)
            Set detail = {"implementation": "native-ai-hub", "timeout_seconds": 60, "provider_cancellation_verified": false}
            Set sc = ##class(SilentShift.Store).AddEvent(id, "agent_invoked", detail.%ToJSON())
            $$$ThrowOnError(sc)
            Set stage = "agent-investigation", raw = "", metadata = {"mode": "native-ai-hub", "status": "failed", "failure_code": "AI_UNAVAILABLE_OR_TIMEOUT"}
            Set sc = ..SendRequestSync("Investigator", request, .agentReply, 60)
            If $$$ISOK(sc), $ISOBJECT(agentReply) {
                Set raw = agentReply.RecommendationJSON
                If agentReply.MetadataJSON '= "" Set metadata = ##class(%DynamicObject).%FromJSON(agentReply.MetadataJSON)
            }
            // Investigator only returns data. A late operation cannot route or
            // update final state after this process's bounded wait expires.
            Set recommendation = "", policyInput = ""
            If raw '= "" {
                Try {
                    Set recommendation = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Canonical(raw))
                    Set policyInput = raw
                } Catch invalidRecommendation {
                    Set recommendation = "", policyInput = ""
                    Do metadata.%Set("output_status", "malformed")
                }
            }
            Do metadata.%Set("raw_response", raw)
            Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            Do body.%Set("agent", metadata)
            If $ISOBJECT(recommendation) Do body.%Set("recommendation", recommendation)
            // E is an explicit validator fault-injection AFTER a native reply.
            // It is never presented as the model's actual recommendation.
            If body.%Get("scenario_id") = "unsafe-agent-output", metadata.%Get("status") = "returned", $ISOBJECT(body.%Get("fault")) {
                Set injected = body.%Get("fault")
                Set policyInput = injected.%ToJSON()
                Set faultRecord = {"kind": "validator_recommendation_override", "synthetic": true, "proposal": (injected)}
                Do body.%Set("fault_injection", faultRecord)
                Set sc = ##class(SilentShift.Store).AddEvent(id, "validator_fault_injected", faultRecord.%ToJSON())
                $$$ThrowOnError(sc)
            }
            If policyInput '= "" Do body.%Set("policy_recommendation", ##class(%DynamicObject).%FromJSON(policyInput))
            Set stage = "policy-evaluation"
            Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON, policyInput))
            Do body.%Set("policy", policy)
            Set sc = ##class(SilentShift.Store).SaveCase(id, body.%ToJSON())
            $$$ThrowOnError(sc)
            Set detail = {"status": (metadata.%Get("status")), "mode": "native-ai-hub", "output_present": (raw '= "")}
            Do detail.%Set("output_present", raw '= "", "boolean")
            Set sc = ##class(SilentShift.Store).AddEvent(id, $SELECT(metadata.%Get("status") = "returned": "agent_returned", 1: "agent_failed"), detail.%ToJSON())
            $$$ThrowOnError(sc)
            Set sc = ##class(SilentShift.Store).AddEvent(id, "policy_evaluated", policy.%ToJSON())
            $$$ThrowOnError(sc)
        }
        Set stage = "routing"
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), policy = body.%Get("policy")
        Set target = "Quarantine"
        If $ISOBJECT(policy), policy.%Get("downstream_permitted") Set target = "Destination"
        Set sc = ..SendRequestSync(target, request, .routeReply, 10)
        $$$ThrowOnError(sc)
        Set response.BodyJSON = ##class(SilentShift.Store).CaseJSON(id)
        Return $$$OK
    } Catch error {
        // Preserve evidence, contain the case, and expose only a stable stage.
        Try {
            Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            If body.%Get("routing") '= "DELIVERED" {
                Set assessment = body.%Get("assessment"), assessmentJSON = ""
                If $ISOBJECT(assessment) Set assessmentJSON = assessment.%ToJSON()
                Set heldPolicy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON, ""))
                Do body.%Set("policy", heldPolicy)
                Do body.%Set("processing_error", {"code": "PRODUCTION_STEP_FAILED", "stage": (stage)})
                Set ignored = ##class(SilentShift.Store).SaveCase(id, body.%ToJSON())
                Set detail = {"code": "PRODUCTION_STEP_FAILED", "stage": (stage), "downstream_effect": false}
                Set ignored = ##class(SilentShift.Store).AddEvent(id, "processing_failed", detail.%ToJSON())
                Set ignored = ..SendRequestSync("Quarantine", request, .heldReply, 10)
            }
            Set response.BodyJSON = ##class(SilentShift.Store).CaseJSON(id)
        } Catch containmentError {
            Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: production failed; delivery was not authorized")
        }
        Return $$$OK
    }
}
}
