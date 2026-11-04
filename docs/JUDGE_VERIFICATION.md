# Judge verification — feature freeze

**Status: BLOCKED after two attempts. No fresh-clone install, native suite or replay pass is claimed.** Application/workbench **0.2.1**; published native IPM **0.2.0**; declared runtime **2026.3.0AI.154.0 Community, ARM64 (154U)**. No newer build was tested.

The first remote clone found a real setup-instruction gap: Docker copied the newly downloaded public IPM installer with mode `0600` and UID 501, preventing IRIS from opening it. The README now includes `chmod 644` for that checksum-verified public file only. The second remote clone confirmed installer mode `0644` and local credentials mode `0600`, then stopped at the host-storage preflight. The corrected installer has **not** yet been loaded by a successful fresh run. We stopped rather than making a third attempt.

## What was isolated

- Two new clones from `https://github.com/himanshu748/silentshift.git`, with no copied `.env`, `.local`, virtual environment, source patch or database. Both tracked trees remained clean.
- Attempt 1 checked out `d116d735f577707a7b89b7c1cdc9fa1a819960b4`. Attempt 2 checked out `37480de32f4de8890c486a6974ea1e1ea7d4c56c`, including the installer-permission instruction. Both README hashes are recorded in the [machine-readable receipt](evidence/judge-verification.json).
- Commands ran with only host `HOME`, `PATH`, `TMPDIR` and locale environment variables. Local viewer/reviewer/gateway credentials were generated separately in each clone and never printed or committed. No LLM/provider API key was supplied. No model or embedding call was made.
- Shared prerequisites were explicitly declared: the preloaded licensed build-154 image, public Web Gateway image and existing Colima VM/context. This was a fresh source checkout and fresh application-container attempt, not a new Mac or a new EAP download.
- Attempt 1 created a container without mounts and observed `$ZVERSION` build 154U. It was stopped and retained after failure. Attempt 2 created no container because preflight failed.

## Exact README commands

Attempt 1 ran both setup commands through the install driver exactly as the README at its commit specified, with default name `silentshift-bonus-registry-judge` and port `52843`. It did not contain the newly required `chmod` line. The repeat-replay command was never reached.

For attempt 2, the README explicitly instructs using a new name and free port for another run. Only those two identifiers changed: `silentshift-bonus-registry-judge-retry`, port `52853`. The following block was extracted from the updated README and executed in a new empty parent directory:

```sh
git clone https://github.com/himanshu748/silentshift.git silentshift-judge
cd silentshift-judge
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
  --execution-mode recorded-replay --container silentshift-bonus-registry-judge-retry \
  --api-port 52853 --execute
```

The README's next command is retained here for the eventual successful run. **It was not reached in either attempt:**

```sh
uv run python scripts/trace_example.py \
  --api http://127.0.0.1:52853/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-registry-judge-retry
```

## Actual output

Attempt 1: [complete command output](evidence/judge-first-output.txt) and [exact IPM loader error](evidence/judge-first-client-error.txt).

```text
Creating fresh public-registry verification container...
Verification stopped: Missing SS_CLIENT_OK; inspect private 10-client.log
```

The loader reported:

```text
Unable to open file. Skipping file: /home/irisowner/silentshift-bonus/zpm.xml
Detected 1 errors during load.
ERROR #5005: Cannot open file '/home/irisowner/silentshift-bonus/zpm.xml'
```

The first container's actual version was:

```text
SS_RUNTIME=IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT
SS_PRISTINE_OK
```

Attempt 2: [complete command output](evidence/judge-retry-output.txt).

```text
Created private local replay configuration; no provider keys.
Using CPython 3.12.11
Creating virtual environment at: .venv
Installed 7 packages in 18ms
Verification stopped: Insufficient free space; retain existing files/volumes and arrange space before retrying
```

The complete output also records the official IPM 0.10.10 download: **1,593,780 bytes**, SHA-256 `daa2adabd66b488f57187d29712e54b0c25bbe000794fbf2a35a882c458b788a`. A post-attempt read showed **1,745,149,952 host bytes free**, below the **1,932,735,283-byte** floor. Docker had **6,904,804 KiB** available. The remaining blocker is host storage, not the VM's available blocks. These are post-attempt readings, not invented measurements from inside the failed preflight.

## What did pass in this freeze pass

The separately retained public-registry instance was restarted and read back as native IPM **0.2.0** on **154U**. It passed a new judge replay; this is **not** a clean-clone result:

```sh
uv run python scripts/trace_example.py --api http://127.0.0.1:52823/silentshift/api --context colima-silentshift --container silentshift-bonus-registry-final-replay-20261104 --output .local/freeze-build154-replay.json
```

```text
execution_mode=recorded-replay; fresh_inference=false
case_id=EE70D85C-D87A-11F1-AFA0-EE4D8B64EE4D; session_id=59
visual_trace_url=http://127.0.0.1:52823/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=59
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

[Full replay metadata](evidence/freeze-build154-replay.json). That retained instance was stopped afterward. Its local URL requires starting that specific instance; session IDs are scoped to an IRIS instance, not globally unique.

Repository checks ran from the primary checkout; no application source changed:

| Command | Result |
| --- | --- |
| `uv run pytest -q` | `174 passed in 4.87s` |
| `npm --prefix web run check` | Exit 0; TypeScript passed |
| `npm --prefix web run build` | Exit 0; production assets built; existing Lucide `use client` bundling warnings |
| `npm --prefix web run test:e2e` | `38 passed (1.0m)`; desktop/mobile landing and disconnected states, keyboard and reduced motion |
| Documentation consistency / `git diff --check` | Version, video, article URLs, local links and whitespace passed |

The five-class / 12-method native suite and five-case live run have [earlier public-package evidence](evidence/final-public-live.json). They were **not rerun successfully from these fresh clones**, and their older results are not substituted for this blocked gate.

## Resume after freeing host space

Make at least another **1 GiB** available to leave room beyond the minimum floor. Preserve existing evidence, models and containers. On an explicit resumed attempt, repeat the README from another fresh clone with an unused container name/port; require the public install, production startup, full native suite and replay to pass. Save their actual output and session URL here before changing this status to Verified. No third test attempt was made in this pass.

The user approved removing three named stopped test containers without volumes. Rebuildable caches were also cleared under the separate cache-cleanup instruction. An active Chromium cache was retained; a protected dotslash cache could not be fully removed and was left after two permission failures. No credentials, models, project source or active app were deleted.

OEX and Developer Community were not edited. [Prepared OEX copy and user-only steps](OPEN_EXCHANGE_COPY.md); [bug filing text and URL](bug-reports/ai-hub-quoted-tool-name.md).
