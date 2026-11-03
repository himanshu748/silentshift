Include (Ensemble, %occStatus)

Class SilentShift.Setup Extends %RegisteredObject
{
/// Compiles separately in bootstrap; installs references and starts hosts without
/// injecting messages or invoking a model. Repeat installation preserves cases.
ClassMethod Install() As %Status
{
    Try {
        If '##class(SilentShift.Bridge).IsRequiredBuild($ZVERSION) Return $$$ERROR($$$GeneralError, "APP_INVALID: required IRIS AI Hub build is 2026.3.0AI.154.0")
        If $NAMESPACE '= "SILENTSHIFT" Return $$$ERROR($$$GeneralError, "APP_INVALID: install requires SILENTSHIFT namespace")
        Set sc = ..SecurityConfig()
        $$$ThrowOnError(sc)
        // Dynamic SQL checks table privileges independently of database RW.
        // Only the application-scoped role receives these fixed read grants.
        For table = "CaseRecord", "Reference", "AuditEvent", "Delivery", "ReviewAction", "Evaluation" {
            Set sc = $SYSTEM.SQL.Security.GrantPrivilege("SELECT", "SilentShift_Data."_table, "TABLE", "SSApplication")
            $$$ThrowOnError(sc)
        }
        Set data = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).FixtureJSON())
        Set scenarios = data.%Get("scenarios")
        For index = 0:1:scenarios.%Size()-1 {
            Set scenario = scenarios.%Get(index), references = scenario.%Get("references")
            For referenceIndex = 0:1:references.%Size()-1 {
                Set reference = references.%Get(referenceIndex)
                Set sc = ..SeedReference(scenario.%Get("id"), reference.%ToJSON())
                $$$ThrowOnError(sc)
                // General ingress has its own approved catalog; it is never
                // selected from a partner-supplied scenario or reference object.
                If scenario.%Get("id") = "quantity-mismatch" {
                    Set sc = ..SeedReference("", reference.%ToJSON())
                    $$$ThrowOnError(sc)
                }
            }
        }
        Set sc = ##class(Ens.Director).SetAutoStart("SilentShift.Production")
        $$$ThrowOnError(sc)
        Set sc = ##class(Ens.Director).GetProductionStatus(.name, .state)
        $$$ThrowOnError(sc)
        If state = $$$eProductionStateRunning {
            If name '= "SilentShift.Production" Return $$$ERROR($$$GeneralError, "APP_CONFLICT: another production is running")
            Return $$$OK
        }
        If state '= $$$eProductionStateStopped Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: production requires operator recovery")
        Return ##class(Ens.Director).StartProduction("SilentShift.Production")
    } Catch error {
        Return $$$ERROR($$$GeneralError, "APP_UNAVAILABLE: native setup failed; inspect local compile/setup diagnostics")
    }
}

ClassMethod SeedReference(scope As %String, referenceJSON As %String) As %Status [ Private ]
{
    Set reference = ##class(%DynamicObject).%FromJSON(referenceJSON)
    Set key = ##class(SilentShift.Bridge).PairHash(scope, reference.%Get("id"))
    Set canonical = ##class(SilentShift.Bridge).Canonical(referenceJSON)
    Set record = ##class(SilentShift.Data.Reference).%OpenId(key)
    If $ISOBJECT(record) {
        If record.Body '= canonical Return $$$ERROR($$$GeneralError, "APP_CONFLICT: frozen reference differs from persisted catalog")
        Return $$$OK
    }
    Set record = ##class(SilentShift.Data.Reference).%New()
    Set record.ReferenceKey = key, record.ReferenceId = reference.%Get("id"), record.ScenarioScope = scope
    Set record.ContractId = reference.%Get("contract_id"), record.Body = canonical
    Return record.%Save()
}

