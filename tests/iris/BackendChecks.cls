Include (%occStatus, %outUnitTest)

/// No inference: regression checks for shared configuration and diagnostics.
Class SilentShift.Test.BackendChecks Extends %UnitTest.TestCase
{
Method TestPromptBytes()
{
    Set prompt = ##class(SilentShift.AI.Investigator).SystemPrompt()
    Do $$$AssertEquals($LENGTH($ZCONVERT(prompt, "O", "UTF8")), 1959)
    Do $$$AssertEquals(##class(SilentShift.Bridge).Hash(prompt), "6e7453ef1af46af157c64dbc0ea93953da508c5b278b3dd1c25b71b5ff7aedc3")
}

Method TestExactToolAllowlist()
{
    For name = "GetCurrentMessage", "GetApprovedContracts", "GetRelatedRecords", "find_similar_precedents" {
        Do $$$AssertTrue(##class(SilentShift.AI.Investigator).IsAllowedTool(name))
    }
    For name = "", "GetCurrentMessage,GetApprovedContracts", "GetCurrentMessage|GetApprovedContracts", "getcurrentmessage", "SQL" {
        Do $$$AssertTrue('##class(SilentShift.AI.Investigator).IsAllowedTool(name))
    }
}

Method TestBoundedRedactedDiagnostic()
{
    Set message = $JUSTIFY("", 2200)
    Do $$$AssertEquals($LENGTH(##class(SilentShift.IPM).RedactDiagnostic(message)), 2048)
    For name = "SILENTSHIFT_IRIS_PASSWORD", "SILENTSHIFT_VIEWER_PASSWORD", "SILENTSHIFT_GATEWAY_PASSWORD", "SILENTSHIFT_API_KEY" {
        Set secret = $SYSTEM.Util.GetEnviron(name)
        If secret '= "" {
            Set result = ##class(SilentShift.IPM).RedactDiagnostic("before "_secret_" after")
            Do $$$AssertTrue(result '[ secret)
            Do $$$AssertTrue(result [ "[REDACTED]")
        }
    }
}

Method TestSharedDefaultAndCatalog()
{
    Do $$$AssertEquals(##class(SilentShift.Provider.Config).DefaultModel(), "qwen3-silentshift:4b-instruct")
    Set rules = ##class(%DynamicArray).%FromJSON(##class(SilentShift.Bridge).PolicyRules())
    Do $$$AssertEquals(rules.%Size(), 7)
    Do $$$AssertEquals(rules.%Get(4).%Get("description"), "Uncertainty above 0.35 requires review.")
}

Method TestCompactAcknowledgment()
{
    Set fixture = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
    Set message = fixture.%Get("scenarios").%Get(0).%Get("message")
    Do message.%Set("event_id", $SYSTEM.Util.CreateGUID())
    Set envelope = {"message": (message), "scenario_id": "synthetic-compact-reply-check"}
    Set sc = ##class(SilentShift.Store).CreateCase(envelope.%ToJSON(), .id, .duplicate)
    Do $$$AssertStatusOK(sc)
    If $$$ISERR(sc) Quit
    Set result = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).SummaryJSON(id))
    Do $$$AssertEquals(result.%Size(), 3)
    Do $$$AssertEquals(result.%Get("case_id"), id)
    Do $$$AssertEquals(result.%Get("routing"), "PROCESSING")
    Do $$$AssertEquals(result.%Get("version"), 1)
    Set full = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Do $$$AssertTrue(full.%IsDefined("message"))
    Do $$$AssertTrue(full.%IsDefined("events"))
}


Method TestDefaultHostSettings()
{
    Set value = ##class(Ens.Director).GetHostSettingValue("Semantic", "StepTimeoutSeconds", .sc)
    Do $$$AssertStatusOK(sc)
    Do $$$AssertEquals(value, 10)
    Set value = ##class(Ens.Director).GetHostSettingValue("Semantic", "MaxReferencesPerAuthority", .sc)
    Do $$$AssertStatusOK(sc)
    Do $$$AssertEquals(value, 10)
    For setting = "AgentWaitSeconds", "Model" {
        Set value = ##class(Ens.Director).GetHostSettingValue("Investigator", setting, .sc)
        Do $$$AssertStatusOK(sc)
        Do $$$AssertEquals(value, "")
    }
    Do $$$AssertEquals(##class(SilentShift.Provider.Config).ModelSetting(), "")
    Set expected = $SYSTEM.Util.GetEnviron("SILENTSHIFT_AGENT_WAIT_SECONDS")
    If expected = "" Set expected = 60
    Do $$$AssertEquals(##class(SilentShift.AI.Investigator).WaitSeconds(), +expected)
    Set value = ##class(Ens.Director).GetAdapterSettingValue("PartnerFiles", "InboxPath", .sc)
    Do $$$AssertStatusOK(sc)
    Do $$$AssertEquals(value, ##class(SilentShift.Adapter.PartnerJSON).#ROOT)
    Do $$$AssertTrue('##class(SilentShift.Adapter.PartnerJSON).RootSafe("relative/inbox"))
    Do $$$AssertTrue('##class(SilentShift.Adapter.PartnerJSON).RootSafe("/tmp/../tmp"))
}
}
