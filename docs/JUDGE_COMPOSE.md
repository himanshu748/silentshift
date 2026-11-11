# Source Compose judge path

This is a **local, recorded-response** path for the current source checkout.
It starts the real IRIS production and React workbench. It does not install the
public IPM package, invoke Ollama, download a model or establish a hosted demo.
Only **2026.3.0AI.154.0 Community / 154U ARM64** is the intended native target.
The [fresh GitHub source run](evidence/voting-finish-nov10/compose-final.json) passed startup, the unchanged recorded replay and a real workbench login. Its failed predecessors remain [visible](evidence/voting-finish-nov10/compose-failures.json); the successful snapshot is separate from the subsequently versioned package candidate.

## Prerequisites

1. Follow the image-access and Colima prerequisites in [INSTALL.md](../INSTALL.md).
   Obtain the official licensed ARM64 build-154 archive from InterSystems yourself;
   it is never redistributed here. Load and tag it as
   `silentshift-iris:2026.3.0AI.154.0`. Another build or architecture is not a tested
   substitute.
2. Use Docker Compose **2.24 or later** and Python/uv. Colima profile `silentshift`
   is the default. The launcher preserves the existing host/VM disk safety floors.
3. Load the public helper images once, before running the stack:

   ```sh
   docker --context colima-silentshift pull containers.intersystems.com/intersystems/webgateway:2026.1
   docker --context colima-silentshift pull node:24-alpine
   ```

   Neither image contains the application or IRIS EAP software. Compose uses
   `pull_policy: never` for every service. The workbench's `npm ci` downloads only
   its lockfile dependencies; internet access is required for those downloads.

## One command, private generated configuration

From the source checkout:

```sh
./scripts/judge-compose.sh
```

The launcher checks the already-loaded IRIS image's build and architecture,
prerequisites, free ports and disk space; selects a disjoint private Docker subnet;
and creates a new `silentshift-judge-*` Compose project. It refuses an existing
project rather than replacing it. Generated, distinct local passwords stay in a
mode-600 `runtime.env` under a mode-700 ignored `.local/judge-compose/` directory.
Existing `.env` credentials/provider settings are not copied into this run.

Compose first builds the owned Java PEX sources against the preloaded image’s Java 11/SDK. The resulting local-only image must never be pushed to a registry. Native setup configures the managed `%Java Server`; signing keys and receipts persist in the manager volume. [PEX details and limits](JAVA_PEX.md).

Compose initializes its **dedicated manager/state volumes**, creates the
SILENTSHIFT namespace, compiles current source, configures its local accounts and
starts the production. The source is mounted read-only. A pre-existing namespace
without this project's ownership marker is rejected. Repeating the same raw
Compose configuration preserves its cases and requires the original passwords.
The frontend is copied into this project's own writable volume, excluding local
environment files and generated dependencies. npm and Vite never write to the
read-only checkout. Run one native judge stack at a time: the launcher refuses
another running build-154 instance in the same context instead of stopping it.
The native startup hook submits no orders. The launcher then calls the existing
authenticated Scenario API and runs the unchanged `trace_example.py` assertions.

Expected result after successful execution:

```text
execution_mode=recorded-replay; fresh_inference=false
checks=12/12; passed=true
```

The actual output includes a session ID and a Visual Trace URL. Open the printed
workbench URL (default **http://127.0.0.1:5193**) and connect using the reviewer
username/password in that run's local `runtime.env`. Credentials are not printed
or stored in the browser. Do not paste the file into chat, logs or Git.
The native portal/API defaults to **http://127.0.0.1:53033**. Both published ports
bind only to loopback. The recorded scenario is the unsupported `20 CASE` order;
other scenarios are outside the replay record's scope and cannot silently become
live investigations. The embedding endpoint and provider API key are forced empty.

To use different free ports or a known unused subnet:

```sh
./scripts/judge-compose.sh --api-port 53043 --web-port 5194 --network-subnet 10.253.245.0/28
```

If only a local vendor archive is available, `--image-archive /absolute/path/to/archive.tar.gz`
can load it, verify its build/architecture and retag it before setup. It never
downloads IRIS. Do not point that option at an untrusted archive.

## Direct Docker Compose command

The launcher is convenient but not required. After setting distinct private
passwords and `IRIS_IMAGE` in a gitignored `.env`, choose free ports and an unused
subnet, then run:

```sh
export DOCKER_CONTEXT=colima-silentshift
export COMPOSE_PROJECT_NAME=silentshift-judge-manual
docker compose --env-file .env -f compose.judge.yaml up --build --detach --wait --wait-timeout 300
```

This starts the initialized native API and workbench. It **does not** run a replay
until an operator requests one. The wrapper adds the real replay and its twelve
assertions. Use a new project rather than reusing the normal application project.
The direct command defaults to API port 53033, web port 5193 and subnet
10.253.247.0/28; set `SILENTSHIFT_JUDGE_API_PORT`, `SILENTSHIFT_JUDGE_WEB_PORT` and
`SILENTSHIFT_JUDGE_SUBNET` in `.env` when those are occupied.

## Failures and retained resources

- **Missing IRIS image:** the command stops before creating credentials or
  containers. Download access belongs to InterSystems; no alternative build is
  claimed supported.
- **Initialization or health fails:** inspect this new project's private
  `judge-state` logs and `.local/judge-compose/<project>/` command logs locally.
  Do not publish raw logs or `docker compose config` output: they may contain
  credentials. Do not lower disk limits or remove other projects to retry.
- **Ports, subnet or project already exist:** choose new values. Existing
  containers, networks and volumes are never replaced or pruned by the launcher.

The successful or failed project is retained for inspection. No automatic
cleanup is performed. Stopping this project without removing its volumes is
reversible; any permanent deletion remains a separate owner decision. Never use
`down -v`, a volume prune or image push as an installation step.

The twelve replay checks are a narrow recorded-route proof, not the full native
test suite, live-model accuracy evidence or proof of a new public IPM package.
