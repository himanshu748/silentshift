Include %occStatus

/// Operator-only synthetic evaluation harness. Not in module.xml or production.
Class SilentShift.Test.HeldoutEval Extends %RegisteredObject
{
ClassMethod Identity() As %String
{
    Set result = {"runtime":($ZVERSION),"namespace":($NAMESPACE),"model":($SYSTEM.Util.GetEnviron("SILENTSHIFT_MODEL")),"prompt_version":(##class(SilentShift.AI.Investigator).#PROMPTVERSION),"execution_mode":(##class(SilentShift.Provider.Lease).ExecutionMode()),"module_version":(##class(%IPM.Storage.Module).NameOpen("silentshift").VersionString)}
    Do result.%Set("assets",##class(%DynamicObject).%FromJSON(..AssetIdentity()))
    Return result.%ToJSON()
}

ClassMethod AssetIdentity() As %String [ Language = python ]
{
    import iris, hashlib, json, pathlib, platform, sys
    root = pathlib.Path(iris.cls('SilentShift.IPM').AssetPath('python'))
    return json.dumps({'engine_sha256': hashlib.sha256((root/'silentshift/engine.py').read_bytes()).hexdigest(), 'architecture': platform.machine(), 'python': sys.version.split()[0]})
}

ClassMethod Initialize(path As %String, runId As %String) As %String
{
    If $DATA(^SilentShiftHeldout(runId)) Throw ##class(%Exception.General).%New("HELDOUT_RUN_ALREADY_EXISTS")
    Set stream=##class(%Stream.FileCharacter).%New(),stream.Filename=path
    If stream.Size>1000000 Throw ##class(%Exception.General).%New("HELDOUT_INPUT_BOUNDS")
    Set data=##class(%DynamicObject).%FromJSON(stream.Read(1000001)),items=data.%Get("scenarios")
    Set ^SilentShiftHeldout(runId,"clock")=data.%Get("clock")
    Set ^SilentShiftHeldout(runId,"version")=data.%Get("dataset_version")
    For i=0:1:items.%Size()-1 {
        Set item=items.%Get(i),sid=item.%Get("id")
        If item.%Size()'=3 Throw ##class(%Exception.General).%New("HELDOUT_LABEL_LEAK")
        If 'item.%IsDefined("message") || 'item.%IsDefined("references") Throw ##class(%Exception.General).%New("HELDOUT_INPUT_FIELDS")
        Set ^SilentShiftHeldout(runId,"input",sid)=item.%ToJSON()
    }
    Return {"initialized":true,"cases":(items.%Size())}.%ToJSON()
}

ClassMethod Rules(runId As %String, sid As %String) As %String
{
    Return ..RulesPython(^SilentShiftHeldout(runId,"input",sid),^SilentShiftHeldout(runId,"clock"))
}

ClassMethod RulesPython(raw As %String, clock As %String) As %String [ Language = python ]
{
    import iris, json, sys, time
    root=iris.cls('SilentShift.IPM').AssetPath('python')
    if root not in sys.path:
        sys.path.insert(0,root)
    from silentshift.engine import assess, rule_only
    item=json.loads(raw)
    started=time.perf_counter_ns()
    assessment=assess(item['message'],item['references'],clock)
    decision=rule_only(assessment)
    elapsed=(time.perf_counter_ns()-started)/1e6
    return json.dumps({'scenario_id':item['id'],'decision':decision,'assessment':assessment,'elapsed_ms':elapsed})
}

ClassMethod Envelope(runId As %String, sid As %String, trial As %Integer) As %DynamicObject
{
    Set input=##class(%DynamicObject).%FromJSON(^SilentShiftHeldout(runId,"input",sid)),message=input.%Get("message")
    Do message.%Set("event_id",message.%Get("event_id")_":"_runId_":"_trial)
    Do message.%Set("correlation_id",message.%Get("correlation_id")_":"_runId_":"_trial)
    Set scope="heldout:"_runId_":"_trial_":"_sid
    Return {"message":(message),"raw_payload":(message.%ToJSON()),"scenario_id":(scope),"dataset_version":(^SilentShiftHeldout(runId,"version")),"clock":(^SilentShiftHeldout(runId,"clock"))}
}

ClassMethod Read(runId As %String, sid As %String, trial As %Integer) As %String
{
    Set envelope=..Envelope(runId,sid,trial),message=envelope.%Get("message"),id=""
    Set key=##class(SilentShift.Bridge).PairHash(message.%Get("source"),message.%Get("event_id"))
    &sql(SELECT CaseId INTO :id FROM SilentShift_Data.CaseRecord WHERE EventKey=:key)
    If SQLCODE<0 Throw ##class(%Exception.General).%New("HELDOUT_READ_FAILED")
    If id="" Return {"exists":false}.%ToJSON()
    Set record=##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Set result={"exists":true,"record":(record),"service_elapsed_ms":null}
    If $DATA(^SilentShiftHeldout(runId,"elapsed",sid,trial)) Do result.%Set("service_elapsed_ms",^SilentShiftHeldout(runId,"elapsed",sid,trial),"number")
    Return result.%ToJSON()
}

ClassMethod Run(runId As %String, sid As %String, trial As %Integer) As %String
{
    If (trial<1) || (trial>3) Throw ##class(%Exception.General).%New("HELDOUT_TRIAL_BOUNDS")
    Set prior=##class(%DynamicObject).%FromJSON(..Read(runId,sid,trial))
    If prior.%Get("exists") Return prior.%ToJSON()
    Set envelope=..Envelope(runId,sid,trial),input=##class(%DynamicObject).%FromJSON(^SilentShiftHeldout(runId,"input",sid)),refs=input.%Get("references")
    For i=0:1:refs.%Size()-1 {
        Set sc=..SeedReference(envelope.%Get("scenario_id"),refs.%Get(i))
        $$$ThrowOnError(sc)
    }
    Set stream=##class(%Stream.GlobalCharacter).%New()
    Do stream.Write(envelope.%ToJSON()),stream.Rewind()
    Set sc=##class(Ens.Director).CreateBusinessService("Partner",.service)
    $$$ThrowOnError(sc)
    Set ^SilentShiftHeldout(runId,"attempt",sid,trial)=$ZTIMESTAMP,started=$ZTIMESTAMP
    Set sc=service.ProcessInput(stream,.reply)
    Set ^SilentShiftHeldout(runId,"elapsed",sid,trial)=##class(SilentShift.TraceEvent).ElapsedMS(started)
    Set result=##class(%DynamicObject).%FromJSON(..Read(runId,sid,trial))
    Do result.%Set("service_status_ok",$SYSTEM.Status.IsOK(sc),"boolean")
    Return result.%ToJSON()
}

/// Same scoped test-catalog insertion used by existing native boundary tests.
/// Setup.SeedReference is private; no shipped method visibility is changed.
ClassMethod SeedReference(scope As %String, reference As %DynamicObject) As %Status [ Private ]
{
    Set key=##class(SilentShift.Bridge).PairHash(scope,reference.%Get("id"))
    Set canonical=##class(SilentShift.Bridge).Canonical(reference.%ToJSON())
    Set row=##class(SilentShift.Data.Reference).%OpenId(key)
    If $ISOBJECT(row) {
        If row.Body'=canonical Return $$$ERROR($$$GeneralError,"Frozen held-out reference differs")
        Return $$$OK
    }
    Set row=##class(SilentShift.Data.Reference).%New()
    Set row.ReferenceKey=key,row.ReferenceId=reference.%Get("id"),row.ScenarioScope=scope
    Set row.ContractId=reference.%Get("contract_id"),row.Body=canonical
    Return row.%Save()
}
}
