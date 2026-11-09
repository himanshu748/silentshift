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
}
