Include (%occStatus, %outUnitTest)

/// The round-trip tests require the real Java gateway; no model calls.
Class SilentShift.Test.PEXChecks Extends %UnitTest.TestCase
{
/// Persisted replay provenance must win even when this process runs in live
/// mode. Arrange synthetic durable state, then use the real Java operation.
Method TestPersistedExecutionModeAndRetry()
{
    Set data = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Test.ReplayChecks).ExampleCase())
    Set message = data.%Get("message"), uuid = $TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
    Do message.%Set("event_id",uuid),message.%Set("source","synthetic-pex-mode-regression")
    Set envelope = {"message":(message),"raw_payload":(message.%ToJSON()),"scenario_id":"quantity-mismatch","dataset_version":"synthetic-pex-mode-regression/1"}
    Set sc = ##class(SilentShift.Store).CreateCase(envelope.%ToJSON(),.id,.duplicate)
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Do body.%Set("agent",{"mode":"native-ai-hub-recorded-replay","execution_mode":"recorded-replay"})
    Do body.%Set("routing","QUARANTINED")
    Set sc = ##class(SilentShift.Store).SaveCase(id,body.%ToJSON())
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Set request = ##class(SilentShift.PEX.Support).Request(id)
    Set payload = ##class(%DynamicObject).%FromJSON(request.PayloadJSON)
    Do $$$AssertEquals(payload.%Get("execution_mode"),"recorded-replay","Persisted replay mode overrides the deployment environment")
    Set sc = ##class(Ens.Director).CreateBusinessService("Partner",.service)
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Set sc = service.SendRequestSync("ReceiptExporter",request,.reply,15)
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Set first = reply.ReceiptJSON
    Do $$$AssertTrue(reply.SignatureValid)
    Set request = ##class(SilentShift.PEX.Support).Request(id)
    Set sc = service.SendRequestSync("ReceiptExporter",request,.retried,15)
    Do $$$AssertStatusOK(sc)
    If $$$ISOK(sc) Do $$$AssertEquals(first,retried.ReceiptJSON,"Reconstructed request reuses the original signed receipt")
    Set after = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Do $$$AssertEquals(after.%Get("routing"),"QUARANTINED")
    Do $$$AssertEquals(after.%Get("delivery_count"),0)
}

