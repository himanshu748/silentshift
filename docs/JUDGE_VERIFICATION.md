# Judge verification — feature freeze

**Verified on November 5, 2026:** a fresh GitHub clone followed both README command blocks without provider keys. The public registry installed native **0.2.0** on **2026.3.0AI.154.0 Community, ARM64 (154U)**. Production startup, the entire native `%UnitTest` suite and two API replays passed. This closes the earlier disk-space and checkout-location gate.

Application/workbench remains **0.2.1**. No runtime or feature code changed, and no newer IRIS build was tested. Recorded replay performs no fresh inference; the separate five-case live result below remains dated evidence.

[Machine-readable receipt and native message metadata](evidence/judge-clean-clone.json) · [installation output](evidence/judge-clean-clone-install.txt) · [complete native test output](evidence/judge-clean-clone-native-tests.txt).

## Isolation and prerequisites

- Remote clone: `https://github.com/himanshu748/silentshift.git`, commit `960b6b6445f8b1f0ef7aaaa8c409e7d036b07170`. Its tracked tree remained clean before and after the run. The receipt records the README SHA-256.
- The clone was created beneath the existing Colima-shared directory, under the primary checkout's ignored `.local/judge-verified-20261105/`. No `.env`, source patch, `.local`, virtual environment or database was copied from another checkout.
- The process inherited only `HOME`, `PATH`, `TMPDIR` and locale variables. New local viewer/reviewer/gateway credentials were generated at mode `0600`; no LLM/provider API key was supplied. The checksum-verified public IPM installer was mode `0644`.
- Shared prerequisites: an already licensed, locally loaded official build-154 image, the local Web Gateway image and the existing `colima-silentshift` Docker context. This verifies a fresh source checkout and application container, not a new Mac or fresh EAP download.
- Native application container `silentshift-bonus-registry-judge-nov5` was new, had **no mounts**, and had no `SILENTSHIFT` namespace before installation. Only the separate gateway mounts generated configuration files. The preflight measured **6,822,494,208 host bytes** and **5,206,700,032 VM bytes** free; the 1.8 GiB / 3 GiB guards were unchanged.
- Both README shell blocks ran from script files with stdin closed, preventing the SSH directory check from consuming later shell instructions. Only the unused container name and port changed, as the README permits. Block 1 exited **0** at `2026-11-05T07:56:33Z`; block 2 exited **0** at `07:56:35Z`.

## Exact README commands executed

From an empty parent directory already shared with Colima:

```sh
git clone https://github.com/himanshu748/silentshift.git silentshift-judge
cd silentshift-judge
colima ssh --profile silentshift -- test -d "$PWD"
python3 - <<'PYCONFIG'
import os
from pathlib import Path
import secrets

values = {
    "IRIS_IMAGE": "silentshift-iris:2026.3.0AI.154.0",
    "SILENTSHIFT_IRIS_USERNAME": "ss-judge-reviewer",
    "SILENTSHIFT_VIEWER_USERNAME": "ss-judge-viewer",
    "SILENTSHIFT_IRIS_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_VIEWER_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_GATEWAY_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_PROVIDER_MODE": "recorded-replay",
    "SILENTSHIFT_AGENT_WAIT_SECONDS": "120",
    "SILENTSHIFT_EMBED_BASE_URL": "http://host.lima.internal:11434/v1/",
}
lines = Path(".env.example").read_text().splitlines()
content = "\n".join(
    line.split("=", 1)[0] + "=" + values[line.split("=", 1)[0]]
    if "=" in line and line.split("=", 1)[0] in values else line
    for line in lines
) + "\n"
with os.fdopen(os.open(".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as out:
    out.write(content)
print("Created private local replay configuration; no provider keys.")
PYCONFIG
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
chmod 644 .local/ipm/vendor/zpm-0.10.10.xml
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest \
  --execution-mode recorded-replay --container silentshift-bonus-registry-judge-nov5 \
  --api-port 52883 --execute
```

The driver issued literal `zpm "install silentshift"` against the public community registry, then explicitly ran `SilentShift.Setup.Install()`. The installed version was read back as **0.2.0**. It compiled the repository's test helpers and ran:

```objectscript
set ^UnitTestRoot="/home/irisowner/silentshift-bonus/tests/"
set manager=##class(%UnitTest.Manager).%New()
set passed=manager.RunTest("","/nodelete")
write "SS_UNIT_RESULT=",passed,!
```

From that same fresh clone, the second README block was:

