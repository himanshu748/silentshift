# Install SilentShift with IPM

The `silentshift` 0.1.0 module installs the native ObjectScript package, its
standard-library Python code, and synthetic fixture assets. Installation does
not configure security, start a production, ingest a message, call a model,
download an embedding model, or send a partner delivery.

On **2026-11-03**, IPM **0.10.10** successfully installed the current **43-class,
nine-asset** package into a new official ARM64 build-**154U** instance using the
literal `install LocalArchive/silentshift 0.1.0 -synchronous` command. The
SILENTSHIFT namespace and application classes were absent before installation;
the instance had no source mount or `/opt/silentshift` directory. The installed
Python modules resolved below `/usr/irissys/mgr/silentshift/SILENTSHIFT/`.

Package checks passed **five deterministic cases, ten invalid paths and four
module origins**. All **ten application/workflow tables were empty** after
installation, and package activation left production stopped. After separate,
explicit setup, a real local embedding indexed **one approved amendment**; one
quarantined SDK warmup diagnostic was recorded separately. The subsequent
real-API native evaluation passed all **five final policy/routing cases**, with
all **four evidence tools read once per case**, persisted evaluation and zero
unsafe releases. Agent proposals matched **four of five** cases; deterministic
server policy enforced the correct review route for conflicting references.
These are synthetic fixed-clock checks, not operational reliability claims.

The archive contains **53 files** and is **75,003 bytes**, SHA-256:

```text
0f8ee11c10621b37fab549995fa29eec732a1a9c76cab1dc9c89f8c9103397e6
```

Private source-package receipts are under
`.local/ipm/runs/20261103T180920827053Z/`; the clean installation receipt is under
`.local/ipm/clean-runs/silentshift-ipm-clean-20261103/resume-20261103T181358112209Z/`.
The final receipt, SDK diagnostic, amendment-index counters and native-five
export are under
`.local/ipm/clean-runs/silentshift-ipm-clean-20261103/native-20261103T181705297435Z/`.
The same fresh container was retained through two driver handoff repairs; the
package installation and five-case native evaluation each ran once.

This proves a **clean local IPM install and native API journey** from the
inspected archive. **Public-registry installation and publication remain
unverified**, and contest bonus eligibility/publication remains a separate gate.

For an existing, already bootstrapped runtime, the operator can run the bounded
local verification wrapper **after stopping intake and the production**:

```sh
python3 scripts/verify_ipm_native.py --context colima-silentshift --container silentshift-clean-iris-1 --install-client
```

The container must already contain the current helper/core classes from the
central bootstrap. The wrapper requires SILENTSHIFT, exact build 154 and a
stopped production, rebuilds a fresh source stage, optionally imports the pinned
client only if absent, runs real IPM load/package, inspects the archive, runs the
installed deterministic checks and compares before/after row counts in all
eight data tables (including Precedent) plus ReviewTask/Worklist. It never invokes Setup.Install and
leaves the production stopped for the operator to resume. Private logs and a
scope-labeled receipt go under `.local/ipm/runs/`. It proves local loading in an
existing namespace, **not a clean installation or public-registry install**.

## Target and prerequisites

- IRIS Community AI Hub **2026.3.0AI build 154** with Embedded Python. The manifest
  declares `Version=">=2026.3" Interoperability="enabled"`; SilentShift's runtime
  guard intentionally accepts only its tested build 154, including the official
  `$ZVERSION` representation `2026.3.0AI (Build 154U)`.
- An existing, interoperability-enabled namespace named **SILENTSHIFT**, with
  its own database/resource. An administrator can use the same definitions as
  [docker/merge.cpf](../docker/merge.cpf) on a disposable instance. The module
  does not create a namespace or enable interoperability in another namespace.
