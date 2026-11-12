# Install SilentShift locally

This guide runs the repository source and its separate browser workbench. Public native IPM **0.3.2** includes Java PEX; the React workbench is built separately. [Publication proof](docs/evidence/ipm-032-publication-nov11/publication.json) and [fresh offline archive installation](docs/evidence/ipm-032-final-nov11/summary.json) are separate checks; a [fresh public 0.3.2 install](docs/evidence/voting-nov11-judge/summary.json) subsequently passed startup, the native suite and both keyless replays. Follow steps 1–7 in order. You do not need a cloud account or a paid model API key.

The tested native environment is **macOS on Apple Silicon, IRIS Community AI Hub 2026.3.0AI.154.0 (154U)**. Other builds and platforms have not been qualified. Organizers also permit **2027.1.0AI.109.0 Community**, but it has **not** been verified for SilentShift. [Official build clarification](https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-interoperability-workflows). The separate app/workbench is **0.2.1**. Public native IPM and OEX release are **0.3.2**. The native package includes the CSV backend/parser; it does not install the React web bundle. [Earlier public 0.3.0 installation](docs/evidence/ship-030-registry.json) · [separate live/source/browser gate](docs/evidence/candidate-030.json).

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

## Optional: source workbench without a model

After steps 1–2, you can inspect a real recorded native case without installing Ollama or editing `.env`. Load the public Node helper image, then use the source Compose launcher:

```sh
docker pull node:24-alpine
./scripts/judge-compose.sh
```

Use Compose 2.24 or later. The candidate builds a local-only Java JAR against the preloaded image’s Java 11/PEX SDK; never push that derived EAP image to a registry. Run one native test stack at a time; the launcher refuses another build-154 instance in this Docker context and does not stop it. It creates a dedicated project, private credentials and volumes, starts the native API and workbench, and runs the unchanged replay assertions. Expect `checks=12/12; passed=true`, a Visual Trace URL and the workbench URL. Read the printed local `runtime.env` file privately for your reviewer login; never copy it into a message or Git. The printed native Visual Trace URL opens the case session. The reviewer can inspect the trace, but reading native message bodies requires an existing administrator with message-content access; the application does not silently widen reviewer permissions. The README includes the captured native bodies for the no-login path. The replay demonstrates a hold only; vector retrieval is intentionally unavailable without embeddings.

[Actual fresh-clone result](docs/evidence/voting-finish-nov10/compose-final.json). This source path is different from the [public-package replay](#optional-check-without-a-model). The [Compose reference](docs/JUDGE_COMPOSE.md) covers different ports, direct `docker compose ... up`, retained resources and failures. For fresh local inference, continue with steps 3–7 instead.

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

The release replay explicitly installs native **0.3.2** with its matching assertion source. It does not request the moving registry latest. A 0.3.3 candidate/release can therefore coexist without changing this already verified path; promote the replay pin only after a separate public 0.3.3 gate passes.

This alternative verifies the **public native IPM 0.3.2 backend**, not the full web installation. It uses recorded provider answers for the synthetic quantity-mismatch case. It performs no fresh inference, calls no paid provider and needs no Ollama model or API key.

1. Start the existing Colima profile as in step 1. Load the separately obtained official **154U ARM64** image and Web Gateway as in step 2. No model, application `.env`, account website login or frontend build is needed for this check.
2. Run this command from the source checkout containing the launcher:

   ```sh
   ./scripts/judge-replay.sh
   ```

The launcher uses isolated Docker containers rather than Compose; the normal live setup above uses Compose. It automatically selects an unused private /28 network without deleting existing networks. If needed, pass a verified disjoint `--network-subnet 10.253.250.0/28`. To load a local vendor archive when the required tag is absent, add `--image-archive /absolute/path/to/official-build154-docker.tar.gz`; the launcher checks build and ARM64 architecture before retagging. It never downloads IRIS.

3. Expect `unit_suite_passed: true`, `replay_passed: true`, then a second `checks=12/12; passed=true`, `routing=QUARANTINED` and `delivery_count=0`. The launcher prints the actual session IDs and local Visual Trace URLs. [Fresh public main commands and output](docs/evidence/voting-week-nov10/judge-main-commands.txt).
4. Keep the private credentials and test resources for inspection. The launcher prints only the credential **path**, not passwords. Opening the native portal needs a permitted local IRIS account; a printed link is not anonymous portal access.

The launcher obtains the pinned source snapshot matching the published package's verification harness, downloads the checksum-pinned official IPM installer and runs literal `zpm "install silentshift"`. It creates its own distinct local test accounts in a fresh container; it does not change your existing `.env` or app. It retains the **1.8 GiB host / 3 GiB VM** disk floors. Never lower those limits. Other builds and x64 remain unverified.

| First-run problem | Next action |
| --- | --- |
| Required local IRIS image missing | Obtain the official build-154 Community ARM64 archive yourself, then follow step 2 to load and tag it. The launcher does not download or redistribute it |
| Docker context unavailable | Run `colima start --profile silentshift`; the launcher defaults to `colima-silentshift` and leaves Docker's default context unchanged |
| API port occupied or a requested container exists | Choose another `--api-port`, for example `52983`, and let the launcher choose a fresh name. It never replaces a container |

A fresh run may take several minutes for IPM download/compilation. Test containers remain available afterward; stopping them preserves their state. [Detailed historical driver commands](docs/JUDGE_VERIFICATION.md) are evidence, not additional setup steps. The public-package launcher deliberately uses release-matched 0.3.2 assertions. Its result does not validate later source changes; [source verification](docs/JUDGE_VERIFICATION.md#voting-week-finish--fresh-github-clones) records that separate boundary.
