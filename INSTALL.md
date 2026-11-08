# Install SilentShift locally

This guide starts the IRIS backend and the browser workbench. Follow steps 1–7 in order. You do not need a cloud account or a paid model API key.

The tested native environment is **macOS on Apple Silicon, IRIS Community AI Hub 2026.3.0AI.154.0 (154U)**. Other builds and platforms have not been qualified. The separate app/workbench is **0.2.1**. Public native IPM and OEX release are **0.3.0**. The native package includes the CSV backend/parser; it does not install the React web bundle. [Fresh public installation](docs/evidence/ship-030-registry.json) · [separate live/source/browser gate](docs/evidence/candidate-030.json).

## Before you start

Have Git, Python 3.11 or newer, uv, Node.js 22.12 or newer, npm, Colima, Docker CLI, Compose 2 and Ollama installed. You also need the official ARM64 Community AI Hub **build 154** Docker archive from InterSystems. It is separately licensed and cannot be included in this repository. If your InterSystems download account no longer offers that build, stop here and ask InterSystems for access; substituting another build is not a tested installation.

You will download the local Qwen model (about 2.5 GB) and a Web Gateway image. Allow disk space for these, the IRIS archive, its extracted image and database. Ports **52773** and **5173** must be free. This is a local evaluation using synthetic orders and an IRIS destination simulator.

## 1. Get the source and start Docker

```sh
git clone https://github.com/himanshu748/silentshift.git
cd silentshift
colima start --profile silentshift
export DOCKER_CONTEXT=colima-silentshift
colima ssh --profile silentshift -- test -d "$PWD"
```

The last command should finish without an error. If it fails, move the checkout into a folder shared with your Colima profile, then try that check again. IRIS needs to read files from the checkout. Run the remaining commands from this directory.

## 2. Load the IRIS archive

Replace the archive path and the loaded-image placeholder below with your own values. `docker load` prints the image name to use in the next command.

```sh
docker load -i "/absolute/path/to/official-build154-docker.tar.gz"
docker tag "<image name printed by docker load>" silentshift-iris:2026.3.0AI.154.0
docker pull containers.intersystems.com/intersystems/webgateway:2026.1
```

The tag is a local name for the vendor image you loaded; it does not download IRIS.

## 3. Set your local passwords

```sh
cp -n .env.example .env
chmod 600 .env
```

Open `.env` in your editor. Set these entries and leave the other defaults alone:

| Entry | Value |
| --- | --- |
| `IRIS_IMAGE` | `silentshift-iris:2026.3.0AI.154.0` |
| `SILENTSHIFT_IRIS_PASSWORD` | A new password for the local reviewer account |
| `SILENTSHIFT_VIEWER_PASSWORD` | A different new password for the viewer account |
| `SILENTSHIFT_GATEWAY_PASSWORD` | A third new password for the gateway |
| `SILENTSHIFT_AGENT_WAIT_SECONDS` | `120` |
| `SILENTSHIFT_EMBED_BASE_URL` | `http://host.lima.internal:11434/v1/` |

Use three different passwords of at least 12 characters. Letters and digits avoid quoting problems in this configuration file. The default account names are `ss-reviewer` and `ss-viewer`. These are local application accounts; they are separate from your InterSystems website login. If you are reusing an existing installation, keep its existing account names and passwords.

Keep `.env` private. Never commit it or paste its contents into a support request.

## 4. Prepare the local model

Start Ollama, then run:

```sh
ollama pull qwen3:4b-instruct
ollama pull all-minilm:22m
ollama create qwen3-silentshift:4b-instruct -f config/Ollama.4b.Modelfile
```

This creates the exact local model alias expected by the application. No external model provider is used. The small `all-minilm:22m` model supports local evidence retrieval. Seeding a precedent corpus and enabling file intake are optional tasks after installation.

## 5. Start the backend

```sh
uv sync --locked
uv run --env-file .env python scripts/bootstrap.py
```

Wait for bootstrap to finish successfully before continuing. It starts IRIS and the Web Gateway, configures the local accounts, loads the application and starts the production. It does not submit orders or call the model. The API is at `http://127.0.0.1:52773/silentshift/api`.

