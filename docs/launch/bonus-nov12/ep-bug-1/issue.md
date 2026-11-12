# Draft: Embedded Python bug 1 (NOT FILED)

Target: https://github.com/intersystems-community/python-bugreports/issues/new (template `bug_report.md`)

Duplicate check (12 Nov 2026): all 33 issues read by title. Closest is #27 (default literals are pasted into the Python source and re-read with Python escape rules). #27 concerns the value of a default when it is used. This report is about the default not being used at all when an argument is skipped. No issue mentions skipped or omitted arguments.

---

## Title

An argument skipped in an ObjectScript call (`Py(,"Z")`, `Py("X",)`) reaches a `[ Language = python ]` method as `None` instead of its declared default

## Describe the bug

A `[ Language = python ]` method with default values in its formal spec gets those defaults only when trailing arguments are left out entirely (`Py()`). When the caller skips an argument with an empty position, which is ordinary ObjectScript syntax for "use the default", the Python method receives `None` instead of the declared default. The same signature written in ObjectScript receives the default.

No error or warning is given. `None` then flows into string concatenation, SQL parameters or comparisons in the method body.

`$classmethod()` with an empty argument behaves the same way.

The documentation ("Run Embedded Python" > "In a Method in an InterSystems IRIS Class") says: "You can then call the method as you would call a method written in ObjectScript."

## iris version/image

`IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`
(AI Hub EAP community image, image id `sha256:8fa0ae85777d…`, arm64, fresh container, namespace USER)

## python version

Embedded Python 3.12.3 (`/usr/irissys/bin/irispython`)

## To Reproduce

Class (attached as `ZProbe.SkippedArg.cls`):

```objectscript
/// Repro: an argument skipped in the call does not get its declared default in a Python method.
Class ZProbe.SkippedArg
{

ClassMethod Py(a As %String = "A", b As %String = "B") As %String [ Language = python ]
{
    return repr(a) + "|" + repr(b)
}

ClassMethod OS(a As %String = "A", b As %String = "B") As %String
{
    quit "'"_a_"'|'"_b_"'"
}

ClassMethod Run()
{
    write "python       Py()     -> ", ..Py(), !
    write "python       Py(,""Z"") -> ", ..Py(, "Z"), !
    write "python       Py(""X"",) -> ", ..Py("X", ), !
    write "objectscript OS(,""Z"") -> ", ..OS(, "Z"), !
    write "objectscript OS(""X"",) -> ", ..OS("X", ), !
}

}
```

Steps:

```
docker run -d --name zprobe --init <iris image>
docker cp ZProbe.SkippedArg.cls zprobe:/tmp/
docker exec -it zprobe iris session IRIS -U USER
USER> do $system.OBJ.Load("/tmp/ZProbe.SkippedArg.cls","ck")
USER> do ##class(ZProbe.SkippedArg).Run()
```

(`repro.sh` runs the same steps in a throwaway container.)

## Actual

```
python       Py()     -> 'A'|'B'
python       Py(,"Z") -> None|'Z'
python       Py("X",) -> 'X'|None
objectscript OS(,"Z") -> 'A'|'Z'
objectscript OS("X",) -> 'X'|'B'
```

## Expected

```
python       Py(,"Z") -> 'A'|'Z'
python       Py("X",) -> 'X'|'B'
```

That is, the same values the ObjectScript method receives. If skipped arguments are intentionally unsupported for Python methods, a compile-time or call-time error (the way `ByRef`/`Output` give `ERROR #2607`) would be better than silently passing `None`.

## Additional context

Reproduced 3 times, each in a fresh container (output in `repro-output.txt`). Not tried on x86-64 or on 2026.2.
