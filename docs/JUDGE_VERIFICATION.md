# Judge verification

## Current-main repeat — isolated source, November 8, 2026 (UTC)

**The remaining local verification gap is closed.** A fresh GitHub clone at **`35d29e0913ea27f4c56dfed214a402418984e5f0`** was loaded into a new **2026.3.0AI.154.0 Community / 154U ARM64** container, using the already loaded official image. The namespace was pristine and the application container had no source mounts. The tracked clone remained clean. Only documentation/evidence commits followed this tested snapshot.

This run used **IPM `load` of current source**, including the CSV class and parser. It is separate from the earlier successful public `zpm "install silentshift"` gate below. The source manifest still declares the published version, but **no new native package was published**. Public IPM remains **0.2.0**; app/workbench remains **0.2.1**. No provider key, paid service or new IRIS download was used.

| Check | Observed result | Evidence |
| --- | --- | --- |
| Fresh source load and production startup | Passed; **45 declared classes** | [Exact command](evidence/source-isolated-nov8-command.sh), [output](evidence/source-isolated-nov8-output.txt), [load transcript](evidence/source-isolated-nov8-load.txt) |
| Full native `%UnitTest` | **5 classes / 12 methods passed** | [Complete output](evidence/source-isolated-nov8-native-tests.txt) |
| Fresh live native scenarios | **5/5 final routes passed**; all agents returned with all four evidence tools | [Source, provenance and complete native receipt](evidence/source-isolated-nov8.json) |
| Fresh CSV workbench import | **32 browser checks passed**, with new held and delivered cases | [CSV receipt](evidence/csv-isolated-nov8.json), [exact command](evidence/csv-isolated-nov8-command.sh), [output](evidence/csv-isolated-nov8-output.txt) |
| Fresh-clone Python | **207 passed in 11.30s** | [Output](evidence/source-isolated-nov8-pytest.txt) |
| TypeScript and production build | Both passed | [Types](evidence/source-isolated-nov8-types.txt), [build](evidence/source-isolated-nov8-build.txt) |
| Landing/disconnected browser checks | **38 passed** | [Output](evidence/source-isolated-nov8-browser.txt) |
| Connected browser checks | **16 passed**, desktop and mobile; read-only native data | [Receipt](evidence/source-isolated-nov8-connected.json), [output](evidence/source-isolated-nov8-connected.txt) |

The complete source/native command took **359.323 seconds**, including installation, one separate local amendment embedding, an SDK diagnostic and the five-case run. CSV verification took **119.966 seconds**; connected checks took **55.396 seconds**. The [local-check receipt](evidence/source-isolated-nov8-local-checks.json) retains each command's measured wall time and exit code. All these commands exited successfully.

Final routing matched the frozen labels **5/5**; raw model recommendations matched **4/5**. The model proposed quarantine for conflicting references; policy correctly selected review. These synthetic cases establish integration behavior, not general model accuracy or an AI advantage over the deterministic baseline. The SDK diagnostic and amendment indexing are excluded from the five-case score.

Native scenario sessions were **30, 58, 86, 113, 141**. The CSV mismatch was **QUARANTINED**, session **169**, with **0 deliveries**; its matching line was **DELIVERED**, session **197**, with **1 simulator receipt**. Both CSV agents returned and read every tool. The UI checks also exercised bounded file rejection, native invalid-quantity rejection, explicit source approval, viewer restrictions, interrupted-request recovery, repeat import without new dispatch, case navigation, keyboard input, compact layouts and reduced motion. [First import](evidence/csv-isolated-nov8-first.json) · [repeat receipt](evidence/csv-isolated-nov8-repeat.json) · [desktop capture](assets/csv-isolated-nov8-desktop.png) · [mobile capture](assets/csv-isolated-nov8-mobile.png).

The earlier reload failure below is retained unchanged. It was bypassed by testing in a new instance without the untracked diagnostic class; that class was not deleted, and native code/policy/AI behavior were not changed. The only harness change allows an explicitly local API port, with [remote endpoints rejected before credential use](evidence/csv-isolated-nov8-guard.json).

