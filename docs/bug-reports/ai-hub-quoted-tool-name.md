# %AI.Tool generates an unquoted call for a valid quoted underscore method (154U)

**Filing URL:** https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/new

The [official contest criteria](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows) link this dedicated AI Hub bug tracker. Use this document's heading as the issue title and copy from **Environment** through **Workaround** as the body.

**Status:** reproduced again on November 4, 2026 at 18:07:42 UTC in the development `USER` namespace; no production classes changed. [Exact compiler transcript](evidence/quoted-tool-build154.txt). Draft only: not filed, vendor-confirmed or organizer-confirmed. No bonus is claimed awarded.

## Environment

Official ARM64 Community AI Hub **2026.3.0AI.154.0**. Exact `$ZVERSION`: `IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`.

## Minimal reproduction

Save these as `CamelCaseTool.cls` and `UnderscoreTool.cls` in a development environment running this build. Neither class uses a database, network, model or credential. The quoted method declaration is intentional; it is valid ObjectScript UDL.

```objectscript
Class SilentShift.Repro.CamelCaseTool Extends %AI.Tool
{
Method FindSimilarPrecedents() As %String
{
    Return "ok"
}
}
```

```objectscript
Class SilentShift.Repro.UnderscoreTool Extends %AI.Tool
{
Method "find_similar_precedents"() As %String
{
    Return "ok"
}
}
```

In an IRIS terminal, in a development namespace, load the two files (adjust their absolute paths):

```objectscript
write $zversion,!
set sc=$system.OBJ.Load("/tmp/SS-CamelCaseTool.cls","ck")
write "SS_CAMEL_OK=",$system.Status.IsOK(sc),!
set sc=$system.OBJ.Load("/tmp/SS-UnderscoreTool.cls","ck")
write "SS_UNDERSCORE_OK=",$system.Status.IsOK(sc),!
do $system.Status.DisplayError(sc)
```

The exact commands used from the SilentShift checkout were:

```sh
docker --context colima-silentshift cp docs/bug-reports/repro/CamelCaseTool.cls silentshift-clean-iris-1:/tmp/SS-CamelCaseTool.cls
docker --context colima-silentshift cp docs/bug-reports/repro/UnderscoreTool.cls silentshift-clean-iris-1:/tmp/SS-UnderscoreTool.cls
docker --context colima-silentshift exec -i silentshift-clean-iris-1 iris session IRIS -U USER <<'IRIS'
write "SS_RUNTIME=",$zversion,!
set sc=$system.OBJ.Load("/tmp/SS-CamelCaseTool.cls","ck")
write "SS_CAMEL_OK=",$system.Status.IsOK(sc),!
set sc=$system.OBJ.Load("/tmp/SS-UnderscoreTool.cls","ck")
write "SS_UNDERSCORE_OK=",$system.Status.IsOK(sc),!
do $system.Status.DisplayError(sc)
halt
IRIS
```

Use a disposable development namespace and adapt the container name. The second load is expected to fail while this bug exists; the reproducer is not part of the passing application unit suite.

## Expected

Both valid classes compile. The inherited native `%Invoke` dispatcher calls the quoted method while preserving the tool name `find_similar_precedents`.

## Actual

The control compiled (`SS_CAMEL_OK=1`). The quoted underscore declaration parsed, but compilation of the generated `%Invoke` failed (`SS_UNDERSCORE_OK=0`):

```text
MPP5376 : Method or Property 'find' does not exist in this class.
TEXT: "find_similar_precedents": ..find_similar_precedents(),
%Invoke+3 #1056: Missing subscript
```

The generated call is unquoted. This is distinct from the first diagnostic attempt, whose unquoted UDL declaration was invalid application code and correctly rejected before generation; that mistake is not reported as a vendor bug.

## Workaround

`SilentShift.AI.EvidenceTools` overrides only its application `%Invoke` dispatch, keeping native discovery and `%Encode`. It checks the exact four-name allowlist and empty argument object, then invokes `.."find_similar_precedents"()`. No vendor class is modified. The current native five-case run executes all four tools with this workaround.

A vendor fix could quote generated ObjectScript identifiers or use a safe dynamic method dispatch. This draft does not establish behavior on build 109 or newer builds.
