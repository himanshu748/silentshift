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
}