**Hosted CI is blocked separately:** GitHub reports that the job did not start because the account is locked for billing. [Exact annotation](evidence/hosted-ci-nov8.json). The passing checks above are local; no hosted CI pass or billing repair is claimed.

The isolated test containers are retained for inspection. Restart only this pair to inspect these sessions:

```sh
docker --context colima-silentshift start silentshift-bonus-load-main-nov8
docker --context colima-silentshift start silentshift-bonus-load-main-nov8-gateway
```

Its API and trace portal use port **52913**. Opening message bodies requires a permitted account in that instance. CSV remains additive to the README's keyless replay and the JSON-ready-file adapter walkthrough. All inputs remain synthetic; delivery remains the IRIS simulator. No newer build, hosted demo, external ERP integration, package publication or bonus award is claimed.

## Earlier current-main repeat — November 8, 2026 (UTC)

**Public-package gate: passed. Current-main CSV repeat: stopped at failed source-reload preparation.** These are separate results; the released native package does not contain the source-only CSV feature.

The fresh GitHub clone's HEAD was **`df591420c06ed081623f6178804359ceb1686964`**. It includes the CSV runtime changes and the UI finish. The tracked clone stayed clean. Subsequent commits in this verification pass add documentation and evidence; this hash identifies the executed source snapshot, not those later receipts.

