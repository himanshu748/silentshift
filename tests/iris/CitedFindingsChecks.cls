Include (%occStatus, %outUnitTest)

/// Pure Embedded Python policy checks: no model calls or persisted cases.
Class SilentShift.Test.CitedFindingsChecks Extends %UnitTest.TestCase
{
Method TestCitationContainment()
{
    Set fixture=##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
    Set item=fixture.%Get("scenarios").%Get(0),message=item.%Get("message"),refs=item.%Get("references")
    Do message.%Set("unit","EA"),message.%Set("quantity","240")
    Set ref=refs.%Get(0)
    Do ref.%Set("dispatch_terms",{"body":"The signed dispatch authorization is withdrawn until further notice."})
    Set assessmentJSON=##class(SilentShift.Bridge).Assess(message.%ToJSON(),refs.%ToJSON(),fixture.%Get("clock"))
    Set assessment=##class(%DynamicObject).%FromJSON(assessmentJSON)
    Set finding={"reference_id":(ref.%Get("id")),"path":"/dispatch_terms/body","quote":"dispatch authorization is withdrawn until further notice."}
    Set proposal={"decision":"QUARANTINE","evidence_ids":(assessment.%Get("evidence_ids")),"explanation":"Dispatch authorization is withdrawn.","uncertainty":0.1,"cited_findings":[(finding)]}
    Set context={"message":(message),"references":(refs)}
    Set result=##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON,proposal.%ToJSON(),context.%ToJSON()))
    Do $$$AssertEquals(result.%Get("decision"),"QUARANTINE","Exact current-evidence quote may contain the transaction")
    Do $$$AssertTrue('result.%Get("downstream_permitted"),"Quotation cannot grant delivery")
    Do finding.%Set("quote","This invented quote does not occur in the reference.")
    Set result=##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON,proposal.%ToJSON(),context.%ToJSON()))
    Do $$$AssertEquals(result.%Get("decision"),"REQUEST_REVIEW","Invented quote cannot justify grounded quarantine")
    Do message.%Set("quantity","241"),proposal.%Set("decision","ALLOW"),proposal.%Set("cited_findings",[])
    Set assessmentJSON=##class(SilentShift.Bridge).Assess(message.%ToJSON(),refs.%ToJSON(),fixture.%Get("clock"))
    Set result=##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON,proposal.%ToJSON(),context.%ToJSON()))
    Do $$$AssertEquals(result.%Get("decision"),"QUARANTINE","Agent never releases a rule hold")
}

Method TestProseCitationPaths()
{
    Set fixture=##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
    Set item=fixture.%Get("scenarios").%Get(0),message=item.%Get("message"),refs=item.%Get("references")
    Set run=$TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
    Do message.%Set("event_id","citation-projection-"_run),message.%Set("correlation_id",run)
    Set envelope={"message":(message),"raw_payload":(message.%ToJSON()),"scenario_id":("native-citation-projection-"_run),"dataset_version":"synthetic-citation-projection/1","clock":(fixture.%Get("clock"))}
    Set sc=##class(SilentShift.Store).CreateCase(envelope.%ToJSON(),.id,.duplicate)
    Do $$$AssertStatusOK(sc)
    Set ref=refs.%Get(0)
    Do ref.%Set("dispatch_terms",{"body":"The signed dispatch authorization is withdrawn until further notice."})
    Do ref.%Set("contract/clause~",{"body":"A separate synthetic approved contractual text leaf."})
    Set scope=envelope.%Get("scenario_id")
    For i=0:1:refs.%Size()-1 {
        Set reference=refs.%Get(i),row=##class(SilentShift.Data.Reference).%New()
        Set row.ReferenceKey=##class(SilentShift.Bridge).PairHash(scope,reference.%Get("id"))
        Set row.ReferenceId=reference.%Get("id"),row.ScenarioScope=scope
        Set row.ContractId=reference.%Get("contract_id"),row.Body=##class(SilentShift.Bridge).Canonical(reference.%ToJSON())
        Set sc=row.%Save()
        Do $$$AssertStatusOK(sc)
    }
    Set sc=##class(SilentShift.Store).SnapshotReferences(id)
    Do $$$AssertStatusOK(sc)
    Set tool=##class(SilentShift.AI.EvidenceTools).%New(),tool.CaseId=id
    Set result=##class(%DynamicObject).%FromJSON(tool.GetApprovedContracts())
    Set paths=result.%Get("prose_citation_paths"),nested=0,escaped=0
    For i=0:1:paths.%Size()-1 {
        Set path=paths.%Get(i).%Get("path")
        If path="/dispatch_terms/body" Set nested=1
        If path="/contract~1clause~0/body" Set escaped=1
    }
    Do $$$AssertTrue(nested,"Nested prose path is visible to the model")
    Do $$$AssertTrue(escaped,"JSON pointer escaping survives native projection")
    Do $$$AssertEquals(result.%Get("references").%Get(0).%Get("dispatch_terms").%Get("body"),"The signed dispatch authorization is withdrawn until further notice.","Prose is returned intact")
}

Method TestFinalFormatAfterInvocationReads()
{
    Set fixture=##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
    Set message=fixture.%Get("scenarios").%Get(0).%Get("message"),run=$TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
    Do message.%Set("event_id","format-contract-"_run)
    Set envelope={"message":(message),"raw_payload":(message.%ToJSON()),"scenario_id":"synthetic-final-format-contract","clock":(fixture.%Get("clock"))}
    Set sc=##class(SilentShift.Store).CreateCase(envelope.%ToJSON(),.id,.duplicate)
    Do $$$AssertStatusOK(sc)
    Set binding={"CaseId":(id),"InvocationSpanId":(run),"ExecutionMode":"live","Provider":"ollama/openai-compatible","PromptVersion":"silentshift-investigator/1.4.2"}
    Set input={"model":"qwen3-silentshift:4b-instruct","messages":[{"role":"user","content":"A synthetic café request."}],"tools":[],"tool_choice":"auto","parallel_tool_calls":false}
    Set raw=$ZCONVERT(input.%ToJSON(),"O","UTF8")
    Set result=##class(SilentShift.Provider.Lease).ShapeFinal(raw,binding,.shaped)
    Do $$$AssertTrue('shaped,"Format cannot suppress required evidence reads")
    Do $$$AssertEquals(result,raw,"Pre-read request bytes remain unchanged")
    For tool="GetCurrentMessage","GetApprovedContracts","GetRelatedRecords","find_similar_precedents" {
        Set sc=##class(SilentShift.Store).AddEvent(id,"agent_tool_read",{"tool":(tool),"invocation_span_id":(run)}.%ToJSON())
        Do $$$AssertStatusOK(sc)
    }
    Do binding.%Set("InvocationSpanId","another-invocation")
    Set result=##class(SilentShift.Provider.Lease).ShapeFinal(raw,binding,.shaped)
    Do $$$AssertTrue('shaped,"Another invocation's reads do not authorize final format")
    Do binding.%Set("InvocationSpanId",run)
    Set result=##class(SilentShift.Provider.Lease).ShapeFinal(raw,binding,.shaped)
    Do $$$AssertTrue(shaped,"Four invocation-scoped reads enable final format")
    Set decoded=##class(%DynamicObject).%FromJSON($ZCONVERT(result,"I","UTF8"))
    Do $$$AssertTrue('decoded.%IsDefined("tools"),"Final request cannot call more tools")
    Do $$$AssertEquals(decoded.%Get("response_format").%Get("type"),"json_schema","Constrained final output is requested")
    Do $$$AssertEquals(decoded.%Get("messages").%ToJSON(),input.%Get("messages").%ToJSON(),"Evidence and UTF-8 messages remain intact")
    Do binding.%Set("ExecutionMode","recorded-replay")
    Set result=##class(SilentShift.Provider.Lease).ShapeFinal(raw,binding,.shaped)
    Do $$$AssertTrue('shaped,"Keyless replay request is unchanged")
    Do $$$AssertEquals(result,raw)
    Do binding.%Set("ExecutionMode","live"),binding.%Set("Provider","openai")
    Set result=##class(SilentShift.Provider.Lease).ShapeFinal(raw,binding,.shaped)
    Do $$$AssertTrue('shaped,"Other providers are not silently reformatted")
}
}