ClassMethod SecurityConfig() As %Status [ Private ]
{
    New $NAMESPACE
    Set $NAMESPACE = "%SYS"
    For name = "SSView", "SSReview" {
        If '##class(Security.Resources).Exists(name) {
            Set sc = ##class(Security.Resources).Create(name, "SilentShift application permission", 0)
        } Else {
            Kill resourceProperties
            Set resourceProperties("PublicPermission") = 0
            Set sc = ##class(Security.Resources).Modify(name, .resourceProperties)
        }
        $$$ThrowOnError(sc)
    }
    // Database authority is application-scoped, never permanently granted to
    // viewer/reviewer users. Reinstall also repairs earlier owned role grants.
    For role = "SSViewer", "SSReviewer", "SSApplication" {
        Set resources = $SELECT(role = "SSViewer": "SSView:U", role = "SSReviewer": "SSReview:U", 1: "%DB_SILENTSHIFT:RW,%Service_EmbeddedPython:U")
        Set inherited = $SELECT(role = "SSReviewer": "SSViewer", 1: "")
        If ##class(Security.Roles).Exists(role) {
            Kill roleProperties
            Set roleProperties("Resources") = resources, roleProperties("GrantedRoles") = inherited
            Set sc = ##class(Security.Roles).Modify(role, .roleProperties)
        } Else {
            Set sc = ##class(Security.Roles).Create(role, "SilentShift scoped application access", resources, inherited)
        }
        $$$ThrowOnError(sc)
    }
    For role = "SSViewer", "SSReviewer" {
        Set username = $SYSTEM.Util.GetEnviron($SELECT(role = "SSViewer": "SILENTSHIFT_VIEWER_USERNAME", 1: "SILENTSHIFT_IRIS_USERNAME"))
        Set password = $SYSTEM.Util.GetEnviron($SELECT(role = "SSViewer": "SILENTSHIFT_VIEWER_PASSWORD", 1: "SILENTSHIFT_IRIS_PASSWORD"))
        If (username = "") || ($LENGTH(password) < 12) Return $$$ERROR($$$GeneralError, "APP_INVALID: application account names and passwords of at least 12 characters are required")
        If '##class(Security.Users).Exists(username) {
            Kill properties
            Set properties("Roles") = role, properties("Password") = password
            Set properties("NameSpace") = "SILENTSHIFT", properties("Enabled") = 1, properties("ChangePassword") = 0
            Set sc = ##class(Security.Users).Create(username, .properties)
            $$$ThrowOnError(sc)
        }
    }
    Set gatewayPassword = $SYSTEM.Util.GetEnviron("SILENTSHIFT_GATEWAY_PASSWORD")
    If $LENGTH(gatewayPassword) < 12 Return $$$ERROR($$$GeneralError, "APP_INVALID: SILENTSHIFT_GATEWAY_PASSWORD must contain at least 12 characters")
    Kill properties
    Set properties("Password") = gatewayPassword, properties("Enabled") = 1, properties("ChangePassword") = 0
    Set sc = ##class(Security.Users).Modify("CSPSystem", .properties)
    $$$ThrowOnError(sc)
    Kill properties
    Set properties("Enabled") = 1, properties("AutheEnabled") = 32
    Set sc = ##class(Security.Services).Modify("%Service_WebGateway", .properties)
    $$$ThrowOnError(sc)
    // Embedded Python requires CallIn enabled. Modify only Enabled so the
    // existing authentication bitmap and resource permissions remain intact.
    Kill callInProperties
    Set callInProperties("Enabled") = 1
    Set sc = ##class(Security.Services).Modify("%Service_CallIn", .callInProperties)
    $$$ThrowOnError(sc)
    For path = "/silentshift", "/csp/silentshift" {
        Kill properties
        Set properties("NameSpace") = "SILENTSHIFT", properties("Enabled") = 1
        Set properties("AutheEnabled") = 32, properties("Resource") = "SSView"
        Set properties("Recurse") = 1, properties("UseCookies") = 0
        // Official MatchRoles format is MatchRole:TargetRole. It adds only
        // database access during this REST application's execution, never the
        // SSReview permission. The generic portal gets no added role.
        Set properties("MatchRoles") = $SELECT(path = "/silentshift": "SSViewer:SSApplication", 1: "")
        If path = "/silentshift" Set properties("DispatchClass") = "SilentShift.API"
        If ##class(Security.Applications).Exists(path) {
            Set sc = ##class(Security.Applications).Modify(path, .properties)
        } Else {
            Set sc = ##class(Security.Applications).Create(path, .properties)
        }
        $$$ThrowOnError(sc)
    }
    Return $$$OK
}
}
