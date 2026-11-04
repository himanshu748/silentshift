# SilentShift 0.2.0 release report

November 4, 2026. Verified runtime: **IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT**, official ARM64 Community **2026.3.0AI.154.0**. No build-109 validation is claimed.

## Shipped

- Source commit **d3637bb**, pushed to `main`, adds physical provider/mode/replay metadata, bounded recorded responses through the same queued operation and native tools, native regression coverage and IPM **0.2.0**.
- Open Exchange **0.2.0 published successfully**; public registry metadata and manifest both returned HTTP 200. Registry-reported artifact hash: `198fc630f90cf990481dd93f64946e34596e1018`, size 7,914,399 bytes. This reported hash is not labeled as a SHA-256 digest.
- README-backed description refresh **sent for approval**; existing contest/IPM selections, dedicated idea link and video preserved. Public page shows 0.2.0, the install command and idea association; owner-facing badge says Awaiting Review. SilentShift remains listed on contest 49.
- All **55** runtime/package files in the actual public-registry cache match the released source. Full native suite and replay passed in that new container without source mounts.

## Exact commands and observed outputs

From the repository root:

```sh
uv run --env-file .env python scripts/verify_native.py --allow-model-calls --output evidence/native/bonus-020-live-five.json
```

```text
quantity-mismatch: policy=QUARANTINE route=QUARANTINED native=True
currency-scaling: policy=QUARANTINE route=QUARANTINED native=True
approved-amendment: policy=ALLOW route=DELIVERED native=True
conflicting-references: policy=REQUEST_REVIEW route=REVIEW native=True
unsafe-agent-output: policy=QUARANTINE route=QUARANTINED native=True
```

Five actual local Ollama investigations, four native tool reads each. Sessions **1667, 1695, 1723, 1750, 1778**. Ten real provider pairs / 20 metadata bodies passed correlation checks. The deterministic baseline also solves these five frozen scenarios; no accuracy uplift is claimed.

```sh
uv run python scripts/verify_bonus_release.py --source public-registry --version 0.2.0 --container silentshift-bonus-registry-20261104 --api-port 52813 --execute
```

Actual installer command inside its fresh SILENTSHIFT namespace:

```objectscript
zpm "install PublicCommunity/silentshift 0.2.0 -synchronous"
```

The public HTTPS registry was configured read-only with empty credentials; no local application archive or source stage supplied the installation. IPM 0.10.10 reported Initialize/Reload/Validate/Compile/Configure/Activate SUCCESS. Its `synchronous` modifier emitted a deprecation warning, with no install failure. Production activation was a separate explicit Setup call.

The driver ran the full native suite:

```objectscript
set ^UnitTestRoot="/home/irisowner/silentshift-bonus/tests/"
set manager=##class(%UnitTest.Manager).%New()
set passed=manager.RunTest("","/nodelete")
```

```text
SilentShift.Test.AdapterChecks passed
SilentShift.Test.ProviderChecks passed
SilentShift.Test.ReplayChecks passed
SilentShift.Test.RuntimeChecks passed
SilentShift.Test.TraceChecks passed
(root) passed
```

All **12 methods** passed. The driver checks actual assertion/class results and rejects failed markers; the manager return value alone is insufficient evidence.

The same driver executed the real API replay:

```text
execution_mode=recorded-replay; fresh_inference=false
case_id=FF220FBE-D824-11F1-9490-630C5D6CBD59; session_id=24
visual_trace_url=http://127.0.0.1:52813/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=24
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

Recorded assistant text is preserved from an earlier live case. Tool envelopes are reconstructed, all four native tools execute, and no new inference is performed. Playback usage and upstream status remain null. [Public install / full suite / paired messages receipt](evidence/bonus-020-registry-install.json).

```sh
uv run python scripts/verify_native_provider.py --inspect-case 36DC88F3-D824-11F1-A71B-4A5ECD1428BB --require-failure --output evidence/native/bonus-020-live-failure.json
```

```text
case=36DC88F3-D824-11F1-A71B-4A5ECD1428BB provider_messages=2 passed=True
```

The preceding documented `ProviderProbe.Run("failure",...)` made one real SDK request with invalid format. Session **1807** recorded actual upstream HTTP **400**, safe error code, quarantine and zero deliveries. [Failure receipt](evidence/bonus-020-live-failure.json).

```sh
uv run pytest -q
npm --prefix web run check
npm --prefix web run build
```

```text
172 passed in 3.13s
tsc --noEmit: exit 0
vite build: exit 0, built in 639ms
```

Existing Lucide `use client` bundler warnings remain. No frontend behavior changed, so earlier connected/disconnected browser checks were retained rather than counted as new runs.

The source commit scan reported `findings: 0; files omitted: 0`. The final documentation/evidence scan reported **zero findings and three omitted binary files**, so its automated verdict is incomplete for the three JPEG screenshots. All three images were visually inspected for visible credentials before committing. The scanner covers known text patterns, not image pixels or Git history.

## Limits and failures retained

The first fresh-source attempt exposed two new test expression errors; `%Get` fixed the underscore-property assertions and the complete suite/replay then passed. A separate source container loaded successfully but paused at the disk guard; its post-restart readiness check also failed and that attempt was stopped. An unverified inspector refinement was removed; the successful first source stage and public registry source both match all 55 released runtime/package files. Local Colima disk capacity increased from 16 to 20 GiB. No retained files/volumes were deleted and no paid service was used.

**Still unverified:** the requested native screenshot with the Body metadata panel. Standard reviewer graph access works but body access was denied twice; the administrator handoff still shows Login in the available browser. No administrator password was changed and the temporary attempted permission change was reverted. Current native metadata is exported directly from persisted bodies, but that export is not a portal screenshot.

**Manual/external:** sign into an existing permitted administrator account to capture the Body panel in current live session 1723; check description/article moderation; verify personal eligibility. The video remains [a4dOcqu89EA](https://youtu.be/a4dOcqu89EA), and the earlier questionnaire receipt remains valid. Organizer bonus awards are unconfirmed.