Method TestLegacyAndInvalidExecutionModes()
{
    Do $$$AssertEquals(##class(SilentShift.PEX.Support).ExecutionMode({"execution_mode":"live","mode":"native-ai-hub-recorded-replay"}),"live","Explicit persisted mode is authoritative")
    Do $$$AssertEquals(##class(SilentShift.PEX.Support).ExecutionMode({"mode":"native-ai-hub-recorded-replay"}),"recorded-replay","Legacy replay provenance remains recognizable")
    Do $$$AssertEquals(##class(SilentShift.PEX.Support).ExecutionMode({"mode":"native-ai-hub"}),"live","Legacy live provenance remains recognizable")
    For value = "{}", "null", "{""execution_mode"":""unknown"",""mode"":""native-ai-hub""}", "{""execution_mode"":null}", "{""execution_mode"":""""}" {
        Set rejected = 0
        Try { Set ignored = ##class(SilentShift.PEX.Support).ExecutionMode(##class(%DynamicObject).%FromJSON(value)) } Catch error { Set rejected = 1 }
        Do $$$AssertTrue(rejected,"Unknown or malformed provenance must not be relabeled from the environment")
    }
}

Method TestRealGatewayRoundTripAndRetry()
{
    Set sc = ##class(Ens.Director).CreateBusinessService("Partner", .service)
    Do $$$AssertStatusOK(sc)
    Set request = ##class(SilentShift.PEX.ExportRequest).%New()
    Set request.CaseId = "native-java-"_$TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
    Set request.Decision = "QUARANTINED"
    Set hash = ##class(SilentShift.Bridge).Hash("synthetic native evidence")
    Set request.PayloadJSON = {"case_id":(request.CaseId),"decision":"QUARANTINED","evidence_hashes":[(hash)],"execution_mode":"recorded-replay","synthetic":true}.%ToJSON()
    Set sc = service.SendRequestSync("ReceiptExporter",request,.reply,15)
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Do $$$AssertTrue(reply.SignatureValid,"Real Java PEX verifies its RSA signature")
    Set first = reply.ReceiptJSON, receipt = ##class(%DynamicObject).%FromJSON(first)
    Do $$$AssertEquals(receipt.%Get("signed").%Get("sha256"),##class(SilentShift.Bridge).Hash(##class(SilentShift.Bridge).Canonical(request.PayloadJSON)))
    Set sc = service.SendRequestSync("ReceiptExporter",request,.retried,15)
    Do $$$AssertStatusOK(sc)
    If $$$ISOK(sc) Do $$$AssertEquals(first,retried.ReceiptJSON,"Retry retains original timestamp and signature")
}

Method TestInvalidJavaRequestCannotCreateReceipt()
{
    Set sc = ##class(Ens.Director).CreateBusinessService("Partner", .service)
    Do $$$AssertStatusOK(sc)
    Set request = ##class(SilentShift.PEX.ExportRequest).%New()
    Set request.CaseId = "invalid-synthetic-export", request.Decision = "ALLOW", request.PayloadJSON = "{}"
    Set sc = service.SendRequestSync("ReceiptExporter",request,.reply,15)
    Do $$$AssertTrue($$$ISERR(sc),"Java operation rejects a non-final, malformed outcome")
}

/// A stopped Java host must not turn a committed hold into a routing failure.
Method TestUnavailableExporterPreservesRouting()
{
    Set sc = ##class(SilentShift.Test.TraceChecks).RunBudgetCase(.id)
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Set before = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Set stopped = 0
    Try {
        Set sc = ##class(Ens.Director).TempStopConfigItem("ReceiptExporter",1,1)
        Do $$$AssertStatusOK(sc)
        If $$$ISOK(sc) {
            Set stopped = 1
            Set sc = ##class(Ens.Director).CreateBusinessService("Partner", .service)
            Do $$$AssertStatusOK(sc)
            Set request = ##class(SilentShift.Message).%New(), request.CaseId = id
            Set routeStatus = service.SendRequestSync("Quarantine",request,.reply,15)
            Do $$$AssertStatusOK(routeStatus,"Java outage does not change the successful committed route")
        }
    } Catch error {
        Do $$$AssertTrue(0,"Unexpected native outage test exception")
    }
    If stopped {
        Set sc = ##class(Ens.Director).TempStopConfigItem("ReceiptExporter",0,1)
        Do $$$AssertStatusOK(sc,"Restore the isolated Java operation after the outage test")
    }
    Set after = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Do $$$AssertEquals(after.%Get("routing"),before.%Get("routing"),"Java outage cannot change a hold")
    Do $$$AssertEquals(after.%Get("delivery_count"),0,"Java outage creates no simulator delivery")
}

/// Explicit live driver, excluded from automatic keyless unit runs. It submits
/// each frozen envelope through Partner.ProcessInput, exactly as the API does.
ClassMethod RunFrozen(allowLocalModelCalls As %Boolean = 0, Output reportJSON As %String) As %Status
{
    Try {
        If 'allowLocalModelCalls || '##class(SilentShift.Test.TraceChecks).LocalRouteSafe() Return $$$ERROR($$$GeneralError,"Explicit local model opt-in is required")
        If $SYSTEM.Util.GetEnviron("SILENTSHIFT_PROVIDER_MODE") = "recorded-replay" Return $$$ERROR($$$GeneralError,"Five-scenario Java test requires live local inference")
        Set data = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON()), ids = []
        For index = 0:1:data.scenarios.%Size()-1 {
            Set scenario = data.scenarios.%Get(index), message = scenario.%Get("message")
            Set run = $TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
            Do message.%Set("event_id",message.%Get("event_id")_"-"_run),message.%Set("correlation_id",run)
            Set envelope = {"message":(message),"raw_payload":(message.%ToJSON()),"scenario_id":(scenario.%Get("id")),"dataset_version":(data.%Get("dataset_version")),"clock":(data.%Get("clock"))}
            If scenario.%Get("id") = "unsafe-agent-output" Do envelope.%Set("fault",scenario.%Get("test_recommendation"))
            Set stream = ##class(%Stream.GlobalCharacter).%New(), sc = stream.Write(envelope.%ToJSON())
            $$$ThrowOnError(sc)
            Kill service
            Set sc = ##class(Ens.Director).CreateBusinessService("Partner",.service)
            $$$ThrowOnError(sc)
            Set sc = service.ProcessInput(stream,.reply)
            $$$ThrowOnError(sc)
            Set body = ##class(%DynamicObject).%FromJSON(reply.BodyJSON)
            Do ids.%Push(body.%Get("id"))
        }
        Return ..CheckFrozen(ids.%ToJSON(),.reportJSON)
    } Catch error { Return error.AsStatus() }
}

/// Check the actual cases just run through the native API; never invent a route.
ClassMethod CheckFrozen(caseIDsJSON As %String, Output reportJSON As %String) As %Status
{
    Try {
        Set ids = ##class(%DynamicArray).%FromJSON(caseIDsJSON), cases = [], seen = "|"
        If ids.%Size() '= 5 Return $$$ERROR($$$GeneralError,"Five real native scenario IDs are required")
        Set fixtures = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
        For index = 0:1:ids.%Size()-1 {
            Set id = ids.%Get(index), body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
            Set scenario = body.%Get("scenario_id"), expected = "", matched = 0
            For fi = 0:1:fixtures.scenarios.%Size()-1 {
                Set fixture = fixtures.scenarios.%Get(fi)
                If fixture.%Get("id") = scenario {
                    Set matched = 1, expected = fixture.%Get("ground_truth").%Get("decision")
                }
            }
            If 'matched || (seen[("|"_scenario_"|")) Return $$$ERROR($$$GeneralError,"Scenario IDs must cover the frozen five exactly once")
            Set seen = seen_scenario_"|"
            Set agent = body.%Get("agent"), reads = agent.%Get("tool_reads")
            If (agent.%Get("mode") '= "native-ai-hub") || (agent.%Get("status") '= "returned") Return $$$ERROR($$$GeneralError,"Live native investigation did not return")
            For tool = "message", "contracts", "related", "precedents" {
                If reads.%Get(tool) < 1 Return $$$ERROR($$$GeneralError,"Live native evidence read missing")
            }
            Set inspection = ..Inspect(id)
            If 'inspection.%Get("passed") Return $$$ERROR($$$GeneralError,"Native Java receipt assertion failed")
            If body.%Get("policy").%Get("decision") '= expected Return $$$ERROR($$$GeneralError,"Frozen policy result changed")
            Do cases.%Push(inspection)
        }
        Set report = {"suite":"java-pex-frozen-cases/1","runtime":($ZVERSION),"cases":(cases),"passed":true}
        Set reportJSON = report.%ToJSON()
        Return $$$OK
    } Catch error { Return error.AsStatus() }
}

ClassMethod Inspect(id As %String) As %DynamicObject
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id)), session = body.%Get("trace_id")
    Set statement = ##class(%SQL.Statement).%New()
    Set sc = statement.%Prepare("SELECT ID,MessageBodyId FROM Ens.MessageHeader WHERE SessionId=? AND MessageBodyClassName='SilentShift.PEX.ExportResponse' ORDER BY ID")
    $$$ThrowOnError(sc)
    Set rows = statement.%Execute(+session), count = 0, valid = 0, receipt = {}, header = ""
    While rows.%Next() {
        Set reply = ##class(SilentShift.PEX.ExportResponse).%OpenId(rows.%Get("MessageBodyId"))
        If $ISOBJECT(reply) {
            Set receipt = ##class(%DynamicObject).%FromJSON(reply.ReceiptJSON), signed = receipt.%Get("signed"), payload = signed.%Get("payload")
            If payload.%Get("case_id") = id {
                Set count = count+1, header = rows.%Get("ID")
                Set valid = reply.SignatureValid && (signed.%Get("sha256") = ##class(SilentShift.Bridge).Hash(##class(SilentShift.Bridge).Canonical(payload.%ToJSON()))) && (payload.%Get("decision") = body.%Get("routing"))
            }
        }
    }
    Set request = ##class(SilentShift.PEX.Support).Request(id)
    Set exported = receipt.%Get("signed")
    If $ISOBJECT(exported) Set valid = valid && (exported.%Get("sha256") = ##class(SilentShift.Bridge).Hash(##class(SilentShift.Bridge).Canonical(request.PayloadJSON)))
    Return {"case_id":(id),"scenario_id":(body.%Get("scenario_id")),"routing":(body.%Get("routing")),"session_id":(session),"receipt_responses":(count),"response_header_id":(header),"hash_and_signature_valid":(valid),"receipt":(receipt),"passed":((count=1)&&valid)}
}
}
