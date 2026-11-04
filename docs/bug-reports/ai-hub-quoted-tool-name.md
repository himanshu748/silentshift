# Draft: %AI.Tool generator does not quote an ObjectScript method name containing underscores

**Status:** locally reproduced on November 4, 2026; draft only, not filed or vendor-confirmed. Potential AI Hub bug qualification is for organizers to decide. No bonus is claimed awarded.

## Environment

Official ARM64 Community AI Hub **2026.3.0AI.154.0**. Exact `$ZVERSION`: `IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`.

## Minimal reproduction

The two small classes under [repro](repro/UnderscoreTool.cls) contain no database, business-data, network or LLM operation. The underscore method declaration is deliberately quoted, which is valid ObjectScript UDL. A camel-case method is the control.

```sh
docker --context colima-silentshift cp docs/bug-reports/repro/CamelCaseTool.cls silentshift-clean-iris-1:/tmp/SS-CamelCaseTool.cls
docker --context colima-silentshift cp docs/bug-reports/repro/UnderscoreTool.cls silentshift-clean-iris-1:/tmp/SS-UnderscoreTool.cls
docker --context colima-silentshift exec -i silentshift-clean-iris-1 iris session IRIS -U SILENTSHIFT <<'IRIS'
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

## Workaround used by SilentShift

`SilentShift.AI.EvidenceTools` overrides only its application `%Invoke` dispatch, keeping native discovery and `%Encode`. It checks the exact four-name allowlist and empty argument object, then invokes `.."find_similar_precedents"()`. No vendor class is modified. The current native five-case run executes all four tools with this workaround.

A vendor fix could quote generated ObjectScript identifiers or use a safe dynamic method dispatch. This draft does not establish behavior on build 109 or newer builds.
