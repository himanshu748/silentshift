# Embedded Python bug 2: filed as https://github.com/intersystems-community/python-bugreports/issues/36

Filed text below.

---

## Title

After `ERROR #2607` on a `[ Language = python ]` method, the compiler also reports an `IndentationError` for generated code, and the rejected class stays callable

## Describe the bug

When the compiler rejects a `[ Language = python ]` method with `ERROR #2607` (here, an `Output` qualifier, which the documentation says is not allowed), it then reports a second error about generated code the user never wrote:

```
ERROR #2607: Python method 'Bad', argument 'x' Output qualifier is not allowed.
Compiling routine ZProbe.Rejected.1
Python error: expected an indented block after class definition on line 1: class Rejected():
```

Calling the rejected method later raises that same `IndentationError`, not anything pointing at the `Output` qualifier:

```
<PYTHON EXCEPTION> 246 <class 'IndentationError'>: expected an indented block after class definition on line 1 (Rejected, line 1): class Rejected():
```

A related observation: after the failed compile (`$system.OBJ.Load` returns an error status and `IsUpToDate()` is 0), the class's ObjectScript methods can still be called and return normally. The same happens after a Python syntax error in a method body. When an ObjectScript method causes the compile failure, the class is not callable (`<CLASS DOES NOT EXIST>`). I'm not sure whether the Python behaviour is intended, so I'm including it for comparison.

## iris version/image

`IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`
(AI Hub EAP community image, image id `sha256:8fa0ae85777d…`, arm64, fresh container, namespace USER)

## python version

Embedded Python 3.12.3 (`/usr/irissys/bin/irispython`)

## To Reproduce

Class under test ([`ZProbe.Rejected.cls`](https://github.com/himanshu748/silentshift/blob/0f47024b8f59d56bfcdd67c6d30b42cddce3d623/docs/launch/bonus-nov12/ep-bug-2/ZProbe.Rejected.cls)):

```objectscript
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

For comparison: [`ZProbe.RejectedSyntax.cls`](https://github.com/himanshu748/silentshift/blob/0f47024b8f59d56bfcdd67c6d30b42cddce3d623/docs/launch/bonus-nov12/ep-bug-2/ZProbe.RejectedSyntax.cls) is the same with a Python syntax error in `Bad()` (`return (`), and [`ZProbe.RejectedOS.cls`](https://github.com/himanshu748/silentshift/blob/0f47024b8f59d56bfcdd67c6d30b42cddce3d623/docs/launch/bonus-nov12/ep-bug-2/ZProbe.RejectedOS.cls) is the same with an ObjectScript error in `Bad()` (`quit (`).

In a fresh container, for each class:

```objectscript
set sc=$system.OBJ.Load("/tmp/ZProbe.Rejected.cls","ck")
write $system.Status.IsOK(sc), " ", $system.OBJ.IsUpToDate("ZProbe.Rejected"), !
write ##class(ZProbe.Rejected).Good(), !
write ##class(ZProbe.Rejected).Bad(), !
```

([`repro.sh`](https://github.com/himanshu748/silentshift/blob/0f47024b8f59d56bfcdd67c6d30b42cddce3d623/docs/launch/bonus-nov12/ep-bug-2/repro.sh) runs all three in a throwaway container.)

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

- `ERROR #2607` is the only error reported for `ZProbe.Rejected`, and a call to `Bad()` doesn't surface an `IndentationError` about generated code.
- A class whose compile failed is in the same state whichever language caused the failure (compare `ZProbe.RejectedOS`).

## Additional context

Reproduced 3 times, each in a fresh container (output in [`repro-output.txt`](https://github.com/himanshu748/silentshift/blob/0f47024b8f59d56bfcdd67c6d30b42cddce3d623/docs/launch/bonus-nov12/ep-bug-2/repro-output.txt)). Not tried on x86-64 or on 2026.2.
