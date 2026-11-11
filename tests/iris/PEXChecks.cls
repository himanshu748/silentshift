Include (%occStatus, %outUnitTest)

/// The round-trip tests require the real Java gateway; no model calls.
Class SilentShift.Test.PEXChecks Extends %UnitTest.TestCase
{
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
