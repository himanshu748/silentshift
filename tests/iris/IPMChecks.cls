Include %occStatus

/// Installed-package smoke checks only: no model, ingress, delivery or reviews.
Class SilentShift.Test.IPMChecks Extends %RegisteredObject
{
ClassMethod Run(requireInstalled As %Boolean = 1) As %Status
{
    Try {
        Set sc = ##class(SilentShift.IPM).CheckTarget()
        $$$ThrowOnError(sc)
        Set root = ##class(SilentShift.IPM).AssetRoot()
        Set expected = ##class(%Library.File).NormalizeDirectory(##class(%Library.File).ManagerDirectory())_"silentshift/SILENTSHIFT/"
        If requireInstalled && (##class(%Library.File).NormalizeDirectory(root) '= expected) $$$ThrowStatus($$$ERROR($$$GeneralError, "Expected manager-directory IPM assets, not a Docker source mount"))
        Set expectedPython = ##class(%Library.File).NormalizeDirectory(root)_"python"
        If ##class(SilentShift.IPM).AssetPath("python") '= expectedPython $$$ThrowStatus($$$ERROR($$$GeneralError, "Configured asset resolver mismatch"))
        Set rejected = 0
        For invalid = "", "/etc/passwd", "../.env", "python/../.env", "python//engine.py", "./engine.py", "python\secret", "C:/secret", "a"_$Char(0)_"b", "a"_$Char(10)_"b" {
            Set failed = 0
            Try {
                Set ignored = ##class(SilentShift.IPM).AssetPath(invalid)
            } Catch error {
                Set failed = 1
            }
            If 'failed $$$ThrowStatus($$$ERROR($$$GeneralError, "Unsafe asset path accepted"))
            Set rejected = rejected+1
        }
        Set fixtureJSON = ##class(SilentShift.Bridge).FixtureJSON()
        Set fixture = ##class(%DynamicObject).%FromJSON(fixtureJSON)
        Set manifestPath = ##class(SilentShift.IPM).AssetPath("fixtures/v1/manifest.json")
        Set stream = ##class(%Stream.FileCharacter).%New()
        Set sc = stream.LinkToFile(manifestPath)
        $$$ThrowOnError(sc)
        Set manifest = ##class(%DynamicObject).%FromJSON(stream)
        If manifest.%Get("sha256") '= ##class(SilentShift.Bridge).Hash(fixtureJSON) $$$ThrowStatus($$$ERROR($$$GeneralError, "Installed frozen fixture checksum mismatch"))
        Set cases = fixture.%Get("scenarios")
        If cases.%Size() '= 5 $$$ThrowStatus($$$ERROR($$$GeneralError, "Installed fixture count mismatch"))
        For index = 0:1:cases.%Size()-1 {
            Set scenario = cases.%Get(index)
            Set message = scenario.%Get("message"), references = scenario.%Get("references")
            Set assessmentJSON = ##class(SilentShift.Bridge).Assess(message.%ToJSON(), references.%ToJSON(), fixture.%Get("clock"))
            Set proposal = scenario.%Get("test_recommendation")
            Set policy = ##class(%DynamicObject).%FromJSON(##class(SilentShift.Bridge).Policy(assessmentJSON, proposal.%ToJSON()))
            Set truth = scenario.%Get("ground_truth")
            If policy.%Get("decision") '= truth.%Get("decision") $$$ThrowStatus($$$ERROR($$$GeneralError, "Installed deterministic policy differs from frozen ground truth"))
        }
        If '..CheckOrigins() $$$ThrowStatus($$$ERROR($$$GeneralError, "Python modules came from a stale source mount or import cache"))
        Write "SILENTSHIFT_IPM_ASSET_ROOT=",root,!
        Write "SILENTSHIFT_IPM_CHECKS_OK path_rejections=",rejected," deterministic_cases=",cases.%Size()," module_origins=4 ai_runs=0",!
        Return $$$OK
    } Catch error {
        Do $SYSTEM.Status.DisplayError(error.AsStatus())
        Return $$$ERROR($$$GeneralError, "Installed IPM checks failed")
    }
}

ClassMethod CheckOrigins() As %Boolean [ Language = python, Private ]
{
    import importlib, iris
    from pathlib import Path
    for name in ('silentshift', 'silentshift.engine', 'silentshift.evaluation', 'silentshift.embeddings'):
        module = importlib.import_module(name)
        relative = 'python/' + name.replace('.', '/') + ('.py' if '.' in name else '/__init__.py')
        expected = Path(iris.cls('SilentShift.IPM').AssetPath(relative)).resolve(strict=True)
        if Path(module.__file__).resolve(strict=True) != expected:
            return False
    return True
}
}
