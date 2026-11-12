# Draft: Embedded Python bug 2 (NOT FILED)

Target: https://github.com/intersystems-community/python-bugreports/issues/new (template `bug_report.md`)

Duplicate check (12 Nov 2026): searched titles for 2605, 2607, compile, compilation, compiler. Hits (#5, #6, #26, #27) are unrelated. #27 mentions `ERROR #2605` only as a side effect of default literals; it doesn't cover what happens to the class after the failure.

Severity note for us: lower impact than bug 1. A triager could call it intended ("partial compile"), but the ObjectScript control shows that IRIS normally does not leave a failed class runnable.

---

## Title

A class rejected by the compiler because of a `[ Language = python ]` method is still installed: its other methods run, while the same failure in ObjectScript leaves `<CLASS DOES NOT EXIST>`

## Describe the bug

When a class fails to compile because of one of its Python methods, `$system.OBJ.Load(..., "ck")` returns an error status and `IsUpToDate()` is 0, but the class is still installed. Its ObjectScript methods can be called and return normally. The broken Python method can also be called and raises a Python exception at run time.

A class that fails to compile because of an ObjectScript method is not runnable: every call raises `<CLASS DOES NOT EXIST>`.

Two triggers show this:

1. A documented compile error: `ByRef`/`Output` on a Python method (`ERROR #2607`). The compiler also prints a second, misleading error, `Python error: expected an indented block after class definition on line 1: class Rejected():`, because the generated Python class is left empty. That text is then what the caller sees when the rejected method is called.
2. A Python syntax error in the method body.

So deployment scripts and CI that check only for `<CLASS DOES NOT EXIST>`, or that call a smoke-test method, see a "working" class after a failed compile.

## iris version/image

`IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`
(AI Hub EAP community image, image id `sha256:8fa0ae85777d…`, arm64, fresh container, namespace USER)

## python version

Embedded Python 3.12.3 (`/usr/irissys/bin/irispython`)

## To Reproduce

Three classes (attached). The one under test:

```objectscript
/// Repro: the compiler rejects this class (ERROR #2607), but the class is still installed and runnable.
Class ZProbe.Rejected
{

ClassMethod Good() As %String
{
    quit "Good() ran"
}

ClassMethod Bad(Output x As %String) As %String [ Language = python ]
{
    return "Bad() ran"
}

}
```

`ZProbe.RejectedSyntax` is the same with `Bad()` body `return (` (Python syntax error). `ZProbe.RejectedOS` is the control: the same shape with an ObjectScript `Bad()` body `quit (`.

For each class, in a fresh container:

```objectscript
set sc=$system.OBJ.Load("/tmp/ZProbe.Rejected.cls","ck")
write $system.Status.IsOK(sc), " ", $system.OBJ.IsUpToDate("ZProbe.Rejected"), !
write ##class(ZProbe.Rejected).Good(), !
write ##class(ZProbe.Rejected).Bad(), !
```

(`repro.sh` runs all three in a throwaway container.)

## Actual

```
ERROR #2607: Python method 'Bad', argument 'x' Output qualifier is not allowed.
Python error: expected an indented block after class definition on line 1: class Rejected():
== ZProbe.Rejected: compile ok=0, IsUpToDate=0
   Good() -> Good() ran
   Bad() -> <PYTHON EXCEPTION> 246 <class 'IndentationError'>: expected an indented block after class definition on line 1 (Rejected, line 1): class Rejected():

Python error: '(' was never closed: return (
== ZProbe.RejectedSyntax: compile ok=0, IsUpToDate=0
   Good() -> Good() ran
   Bad() -> <PYTHON EXCEPTION> 246 <class 'SyntaxError'>: '(' was never closed (RejectedSyntax, line 3): return (

ERROR: ZProbe.RejectedOS.cls(Bad+2) #1054: Invalid expression : '}' ...
== ZProbe.RejectedOS: compile ok=0, IsUpToDate=0
   Good() -> <CLASS DOES NOT EXIST> 150  ZProbe.RejectedOS
   Bad() -> <CLASS DOES NOT EXIST> 150  ZProbe.RejectedOS
```

## Expected

A class whose compile failed behaves the same whichever language caused the failure: it is not installed (`<CLASS DOES NOT EXIST>`, as with `ZProbe.RejectedOS`). Also, `ERROR #2607` should be the only error reported, not followed by an `IndentationError` about generated code the user never wrote.

## Additional context

Reproduced 3 times, each in a fresh container (output in `repro-output.txt`). Not tried on x86-64 or on 2026.2.
