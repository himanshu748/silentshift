Include %occStatus

Class SilentShift.PEX.Support Extends %RegisteredObject
{
/// Called only after an operation has committed its existing routing decision.
ClassMethod Request(id As %String) As SilentShift.PEX.ExportRequest
{
    Set body = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Store).CaseJSON(id))
    Set hashes = [], references = body.%Get("references")
    For field = "message", "assessment", "policy" {
        Set value = body.%Get(field)
        If $ISOBJECT(value) Set hashValues(##class(SilentShift.Bridge).Hash(##class(SilentShift.Bridge).Canonical(value.%ToJSON()))) = 1
    }
    If $ISOBJECT(references) Set hashValues(##class(SilentShift.Bridge).Hash(##class(SilentShift.Bridge).Canonical(references.%ToJSON()))) = 1
    Set hash = ""
    For {
        Set hash = $ORDER(hashValues(hash))
        Quit:hash=""
        Do hashes.%Push(hash)
    }
    Set mode = $SYSTEM.Util.GetEnviron("SILENTSHIFT_PROVIDER_MODE")
    If mode '= "recorded-replay" Set mode = "live"
    Set payload = {"case_id": (id), "decision": (body.%Get("routing")), "evidence_hashes": (hashes), "execution_mode": (mode), "synthetic": (body.%Get("synthetic"))}
    Do payload.%Set("synthetic",body.%Get("synthetic"),"boolean")
    Set request = ##class(SilentShift.PEX.ExportRequest).%New()
    Set request.CaseId = id, request.Decision = body.%Get("routing"), request.PayloadJSON = payload.%ToJSON()
    Return request
}

/// JDK/PEX are supplied by the licensed local image, not bundled in IPM.
ClassMethod Configure() As %Status
{
    Try {
        Set root = ##class(SilentShift.IPM).AssetRoot(), output = $SYSTEM.Util.ManagerDirectory()_"silentshift-pex/"
        Set log = output_"build.log"
        If '##class(%File).CreateDirectoryChain(output) Return $$$ERROR($$$GeneralError, "Cannot create Java build directory")
        Set rc = $ZF(-100, "/STDOUT="""_log_""" /STDERR="""_log_"""", "/bin/sh", root_"/java/build.sh", root_"/java", output)
        If rc '= 0 Return $$$ERROR($$$GeneralError, "Java PEX build failed; inspect manager silentshift-pex/build.log")
        Set sdk = $SYSTEM.Util.InstallDirectory()_"dev/java/lib/1.8/"
        Set rs = ##class(%File).FileSetFunc(sdk, "intersystems-pex-*-shaded.jar"), pex = ""
        If rs.%Next() Set pex = rs.Name
        If pex = "" Return $$$ERROR($$$GeneralError, "IRIS PEX SDK not found")
        Do ..Default("%gatewayExtraClasspaths", pex_"|"_output_"silentshift-pex.jar")
        Do ..Default("%remoteSettings", "Directory="_output_"receipts")
        Return $$$OK
    } Catch error { Return $$$ERROR($$$GeneralError, "Java PEX setup failed; inspect local setup diagnostics") }
}

ClassMethod Default(setting As %String, value As %String)
{
    Set row = ##class(Ens.Config.DefaultSettings).%OpenId("SilentShift.Production||ReceiptExporter||EnsLib.PEX.BusinessOperation||"_setting)
    If '$ISOBJECT(row) {
        Set row = ##class(Ens.Config.DefaultSettings).%New()
        Set row.ProductionName = "SilentShift.Production", row.ItemName = "ReceiptExporter", row.HostClassName = "EnsLib.PEX.BusinessOperation", row.SettingName = setting
    }
    Set row.SettingValue = value, row.Deployable = 1
    Set sc = row.%Save()
    $$$ThrowOnError(sc)
}
}