Installation now lives in [INSTALL.md](../INSTALL.md#optional-check-without-a-model), linked from the README. The two historical README blocks were repeated with only a new container name and port. The already loaded official **2026.3.0AI.154.0 Community / 154U ARM64** image was used; no IRIS image was downloaded and no provider key was supplied.

| Executed check | Observed result | Elapsed |
| --- | --- | ---: |
| Fresh clone, literal `zpm "install silentshift"`, production startup and full native suite | Public native **0.2.0**; **5 classes / 12 methods passed**; initial replay **12/12** | 119.348 s for the complete first block |
| Second API replay | **12/12 passed** | 1.640 s |
| Fresh-clone `uv run pytest -q` | **207 passed in 14.21s** | 16.664 s wall time |

All blocks exited successfully. Replay sessions **24** and **58** each ended **QUARANTINED**, with **0 deliveries** and no fresh inference. [Machine-readable receipt](evidence/judge-current-nov8.json), [installation output](evidence/judge-current-nov8-install.txt), [complete native tests](evidence/judge-current-nov8-native-tests.txt) and [authenticated health](evidence/judge-current-nov8-health.json) preserve the observations.

Exact commands and outputs: [installation block](evidence/judge-current-nov8-command-1.sh) / [output](evidence/judge-current-nov8-command-1.txt), [repeat block](evidence/judge-current-nov8-command-2.sh) / [output](evidence/judge-current-nov8-command-2.txt), [Python block](evidence/judge-current-nov8-command-3.sh) / [output](evidence/judge-current-nov8-command-3.txt). Public logs replace the checkout path with `<fresh-clone>` and strip trailing whitespace. Private originals are retained. The fresh public-package containers were stopped and retained after testing.

### CSV and UI evidence; stopped repeat

Earlier in this same turn, before the fresh-clone gate, the refined CSV workbench completed **32 browser checks** against the retained local production. The synthetic mismatch was held and the matching line delivered once; invalid quantity input was rejected by the native server. [UI receipt](evidence/csv-ui-design-nov8.json), [successful import observations](evidence/csv-ui-nov8-success.json), [bounded-rejection observations](evidence/csv-ui-nov8-rejection.json). These observations are explicitly dated and ordered; they are not a post-gate CSV rerun.

After the fresh-clone gate, source/Python/fixture bytes were compared with that clone, then the documented source bootstrap was attempted in the retained local instance. It exited **1**: `CompilePackage("SilentShift")` also compiled the retained, untracked diagnostic class `SilentShift.Repro.UnderscoreTool`. Its generated `find_similar_precedents` invocation produced **3 compiler errors**, including `MPP5376`. This demonstrates a failed reload in that instance; it does not establish a defect in CSV import or a clean-source-install failure.

**Stopped without retry or native-code changes.** The post-gate CSV success/rejection checks and a fresh full live five-case run were not executed. The previously running production was restarted successfully after the failed reload. [Failure receipt and source hashes](evidence/csv-current-nov8.json), [executed command](evidence/csv-current-nov8-command.sh), [output](evidence/csv-current-nov8-bootstrap.txt), [compiler excerpt](evidence/csv-current-nov8-compiler.txt).

CSV is additive: it does not change the documented keyless replay walkthrough or the JSON-ready-file adapter path in [PARTNER_INBOX.md](PARTNER_INBOX.md). It requires the current source installation and explicit importer permission; public native IPM remains unchanged. No newer build, hosted demo, package publication or organizer award is claimed.

## Current-main repeat — November 5, 09:04–09:09 UTC

A second fresh GitHub clone, at **e8e1e60fded08d688c263bc9485fc7419c10f15b**, passed both README blocks with no provider keys. Only the unused container name (`silentshift-bonus-registry-main-nov5`) and port (`52893`) changed. The tracked clone remained clean. Within the historical `960b6b6` → `e8e1e60` interval, changes were documentation/evidence only. This statement does not cover the later CSV runtime and workbench changes.

**Public native IPM 0.2.0, production startup, all five native test classes / 12 methods, and both 12/12 replays passed on 2026.3.0AI.154.0 / 154U ARM64.** Fresh-clone `uv run pytest -q` returned **174 passed in 15.09s**. No fresh model/embedding call, five-case live rerun or newer build test is claimed.

[Machine-readable receipt and both native traces](evidence/judge-main-clean-clone.json) · [full native test output](evidence/judge-main-native-tests.txt) · [registry installation output](evidence/judge-main-install.txt).

The exact executed shell blocks are preserved as [block 1](evidence/judge-main-command-1.sh) and [block 2](evidence/judge-main-command-2.sh), with [first output](evidence/judge-main-command-1.txt) and [repeat output](evidence/judge-main-command-2.txt). Public logs replace the private checkout path with `<fresh-clone>` and strip trailing whitespace; original logs remain local. Both commands exited **0**. The repeated API journey printed:

```text
execution_mode=recorded-replay; fresh_inference=false
case_id=A56C930B-D8F8-11F1-9B50-2D0E2BB6B2AA; session_id=58
visual_trace_url=http://127.0.0.1:52893/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=58
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

The initial case was `A2778A37-D8F8-11F1-9B50-2D0E2BB6B2AA`, session **24**. These session numbers belong to this new isolated instance, not the earlier instance with the same numbers. Host/VM preflight free space was 7,706,902,528 / 4,274,151,424 bytes; the existing safety floors were unchanged. The new test containers were stopped and retained after verification; the working app was preserved. To inspect these particular traces, restart only this pair:

```sh
docker --context colima-silentshift start silentshift-bonus-registry-main-nov5
docker --context colima-silentshift start silentshift-bonus-registry-main-nov5-gateway
```

## Earlier clean-clone run — 960b6b6

**Verified on November 5, 2026:** a fresh GitHub clone followed both README command blocks without provider keys. The public registry installed native **0.2.0** on **2026.3.0AI.154.0 Community, ARM64 (154U)**. Production startup, the entire native `%UnitTest` suite and two API replays passed. This closes the earlier disk-space and checkout-location gate.

At this earlier snapshot, application/workbench was **0.2.1**. No runtime or feature code changed within that historical documentation interval, and no newer IRIS build was tested. Recorded replay performs no fresh inference; the separate five-case live result below remains dated evidence.

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

No external edit was part of the test run itself. The user subsequently authorized filing the [AI Hub bug as #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) and submitting the [OEX description](OPEN_EXCHANGE_COPY.md); both actions were verified on November 5. [OEX submission receipt](evidence/oex-submitted-nov5.json). Developer Community was unchanged. Organizer awards and public visibility of the dedicated OEX idea association remain unconfirmed.