- IPM **0.9.0 or newer** installed in that namespace. Use a pinned, released IPM
  installer from the [official IPM project](https://github.com/intersystems/ipm)
  and record its version and installer checksum. Do not silently replace an
  administrator's IPM installation or repository configuration.
- Write access to the namespace's class database and manager directory while
  installing. Runtime access to those assets must remain read-only to partner
  inputs.

For the recorded test procedure, the pinned stable official client is
[IPM 0.10.10](https://github.com/intersystems/ipm/releases/tag/v0.10.10)
(released 2026-10-14). Its `zpm-0.10.10.xml` installer is **1,593,780 bytes**, with
the release asset SHA-256:

```text
daa2adabd66b488f57187d29712e54b0c25bbe000794fbf2a35a882c458b788a
```

Download and verify just that small vendor artifact, without modifying IRIS:

```sh
python3 scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
```

On the isolated target, expose the verified file as `/release/zpm-0.10.10.xml`.
After selecting SILENTSHIFT as an administrator, import it explicitly:

```objectscript
write $namespace,!
set sc=$system.OBJ.Load("/release/zpm-0.10.10.xml","ck")
do $system.Status.DisplayError(sc)
zpm "version"
```

This is a runtime mutation, distinct from downloading. Do not run it during a
production investigation. Do not use `enable -community` or global mappings for
this test: IPM remains namespace-local and no repository configuration is needed
to load/package local source.

`CheckTarget()` runs after IPM compiles the imported classes and before its
Activate phase copies files. A wrong namespace/build or running production fails
installation before assets or namespace configuration are changed. IPM can
already have imported class definitions when this guard fails; always choose the correct
namespace before running `load` or `install`.

## Prepare an inspectable source release

From the project root, choose a fresh, ignored staging directory:

```sh
uv run python scripts/package_ipm.py --output .local/ipm/stage-0.1.0
```

The script validates the manifest, frozen scenario checksum, class/path names,
explicit asset targets and activation methods. It copies only native `.cls`
files under `src/SilentShift`, the nine declared runtime files, this guide and
the manifest. The resulting `package-inventory.json` records file sizes and
SHA-256 digests. It refuses symlinks and an existing destination. This stage is
input to **the real IPM client**, not a simulated package or installation.

The manifest lists each core class explicitly. It does not export a broad
`SilentShift.PKG` wildcard, so pre-existing diagnostics under `SilentShift.Test`
in the build namespace cannot become package resources accidentally. Adding a
native source class requires updating that declared class list.

No `.env`, credentials, IRIS image, database, license key, local evidence,
`__pycache__`, node modules or generated frontend bundle is included. The MIT
license text is included; an IRIS runtime license is not.

In the **SILENTSHIFT** terminal on an isolated build-154 instance, with the stage
available at `/release/silentshift` and a writable export directory `/release/out`:

```objectscript
write $namespace,!, $zversion,!
zpm "version"
zpm "load /release/silentshift"
write ##class(SilentShift.IPM).AssetRoot(),!
write ##class(SilentShift.Bridge).IsRequiredBuild($zversion),!
write $length(##class(SilentShift.Bridge).FixtureJSON()),!
zpm "package silentshift -path /release/out/"
```

IPM's own success output and exit/status checks must be retained. Inspect its
actual archive contents; do not substitute the source inventory for an archive
inspection. Next, install that generated artifact in a **second clean build-154
instance** with no `/opt/silentshift` source mount. Record the artifact SHA-256,
IPM version, `$ZVERSION`, namespace, activation status and the following checks:

1. Assets resolve below the second instance's manager directory, not the source
   checkout or an extracted temporary archive.
2. `Bridge.FixtureJSON()` reads the frozen five-scenario dataset; Embedded Python
   can run deterministic assessment/policy from the installed package.
3. Production is still stopped, no security accounts/applications were created,
   and no model invocation or delivery occurred merely from installation.
4. Explicit setup, configured separately below, starts the real native chain;
   representative native verification uses the real API and persisted routing.

Load `tests/iris/IPMChecks.cls` separately from the package source and call
`##class(SilentShift.Test.IPMChecks).Run()` for ten invalid asset-path checks,
installed fixture checksum verification and all five **deterministic policy
regressions** through IRIS Embedded Python. These use the fixture's labeled
`test_recommendation` inputs; they measure package integrity, not native-agent
accuracy. The test invokes no model and creates no case or delivery records.
It also checks the resolved `__file__` of all four installed Python modules, so
an import still pointing at `/opt/silentshift` cannot pass as installed assets.

## Clean local installation through the real install command

`scripts/verify_ipm_clean.py` prepares a **local-only** verification path. Its
default is a read-only plan; a plan is not installation evidence. It requires a
fresh, real IPM-generated archive matching the current manifest and assets,
the already loaded official build-154 image, and the pinned IPM installer above.
It never pulls an image, downloads IPM, publishes a package or changes an
existing container, network or volume.

Generate the fresh archive in a separately authorized, stopped build namespace
using the existing wrapper. Do not use the earlier 33-class artifact for the
current 43-class source. Keep the receipt and archive together, then plan the
clean verification with the archive's actual path:

```sh
python3 scripts/verify_ipm_clean.py --archive /absolute/path/to/silentshift-0.1.0.tgz
```

The plan verifies archive boundaries and installer checksum, confirms that the
image is already loaded and the new resource names are unused, and checks host
and Colima VM disk space. The driver refuses to start below **1.8 GiB host free
space or 3 GiB VM Docker free space** and repeats the check immediately before
creation. An initial check on 2026-11-03 observed host **2.5 GiB** free and VM
Docker filesystem **5.3 GiB** free. A later host recheck fell to **1.1 GiB**, below
the safety floor; execution was deferred. After idle local models were unloaded,
the actual run started with **5.2 GiB** host free space, without deleting files.
A new writable container layer was estimated to need **0.8–1.3
GiB**, depending on IRIS database/journal growth; this is not a measured limit.
The 6.89 GB image layers are shared. There is no new manager volume or source
bind mount, and `/tmp` uses a bounded 192 MiB memory filesystem. The driver
retains created resources and evidence for review; it never deletes them to
make a retry appear clean. Recheck space after generating a package.

With execution explicitly authorized, add `--execute` and choose a fresh name:

```sh
python3 scripts/verify_ipm_clean.py \
  --archive /absolute/path/to/silentshift-0.1.0.tgz \
  --container silentshift-ipm-clean-step5 --execute
```

The new container starts from the loaded image by immutable image ID, with
networking disabled and no `/opt/silentshift` directory. Before installation,
the driver proves that the SILENTSHIFT namespace and application classes are
absent. It then explicitly creates an empty interoperability namespace and
enables `%Service_CallIn` on **this new instance only**, preserving the service's
authentication settings. CallIn is an administrator prerequisite for Embedded
Python, separate from package activation. The pinned IPM installer is imported
only into SILENTSHIFT.

The inspected archive is extracted into an isolated local filesystem repository.
The following are **real IPM CLI commands**, with statuses retained:

```objectscript
zpm "config set analytics 0"
zpm "repo -name LocalArchive -fs -depth 2 -path /home/irisowner/silentshift-ipm-release/repository/"
zpm "install LocalArchive/silentshift 0.1.0 -synchronous"
```

This uses the official pinned
[filesystem repository definition](https://github.com/intersystems/ipm/blob/v0.10.10/src/cls/IPM/Repo/Filesystem/Definition.cls)
and [package service](https://github.com/intersystems/ipm/blob/v0.10.10/src/cls/IPM/Repo/Filesystem/PackageService.cls):
the repository reads the archived manifest and returns an archive to IPM's
normal installer. No registry server or publish operation is involved. This
can prove a literal `install` in a clean instance; it does **not** prove a
Community registry listing or public-registry installation. For comparison,
the separately documented offline `zpm "load /path/to/archive.tgz"` route is
archive loading and must be named accordingly.

After installation, the driver loads the diagnostic class separately, verifies
the manager-directory module origins and all five deterministic cases, rejects
ten invalid paths, verifies all ten application/workflow tables are empty, and
checks that production remains stopped. The receipt records the input archive
SHA-256, image ID, actual `$ZVERSION`, client version, install command and proof
scope. Logs and receipts use mode **0600** under
`.local/ipm/clean-runs/<new-container-name>/`; the directory uses mode **0700**.
An installation receipt is written before any optional runtime setup.

Runtime setup and native model validation are separate explicit flags. The
following command also creates an isolated gateway on localhost port **52783**,
uses the private environment, calls `SilentShift.Setup.Install()` and checks
authenticated API health without submitting a case:

```sh
python3 scripts/verify_ipm_clean.py \
  --archive /absolute/path/to/silentshift-0.1.0.tgz \
  --container silentshift-ipm-clean-step5 --execute --activate-runtime \
  --env-file .env
```

The tested configuration is local `qwen3-silentshift:4b-instruct`, local
`all-minilm:22m`, and a **120-second** agent budget. Both endpoints must be
explicit local Ollama HTTP addresses on port 11434. The driver rejects missing
or remote provider endpoints and never downloads a model. Credentials are
passed through a private environment file and never included in printed plans
or command arguments. The gateway receives only its two generated config
files; the IRIS container receives no source mount.

To additionally run the existing real-API five-case native verifier, include
`--allow-model-calls` **in the initial invocation above**. That flag authorizes
the following separate local steps:

1. Index the single approved amendment from the installed synthetic fixtures
   with `IndexAmendments(.report)`. Record the actual embedding-request counter,
   persisted row count, model and dimensions. Create no invented resolved cases.
2. Copy only `tests/iris/ProviderProbe.cls` and run one real native SDK `basic`
   diagnostic to warm the local model. Require caught **0**, provider requests
   **1**, route **QUARANTINED**, delivery count **0**, and real case/session IDs.
   Record this synthetic diagnostic separately; exclude it from benchmark totals.
3. Run five local native investigations and their idempotency/policy/evaluation
   checks through the real API.

A successful native receipt must report five cases, all four evidence
tools, native traces, expected routing and a persisted evaluation. It is
separate from deterministic package checks. Do not rerun the creation command
with the same name to add a later phase: existing resources are deliberately
refused. An interrupted run leaves its named resources and failure-stage
receipt for operator inspection, without touching the existing runtime.

The recorded run above executed these gates. It also retained the original
pristine-state and installation logs when recovering from file-handoff and
network-transition failures. `--resume-pristine` is restricted to the exact
container ID, image ID, archive hash and recorded pre-namespace state; execution
rechecks namespace absence before changing anything. Installed instances must
not be treated as pristine retries. Input files are staged in the irisowner
home directory, outside `/tmp`; explicit activation disconnects Docker's
exclusive `none` network before attaching the new isolated gateway network.

## Installed paths and explicit setup

FileCopy writes individual files below
`<IRIS-manager-directory>/silentshift/SILENTSHIFT/`:

```text
python/silentshift/{__init__,engine,evaluation,embeddings}.py
fixtures/v1/{scenarios.json,manifest.json,README.md}
fixtures/runbooks.json
LICENSE
```

Activation verifies the path, rejects symlinked package files/directories,
checks the frozen dataset SHA-256 and stores only
`^SilentShift.Config("AssetRoot")` in SILENTSHIFT. `AssetRoot()` falls back to
`/opt/silentshift` when no IPM path was configured, preserving the existing
Docker journey. `AssetPath()` rejects absolute paths and traversal. No global
Python path or shared site-packages directory is modified.

After a successful package installation, an administrator explicitly provisions
the runtime environment using the names documented in [.env.example](../.env.example):

```text
SILENTSHIFT_IRIS_USERNAME
SILENTSHIFT_IRIS_PASSWORD
SILENTSHIFT_VIEWER_USERNAME
SILENTSHIFT_VIEWER_PASSWORD
SILENTSHIFT_GATEWAY_PASSWORD
```

Passwords must contain at least 12 characters and the viewer/reviewer identities
must be distinct. Supply them through the runtime's private environment; never
place their values in the manifest, terminal transcript or release archive.
Then, in SILENTSHIFT:

```objectscript
set sc=##class(SilentShift.Setup).Install()
do $system.Status.DisplayError(sc)
```

This **explicit** step configures application roles/users, password-protected
REST applications, the Web Gateway service and CallIn, seeds synthetic approved
references, configures workflow and starts `SilentShift.Production`. Existing
application users are preserved. Review these instance-wide security changes
before using a shared instance. The package activation does not perform them.
Configure a separate Web Gateway as in [README.md](../README.md), the local
`qwen3-silentshift:4b-instruct` model and local `all-minilm:22m` embeddings before
running model scenarios. The current transport accepts only the documented local
route. Model weights are not bundled by IPM.

The React workbench remains a separate frontend (`npm --prefix web ci`, then
the documented development proxy or production reverse proxy). The IPM module
installs the native backend, not a pretend CSP frontend with a broken `/api`
route. File-adapter inbox provisioning and optional embedding/vector indexing
also remain explicit runtime steps.

## Publish and verify the public package

**Publication requested through Open Exchange on 2026-11-04; moderation is pending.** The saved 0.1.0 application has **Publish in Package Manager** checked and shows **Sent for approval**. Anonymous registry listing and manifest reads returned 404; public registry installation has not been performed. Sources were rechecked on **2026-11-04**. The [official publication
guide](https://docs.openexchange.intersystems.com/apps/ipm/) makes Open Exchange
the gateway to `pm.community.intersystems.com`. The CLI `publish` action targets
a separately configured publishing registry. Public Community publication uses
the Open Exchange form below; it does not require inventing a registry account,
token or direct-upload endpoint.

### 1. Publish through Open Exchange

1. Confirm that the [public repository](https://github.com/himanshu748/silentshift)
   contains root-level [module.xml](https://github.com/himanshu748/silentshift/blob/main/module.xml),
   module `silentshift`, version `0.1.0`, license and the full 43-class source.
   Keep the published source revision and the verified archive receipt together.
   The local archive above is already tested; include no EAP kit, derived image,
   IRIS database, credentials or private logs in a release.
2. Sign in and open the existing
   [SilentShift draft](https://openexchange.intersystems.com/portal/products/SilentShift/edit).
   Use [the application copy](OPEN_EXCHANGE_COPY.md), set the repository URL,
   actual video URL and idea link, and select **Publish in Package Manager**.
   Declare the tested **2026.3.0AI.154.0 ARM64 Community** runtime.
3. Use **Save** and **Preview**, review the fields, then manually click
   **Send for Approval**. Retain the saved submission state and, when approved,
   the actual public application URL. Follow any moderation instructions.
4. Wait for the `silentshift` **0.1.0** listing in the public registry and run the
   fresh registry verification below. OEX approval, registry availability and
   contest entry each need their own confirmation. An app draft or checked box
   alone is insufficient.

The organizer's [IPM clarification](https://community.intersystems.com/node/590306)
requires publication and checks installation on the declared AI Hub build. The
later build-109 allowance does not establish SilentShift compatibility with
109: this package intentionally guards its tested build **154**. The module's
`SystemRequirements` remain explicit. The potential **2-point** IPM bonus stays
unconfirmed until publication, real registry installation and organizer review.

### 2. Optional private/test-registry publish command

The official guide also recommends testing a publish operation against a
registry the developer controls or the linked test registry. This is a separate
external write, performed only if the user chooses it. It does not publish to
the public Community registry. Use an isolated stopped build-154 SILENTSHIFT
namespace with the module already loaded. Ask the registry operator for the
actual URL and username; replace both placeholders before running. Supply
`SILENTSHIFT_IPM_REGISTRY_PASSWORD` privately to the IRIS process.

Enter `zpm`, then run these at the **IPM prompt**:

```text
repo -r -n TestPublish -url <REGISTRY_URL_FROM_OPERATOR> -username <REGISTRY_USERNAME> -password-env SILENTSHIFT_IPM_REGISTRY_PASSWORD -publish 1
repo -list
publish silentshift
quit
```

Inspect the target shown by `repo -list` before publishing. IPM 0.10.10's
[credential handling](https://github.com/intersystems/ipm/blob/v0.10.10/src/cls/IPM/Repo/Definition.cls)
supports `-password-env`; no password value belongs in command history or
transcripts. Authentication and acceptance for a user-owned/test registry have
not been exercised here. No test-registry username or token is assumed.

### 3. Verify installation from the public registry in a fresh instance

Use a **new official build-154 instance**, separate from the retained filesystem
proof and the existing application runtime. Provision the empty
interoperability namespace **SILENTSHIFT**, its database/resource, Embedded
Python CallIn prerequisite and pinned **IPM 0.10.10** as described above. Keep
production stopped, omit source mounts, and do not copy a source stage, local
archive or application classes into this instance. Only the later diagnostic
class is copied separately. The existing `verify_ipm_clean.py` driver installs
from its local filesystem repository; its receipt proves that specific source.

Before public installation, capture the actual terminal output:

```objectscript
write $namespace,!, $zversion,!
write ##class(%Dictionary.CompiledClass).%ExistsId("SilentShift.Setup"),!
write $data(^SilentShift.Config("AssetRoot")),!
```

Expected namespace/build: **SILENTSHIFT / 154U** on this ARM64 target. Both final
values must be **0**. Capture the absence of `/opt/silentshift` and the instance's
mount list as well. Do not substitute a previously installed namespace.

Enter `zpm`. Run each command at the **IPM prompt**, retaining success/error
output and stopping on an error:

```text
version
config set analytics 0
repo -list
repo -r -n PublicCommunity -url https://pm.community.intersystems.com/ -user "" -pass "" -publish 0 -read-only 1
repo -list
search -versions silentshift
install PublicCommunity/silentshift 0.1.0
list-installed silentshift
history find -Daction=install -Dpackage=silentshift
quit
```

The empty credentials select anonymous public access; no publishing permission
is enabled. If this URL is already configured under a different name, use that
listed name consistently instead of `PublicCommunity`, with publishing disabled;
the [pinned remote-repository code](https://github.com/intersystems/ipm/blob/v0.10.10/src/cls/IPM/Repo/Remote/Definition.cls)
rejects duplicate URLs. `search` shows repository headings; verify that version
**0.1.0** appears under the public URL. The qualified `install` pins the source,
so a local cache/filesystem package cannot establish this gate. These forms are
supported by the [pinned CLI implementation](https://github.com/intersystems/ipm/blob/v0.10.10/src/cls/IPM/Main.cls).
The older `-synchronous` modifier is deprecated in 0.10.10 and is omitted here.

After successful installation, at the ObjectScript prompt:

```objectscript
set module=##class(%IPM.Storage.Module).NameOpen("silentshift")
write module.VersionString,!
write ##class(SilentShift.IPM).AssetRoot(),!
set sc=##class(SilentShift.IPM).RequireStopped()
do $system.Status.DisplayError(sc)
set sc=$system.OBJ.Load("<COPIED_DIAGNOSTIC_DIRECTORY>/IPMChecks.cls","ck")
do $system.Status.DisplayError(sc)
set sc=##class(SilentShift.Test.IPMChecks).Run()
do $system.Status.DisplayError(sc)
```

Replace `<COPIED_DIAGNOSTIC_DIRECTORY>` with the actual path containing only the
separately copied `tests/iris/IPMChecks.cls`. Require version **0.1.0**, the
namespace-specific manager asset root, successful statuses and
`SILENTSHIFT_IPM_CHECKS_OK path_rejections=10 deterministic_cases=5 module_origins=4 ai_runs=0`.
Record zero rows in the eight SilentShift data tables plus native ReviewTask and
Worklist, as the local clean driver does. No case, delivery or model call should
be caused by package installation.

For the complete post-registry native gate, separately configure the private
runtime environment and isolated gateway, run explicit `Setup.Install()`, index
the approved amendment and record the separate SDK warmup as above. Then run
the actual API verifier against that instance's **own** port:

```sh
uv run --env-file .env python scripts/verify_native.py \
  --api http://127.0.0.1:<REGISTRY_TEST_GATEWAY_PORT>/silentshift/api \
  --allow-model-calls --output .local/ipm/public-registry-native-five.json
```

This later command invokes the five local model investigations; run it only
when that inference is explicitly authorized and idle. Require `passed`,
`native_verified` and `evaluation_persisted` to be true, five accepted cases,
all four tools, expected routes and zero unsafe releases. Keep the separate
diagnostic out of that evaluation.

Retain registry URL, search output, version, source-qualified install command,
history record, `$ZVERSION`, client version/checksum, pristine-state checks,
installed module origins, empty-state checks and any later native export.
Record the public artifact's own digest when retained; it may be rebuilt and
must not be assumed byte-identical to the local 75,003-byte archive. The pinned
[remote package service](https://github.com/intersystems/ipm/blob/v0.10.10/src/cls/IPM/Repo/Remote/PackageService.cls)
checks the registry's supplied SHA-1 when present; label an independently
computed SHA-256 distinctly. Redact credentials and any install capabilities
before sharing a receipt. Until these steps actually run, keep
`public_registry_install_verified` and `registry_published` **false**.

No registry publication, Open Exchange submission, paid call or runtime restart
is performed by `package_ipm.py` or by this documentation update.

Use `python3 scripts/inspect_ipm.py /path/to/generated.tgz` to inspect the real
archive without extracting it. It canonicalizes the repeated path separators
emitted by IPM 0.10.10 and rejects duplicate canonical names, unsafe paths,
links, oversized files,
extra classes (including diagnostic/test classes from a dirty build namespace),
undeclared assets, modified runtime data and altered deployment metadata. Its
archive receipt still does not claim native installation or public publication.

The manifest/FileCopy/Invoke conventions follow the
[official IPM manifest documentation](https://github.com/intersystems/ipm/wiki/03.-IPM-Manifest-(module.xml)):
application Python files use `FileCopy`, individual targets avoid destructive
directory replacement, and asset configuration runs after Activate's copies.
Reinstalling source/Python code in a running production is an operator-managed
upgrade: stop intake and the production before upgrading and revalidate after
restart. IPM installation itself does not restart a production or invalidate
already imported Python modules.

## Upgrade, rollback and removal

Stop intake and `SilentShift.Production` before any package upgrade. Save a
database backup, the previous verified package archive/digest and a copy of its
installed asset tree. Record `^SilentShift.Config("AssetRoot")` and security
configuration separately. Reload/install the selected version, inspect its
activation status and rerun deterministic/native verification before resuming
intake. Individual FileCopy targets replace the declared files only; they do
not recursively replace the manager directory or delete unrelated files.

Filesystem copies and the namespace configuration are not one atomic database
transaction. If activation fails, keep the production stopped, restore the
previous verified archive/assets and matching AssetRoot, then restart only after
verification. An in-process Python import cache can retain earlier code;
perform the operator-managed production/runtime recovery appropriate to the
instance rather than assuming a file copy changed already loaded modules. This
0.1.0 package has no schema migration or automatic data rollback.

`zpm "uninstall silentshift"` is supported only for a **stopped, empty**
installation. Its Clean/Before guard refuses removal if any SilentShift data
table contains rows or an empty state cannot be established. This prevents an
uninstall from becoming a way to delete existing investigations, references,
review records, evaluations, receipts or indexed runbooks. A populated instance
requires a separately planned data migration/retention decision; use a compatible
package rollback instead. Never add `-purge`, `-all` or `-force` to bypass this
procedure.

The removal guard also refuses native ReviewTask, Worklist or MessageHeader
history. It does not remove the native workflow/message history to make an
installation appear empty.

For an eligible empty installation, the guard removes only the AssetRoot value
that exactly matches this module's target. IPM then removes module classes and
the nine explicitly declared asset files. It leaves parent directories, case
database directories, unrelated globals, security users/roles, REST application
configuration, gateway configuration and the IPM client untouched. Security
resources created by an earlier explicit Setup.Install remain an administrator's
responsibility. Uninstall failure can leave partial class/file removal; retain
the installation log and restore the verified archive before using the app.