If bootstrap fails, use the troubleshooting table below. Do not continue to the browser with an unfinished backend installation.

## 6. Open the workbench

```sh
npm --prefix web ci
npm --prefix web run dev -- --port 5173 --strictPort
```

Leave this terminal running. Open **http://127.0.0.1:5173**, select **Open workbench**, and connect with `ss-reviewer` and the reviewer password you set in `.env`. The connection indicator should show that the native API is connected. An empty case list is normal on a new installation.

## 7. Run your first order

1. Open **Scenario Lab** and choose **Quantity mismatch**.
2. Select **Inject into IRIS** once. Allow up to two minutes for local inference.
3. Open the returned investigation. It should show **Quarantined**, `20 CASE` against `240 EA`, a native trace ID and **zero deliveries**.
4. Try **Approved amendment**. Inspect the effective amendment and the resulting simulator delivery. If inference fails or the result needs review, inspect the case; do not approve a critical contradiction to force the example through.

You now have the application running. [Features and examples](docs/FEATURES.md) explain review tasks, trace metadata, precedents and file intake. They are optional reading after installation.

To bring your own CSV order feed, follow the [workbench CSV guide](docs/CSV_IMPORT.md). Its reference-import permission is a separate administrator opt-in.

## Troubleshooting

| What you see | What to do |
| --- | --- |
| Docker cannot connect | Run `colima start --profile silentshift` and check that `DOCKER_CONTEXT` is set in this terminal |
| Required image is missing or the build is rejected | Repeat step 2 with the official **Community build 154 ARM64** archive and the exact local tag |
| Bind mount or gateway configuration file is missing | Repeat the shared-directory check in step 1 before running bootstrap again |
| Login is denied | Use the local credentials from `.env`, not your InterSystems website account. An existing database retains its original accounts |
| Workbench says the API is unavailable | Check that bootstrap finished and port 52773 is free; inspect `.local/bootstrap.log` privately |
| Model requests fail | Confirm Ollama is running and has the exact alias from step 4. Verify that `host.lima.internal:11434` is reachable **from the IRIS container**; a working Mac connection does not prove container DNS works |
| The first investigation takes too long | Keep the tested wait at 120 seconds. Inspect the persisted case before retrying; do not create repeated injections while a result is uncertain |

Stopping containers preserves their database. Do not delete volumes to troubleshoot an installation you want to keep. Raw logs and `.env` may contain private configuration; share redacted errors only.

## Optional: check without a model

This is an alternative **backend verification**, not the full live workbench installation above. It installs the **currently published** native IPM version, starts a separate production, runs native tests and replays one frozen synthetic order. The independently checked public version is **0.3.0**, installed from the community registry in a new isolated container. [Commands and results](docs/JUDGE_VERIFICATION.md#public-030-install--november-8-2026-utc). It does not download or call Ollama. Only the recorded quantity-mismatch case is supported in this mode.

Complete steps 1–3 first. You can skip steps 4–7. The Web Gateway image must already be loaded. The driver requires at least **1.8 GiB free on the Mac and 3 GiB in the Docker VM**. It refuses an existing container name; choose another suffix and port if you have run this example before.

```sh
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
chmod 644 .local/ipm/vendor/zpm-0.10.10.xml
PUBLIC_IPM_VERSION=0.3.0
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest \
  --version "$PUBLIC_IPM_VERSION" \
  --execution-mode recorded-replay --container silentshift-bonus-registry-judge \
  --api-port 52843 --execute
```

The driver uses the public `zpm "install silentshift"` command. It should finish with `unit_suite_passed: true` and `replay_passed: true`. Repeat the API journey and print its Visual Trace URL with:

```sh
uv run python scripts/trace_example.py \
  --api http://127.0.0.1:52843/silentshift/api \
  --context colima-silentshift --container silentshift-bonus-registry-judge
```

Expected: `checks=12/12; passed=true`, `routing=QUARANTINED` and `delivery_count=0`. Containers remain available for inspection. Opening the printed native trace requires a permitted local IRIS portal account. [Recorded clean-install commands and results](docs/JUDGE_VERIFICATION.md) are evidence from earlier runs, not additional setup steps.
