Include (%occStatus, Ensemble)

/// Explicit local SDK diagnostics, never part of the frozen five-case dataset.
/// The failure mode asks the real local endpoint to reject an invalid format.
Class SilentShift.Test.ProviderProbe Extends %RegisteredObject
{
ClassMethod Run(kind As %String, Output id As %String, Output summary As %String) As %Status
{
    Set token = "", id = "", summary = ""
    Try {
        If (kind '= "basic") && (kind '= "failure") Return $$$ERROR($$$GeneralError,"PROBE_KIND_INVALID")
        Set sc = ##class(SilentShift.Provider.Lease).LocalHost(.host)
        $$$ThrowOnError(sc)
        Set fixtures = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
        Set message = ##class(%DynamicObject).%FromJSON(fixtures.scenarios.%Get(0).message.%ToJSON())
        Set unique = $TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
        Do message.%Set("event_id","provider-probe-"_unique)
        Do message.%Set("correlation_id","provider-probe-"_unique)
        Do message.%Set("source","silentshift-local-provider-probe")
        Do message.%Set("occurred_at",##class(SilentShift.Bridge).Now())
        Do message.%Set("notes","Synthetic native SDK transport diagnostic; never a business delivery.")
        Set envelope = {"message":(message),"raw_payload":(message.%ToJSON())}
        Set sc = ##class(SilentShift.Store).CreateCase(envelope.%ToJSON(),.id,.duplicate)
        $$$ThrowOnError(sc)
        // Mark the newly created, isolated diagnostic truthfully as synthetic.
        Set record = ##class(SilentShift.Data.CaseRecord).%OpenId(id)
        Set initial = ##class(%DynamicObject).%FromJSON(record.Body)
        Do initial.%Set("synthetic",1,"boolean")
        Set record.Body = initial.%ToJSON(), sc = record.%Save(), record = ""
        $$$ThrowOnError(sc)
        Set request = ##class(SilentShift.Message).%New(), request.CaseId = id
        Set sc = ##class(Ens.Director).CreateBusinessService("Partner",.service)
        $$$ThrowOnError(sc)
        Set service.%PreserveSession = 1
        // This genuine reference operation allocates the native case session.
        Set sc = service.SendRequestSync("References",request,.referenceReply,10)
        $$$ThrowOnError(sc)
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        Do body.%Set("trace_id",service.%SessionId_"")
        Set assessmentJSON = ##class(SilentShift.Bridge).Assess(body.%Get("raw_payload"),body.%Get("references").%ToJSON(),body.%Get("clock"))
        Do body.%Set("assessment",##class(%DynamicObject).%FromJSON(assessmentJSON))
        Set sc = ##class(SilentShift.Store).SaveCase(id,body.%ToJSON())
        $$$ThrowOnError(sc)
        Set invocation = $TRANSLATE($SYSTEM.Util.CreateGUID(),"{}","")
        Set sc = ##class(SilentShift.Provider.Lease).Open(id,service.%SessionId,"qwen3-silentshift:4b-instruct","provider-protocol-probe/1",.token,invocation)
        $$$ThrowOnError(sc)
        Set provider = ##class(%AI.Provider).Create("openai",{"api_key":(token),"base_url":"http://gateway/silentshift-provider/v1/"})
        Set agent = ##class(%AI.Agent).%New(provider), sc = agent.%Init()
        $$$ThrowOnError(sc)
        Set agent.Model = "qwen3-silentshift:4b-instruct", agent.SystemPrompt = "This is a local transport diagnostic. Reply OK."
        Set config = {"max_iterations":1,"max_tokens":16,"extra_params":{"reasoning_effort":"none"}}
        If kind = "failure" Do config.%Get("extra_params").%Set("response_format",42)
        Set session = agent.CreateSession(config), caught = 0, gatewayCode = "", content = ""
        Try {
            Set result = agent.Chat(session,"Reply OK. /no_think"), content = $EXTRACT(result.Content,1,256)
        } Catch providerError {
            Set caught = 1, diagnostic = $SYSTEM.Status.GetErrorText(providerError.AsStatus())
            // Keep only our own fixed error identifiers, never SDK exceptions,
            // request headers, opaque capabilities or upstream body content.
            For known = "PROVIDER_LEASE_REQUIRED","PROVIDER_GATEWAY_FAILED","PROVIDER_FIELD_REJECTED","PROVIDER_TOKEN_BUDGET_REQUIRED","PROVIDER_TOKEN_BUDGET_REJECTED","PROVIDER_RESPONSE_BOUNDS" {
                If diagnostic [ known Set gatewayCode = known
            }
            Set diagnostic = ""
        }
        Set calls = +$GET(^CacheTemp.SilentShift.Provider("lease",##class(SilentShift.Provider.Lease).TokenKey(token),"count"))
        Do ##class(SilentShift.Provider.Lease).Close(token)
        Set token = ""
        Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        Set metadata = {"mode":"native-ai-hub","status":($SELECT(caught:"failed",1:"returned")),"model":"qwen3-silentshift:4b-instruct","probe_kind":(kind),"synthetic":true,"prompt_version":"provider-protocol-probe/1","provider_request_count":(calls),"trace":{"invocation_id":(invocation)},"tool_reads":{"message":0,"contracts":0,"related":0},"provider_failure_caught":(caught),"gateway_error_code":(gatewayCode),"diagnostic_content":(content),"scope":"SDK transport diagnostic; no business recommendation or model-quality claim."}
        Do metadata.%Set("provider_failure_caught",caught,"boolean")
        Do body.%Set("agent",metadata)
        Do body.%Set("policy",##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON,"")))
        Set sc = ##class(SilentShift.Store).SaveCase(id,body.%ToJSON())
        $$$ThrowOnError(sc)
        // The actual critical assessment and missing proposal keep this held.
        Set sc = service.SendRequestSync("Quarantine",request,.heldReply,10)
        $$$ThrowOnError(sc)
        Set final = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
        Set summary = {"case_id":(id),"kind":(kind),"trace_id":(service.%SessionId),"provider_requests":(calls),"failure_caught":(caught),"gateway_error_code":(gatewayCode),"route":(final.%Get("routing")),"delivery_count":(final.%Get("delivery_count"))}.%ToJSON()
        Return $$$OK
    } Catch error {
        If token '= "" Do ##class(SilentShift.Provider.Lease).Close(token)
        Return $$$ERROR($$$GeneralError,"LOCAL_PROVIDER_PROBE_FAILED")
    }
}
}
