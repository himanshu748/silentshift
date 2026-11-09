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
            // Retrieve supporting procedures outside native agent callbacks.
            // Oversized evidence is rejected before any model (including an
            // embedding model) is invoked. Procedures grant no release rights.
            Set approvedCount = 0, peerCount = 0
            For index = 0:1:references.%Size()-1 {
                If references.%Get(index).%Get("authority") = "approved" {
                    Set approvedCount = approvedCount + 1
                } Else {
                    Set peerCount = peerCount + 1
                }
            }
            If (approvedCount <= 10) && (peerCount <= 10) {
                Set stage = "supporting-procedures"
                Set optionalStatus = ..SendRequestSync("Runbooks", request, .runbookReply, 10)
                Set context = {"status": "unavailable", "implementation": "IRIS VECTOR_COSINE", "matches": [], "decision_authority": false, "failure_code": "RUNBOOK_RETRIEVAL_UNAVAILABLE"}
                If $$$ISOK(optionalStatus), $ISOBJECT(runbookReply), runbookReply.BodyJSON '= "" {
                    Set context = ##class(%DynamicObject).%FromJSON(runbookReply.BodyJSON)
                }
                Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
                Do body.%Set("runbook_context", context)
                Set sc = ##class(SilentShift.Store).SaveCase(id, body.%ToJSON())
                $$$ThrowOnError(sc)
                Set detail = {"status": (context.%Get("status")), "implementation": "IRIS VECTOR_COSINE", "match_count": (context.%Get("matches").%Size()), "decision_authority": false}
                Set sc = ##class(SilentShift.Store).AddEvent(id, "runbook_retrieved", detail.%ToJSON())
                $$$ThrowOnError(sc)
                Set stage = "similar-precedents"
                Set optionalStatus = ..SendRequestSync("Precedents", request, .precedentReply, 10)
                Set context = {"status": "unavailable", "implementation": "IRIS VECTOR_COSINE", "model": "all-minilm:22m", "dimensions": 384, "matches": [], "decision_authority": false, "failure_code": "PRECEDENT_RETRIEVAL_UNAVAILABLE"}
                If $$$ISOK(optionalStatus), $ISOBJECT(precedentReply), precedentReply.BodyJSON '= "" {
                    Set context = ##class(%DynamicObject).%FromJSON(precedentReply.BodyJSON)
                }
                Do context.%Set("case_id",id)
                Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
                Do body.%Set("precedent_context",context)
                Set sc = ##class(SilentShift.Store).SaveCase(id,body.%ToJSON())
                $$$ThrowOnError(sc)
                Set detail = {"status":(context.%Get("status")),"implementation":"IRIS VECTOR_COSINE","match_count":(context.%Get("matches").%Size()),"decision_authority":false}
                Set sc = ##class(SilentShift.Store).AddEvent(id,"precedents_retrieved",detail.%ToJSON())
                $$$ThrowOnError(sc)
                // Optional context cannot veto an otherwise valid case, and
                // cannot supply missing contract evidence or authorize ALLOW.
            }
            Set agentWait = ##class(SilentShift.AI.Investigator).WaitSeconds()
            Set detail = {"implementation": "native-ai-hub", "timeout_seconds": (agentWait), "provider_cancellation_verified": false}
            Set sc = ##class(SilentShift.Store).AddEvent(id, "agent_invoked", detail.%ToJSON())
            $$$ThrowOnError(sc)
            Set stage = "agent-investigation", raw = "", metadata = {"mode": "native-ai-hub", "status": "failed", "failure_code": "AI_UNAVAILABLE_OR_TIMEOUT"}
            Set sc = ..SendRequestSync("Investigator", request, .agentReply, agentWait)
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
            If (raw '= "") || 'metadata.%IsDefined("raw_response") Do metadata.%Set("raw_response", raw)
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
            Set evidenceContext = {"message": (body.%Get("message")), "references": (body.%Get("references"))}
            Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON, policyInput, evidenceContext.%ToJSON()))
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
        // Completed source records become future evidence in a separate pool.
        // Indexing cannot change policy, case state or the committed receipt.
        Set routed = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        If (routed.%Get("routing") = "DELIVERED") || (routed.%Get("routing") = "REJECTED") {
            Set indexRequest = ##class(SilentShift.Message).%New()
            Set indexRequest.CaseId = id, indexRequest.Action = "index_precedent"
            Set indexStatus = ..SendRequestAsync("Precedents",indexRequest,0,"","Index resolved precedent")
            If $$$ISERR(indexStatus) Set ignored = ##class(SilentShift.Store).AddEvent(id,"precedent_index_enqueue_failed",{"code":"PRECEDENT_INDEX_UNAVAILABLE","decision_authority":false}.%ToJSON())
        }
        // Newly processed review and quarantine holds create native tasks.
        // Existing benchmark/history cases are never scanned or backfilled.
        If request.Action '= "review_route" {
            Set routed = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            If (routed.%Get("routing") = "REVIEW") || (routed.%Get("routing") = "QUARANTINED") {
                Set workflow = {"engine": "native-iris-workflow", "status": "queued", "role": "ReviewWorklist", "requested_at": (##class(SilentShift.TraceEvent).UTC()), "completion_received": false}
                Set sc = ##class(SilentShift.Store).SetWorkflow(id, workflow.%ToJSON(), "workflow_task_requested")
                $$$ThrowOnError(sc)
                Set sc = ..SendRequestAsync("ReviewCoordinator", request, 0, "", "Create native semantic review")
                $$$ThrowOnError(sc)
                // Bounded wait for task linkage only; human completion is
                // durable asynchronous work in the separate coordinator BP.
                For attempt = 1:1:20 {
                    Set routed = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
                    Set workflow = routed.%Get("workflow")
                    If workflow.%Get("task_id") '= "" Quit
                    Hang .1
                }
            }
        }
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
