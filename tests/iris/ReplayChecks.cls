Include (%occStatus, %outUnitTest)

/// No inference/network: verify provenance, scope, tool progression and policy.
Class SilentShift.Test.ReplayChecks Extends %UnitTest.TestCase
{
Method TestRecordedResponseProgression()
{
    Set messages = [{"role":"user","content":"Synthetic playback test"}]
    For round = 1:1:5 {
        Set request = {"messages":(messages)}
        Set raw = ##class(SilentShift.Provider.Replay).Response(request.%ToJSON(),round)
        Set data = ##class(%DynamicObject).%FromJSON(raw), choice = data.choices.%Get(0)
        Do $$$AssertTrue('data.%IsDefined("usage"))
        If round < 5 {
            Do $$$AssertEquals(choice.%Get("finish_reason"),"tool_calls")
            Do $$$AssertEquals(choice.%Get("message").%Get("tool_calls").%Size(),1)
            Do messages.%Push({"role":"tool","content":"synthetic test result"})
        } Else {
            Set proposal = ##class(%DynamicObject).%FromJSON(choice.message.content)
            Do $$$AssertEquals(proposal.decision,"QUARANTINE")
            Do $$$AssertEquals(proposal.%Get("evidence_ids").%Get(0),"contract:PO-2048:v1")
            Do $$$AssertEquals(choice.%Get("finish_reason"),"stop")
        }
    }
    Set rejected = 0
    Try { Set ignored = ##class(SilentShift.Provider.Replay).Response("{""messages"":[]}",5) } Catch error { Set rejected = 1 }
    Do $$$AssertTrue(rejected,"A final response cannot skip the four native evidence reads")
    Set rejected = 0
    Try { Set ignored = ##class(SilentShift.Provider.Replay).Response("{""messages"":[]}",6) } Catch error { Set rejected = 1 }
    Do $$$AssertTrue(rejected,"Playback has only five bounded responses")
}

Method TestPlaybackScopeAndCriticalPolicy()
{
    Set data = ##class(%DynamicObject).%FromJSON(..ExampleCase())
    Do $$$AssertTrue(##class(SilentShift.Provider.Replay).MatchesCase(data.%ToJSON()))
    Do data.%Set("synthetic",0,"boolean")
    Do $$$AssertTrue('##class(SilentShift.Provider.Replay).MatchesCase(data.%ToJSON()))
    Do data.%Set("synthetic",1,"boolean")
    Do data.message.%Set("quantity","21")
    Do $$$AssertTrue('##class(SilentShift.Provider.Replay).MatchesCase(data.%ToJSON()))
    Set assessment = {"classification":"VERIFIED_CONTRADICTION","critical":true,"findings":[{"severity":"critical"}],"evidence_ids":["contract:PO-2048:v1"],"active_reference_ids":["contract:PO-2048:v1"]}
    Set malicious = {"decision":"ALLOW","evidence_ids":["contract:PO-2048:v1"],"explanation":"Misleading recorded output","uncertainty":0}
    Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessment.%ToJSON(),malicious.%ToJSON()))
    Do $$$AssertTrue('policy.%Get("downstream_permitted"))
    Do $$$AssertEquals(policy.decision,"QUARANTINE")
}

ClassMethod ExampleCase() As %String [ Language = python ]
{
    import iris,json
    from pathlib import Path
    dataset=json.loads(Path(iris.cls('SilentShift.IPM').AssetPath('fixtures/v1/scenarios.json')).read_text())
    message=next(s['message'] for s in dataset['scenarios'] if s['id']=='quantity-mismatch')
    return json.dumps({'synthetic':True,'scenario_id':'quantity-mismatch','routing':'PROCESSING',
        'dataset_version':dataset['dataset_version'],'message':message,
        'assessment':{'critical':True,'evidence_ids':['contract:PO-2048:v1']}})
}
}
