# Draft investigation: historical signal 11 during native AI Hub tool callbacks

**Status:** observed historical crash, not an isolated/reproducible vendor defect. Do not present this as an earned AI Hub or Embedded Python bug bonus. Draft only; nothing was filed.

## Environment and observed behavior

Official ARM64 Community **2026.3.0AI.154.0 (154U)**. The retained original IRIS message log has **five background-job signal-11 entries** on November 2. The [sanitized log extract](../evidence/historical-callback-crashes.json) preserves timestamps and process IDs. Full logs remain private.

During early native `%AI.Agent.Chat` investigations, tool callbacks called `SilentShift.Store.AddEvent`, which called Embedded Python for JSON canonicalization and UTC time. The worker failed inside Chat/callback activity. A supported callback should return a value or a managed error without terminating the worker; that is the behavior to investigate.

## Reproduction status

A standalone minimal failing class has **not** been established. The original application snapshot is commit `7021610`; `Store.AddEvent` calls `Bridge.Canonical` and `Bridge.Now` there. Commit `b836d2d` keeps callback-side serialization/timestamps in ObjectScript. The diff provides an application-scale starting point:

```sh
git diff 7021610 b836d2d -- src/SilentShift/Store.cls src/SilentShift/AI/Investigator.cls
```

Replaying that historical snapshot requires an isolated licensed build-154 environment, its original model settings and an explicitly authorized local LLM call. The current application was not reverted or deliberately crashed. A reviewer should first reduce the nested callback path into a standalone harness and correlate native/Python stack traces before filing a reproducible vendor issue.

## Workaround and uncertainty

The application moved JSON serialization and timestamp creation inside the native callback to ObjectScript. Embedded Python still performs deterministic assessment and policy outside that callback. Subsequent full native runs passed. This is correlation with an effective application workaround, not proof that nesting alone caused the crash.

Removing optional `session.GetStats()` did not resolve the historical problem. Do not file a separate statistics bug or classify this automatically as an Embedded Python defect. Neither stack trace attribution nor vendor confirmation is available. No build-109 result is claimed.