```sh
uv run python scripts/trace_example.py \
  --api http://127.0.0.1:52883/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-registry-judge-nov5
```

## Actual results

Published console logs omit trailing whitespace only; private original logs are retained unchanged.

[Complete setup command output](evidence/judge-clean-clone-command-1.txt):

```text
Creating fresh public-registry verification container...
IPM install silentshift
Starting the installed native production (recorded-replay)...
Running the full native %UnitTest suite...
Running the no-key synthetic playback example...
```

The final JSON result reported `unit_suite_passed: true`, `replay_passed: true`, native version `0.2.0` and first replay session `24`. Its `native_five_passed` field is null because this was a recorded-replay run.

The installer and health checks reported:

```text
SS_MODULE_VERSION=0.2.0
SS_VERSION_OK
http_status: 200
production_running: true
```

The full native suite passed **five classes / 12 test methods**, not merely the test runner's return status:

```text
SilentShift.Test.AdapterChecks passed
SilentShift.Test.ProviderChecks passed
SilentShift.Test.ReplayChecks passed
SilentShift.Test.RuntimeChecks passed
SilentShift.Test.TraceChecks passed
All PASSED
SS_UNIT_RESULT=1
SS_UNIT_OK
```

The initial replay used case `69262B24-D8EE-11F1-897E-970E6F17AA2B`, session **24**. [Repeat command output](evidence/judge-clean-clone-command-2.txt):

```text
execution_mode=recorded-replay; fresh_inference=false
case_id=6BADC663-D8EE-11F1-897E-970E6F17AA2B; session_id=58
visual_trace_url=http://127.0.0.1:52883/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=58
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

Both replays passed **12/12**: five paired provider exchanges in the original case session, each of the four native tools executed once, recorded-replay provenance, null current token usage/cost, critical policy veto, `QUARANTINED` and zero delivery receipts. Full per-call metadata is retained in the receipt. Neither replay made a model or embedding request.

The actual runtime reported:

```text
IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT
```

## Other checks and boundaries

| Command | Checkout | Observed result |
| --- | --- | --- |
| `uv run pytest -q` | Fresh clone | `174 passed in 8.66s` |
| `npm --prefix web run check` | Primary checkout, unchanged source | Exit 0; TypeScript passed |
| `npm --prefix web run build` | Primary checkout, unchanged source | Exit 0; Vite built in 853 ms; existing Lucide `use client` warnings |

The browser suite was not repeated for this documentation-only update; the prior run recorded **38 passed (1.0m)**. The [earlier public-package live receipt](evidence/final-public-live.json) retains **5/5 expected final routes** on build 154U. It is not presented as a new live run or proof of model accuracy. No build 109, new package publication, public deployment or organizer award is claimed.

The new test gateway and IRIS container were stopped after verification and retained, with their logs and private credentials. The existing application was preserved. Session URLs are local to this retained instance and require restarting that pair; session IDs are not globally unique:

```sh
docker --context colima-silentshift start silentshift-bonus-registry-judge-nov5
docker --context colima-silentshift start silentshift-bonus-registry-judge-nov5-gateway
```

Use a permitted local IRIS account to view message bodies. The successful API replay does not bypass portal permissions. Existing [native Body screenshots](../README.md#native-provider-metadata) remain the screenshot evidence.

## Earlier failed attempts — retained history

The previous attempts remain documented in their original receipts; none is relabeled successful:

1. An installer copied with mode `0600` could not be read by IRIS. The README added `chmod 644` for that public installer only. [First attempt and disk-gated retry](evidence/judge-verification.json), [loader error](evidence/judge-first-client-error.txt).
2. A sibling checkout installed the package but was outside the Colima shared directory, preventing gateway bind mounts. The README added the shared-directory prerequisite and early visibility check.
3. A later shared checkout installed the package and completed setup, then stopped at the host-space guard. The user requested stopping. [Resumed-attempt receipt](evidence/judge-resumed.json).
4. The November 5 run above used the corrected unchanged recipe after more host space became available. No further cleanup or lower safety floor was needed.

The separate November 4 retained-instance replay passed **12/12**, session **59**; [its evidence](evidence/freeze-build154-replay.json) remains independent of this clean-clone proof.

OEX and Developer Community were not edited. [Prepared OEX copy and user-only steps](OPEN_EXCHANGE_COPY.md); [exact AI Hub bug filing text and URL](bug-reports/ai-hub-quoted-tool-name.md). Organizer awards and the dedicated OEX idea association remain unconfirmed.
