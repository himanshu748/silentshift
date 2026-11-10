# Landing and demo deployment plan — not executed

Prepared November 10, 2026 IST. Source branch: `landing-demo-nov10`, based on
main `9f3178e3672d54df5eb711e94d9f688ed450d861` / v0.3.1. The package, release,
Open Exchange fields and existing Crashcart deployment are outside this change.

## Pages: ready for a separately approved deployment

1. Obtain the owner's exact **submit** for the branch push and PR. Review the
   committed static page, local quality receipt and actual browser recording.
2. After CI, obtain a separate **submit** to merge. No squash or force-push.
3. Obtain a separate **submit** for Pages publication. The proposed PR includes
   the manual-only `.github/workflows/pages.yml`; it has no push/PR deployment
   trigger and is restricted to main. After the separately approved merge, choose
   GitHub Actions as the Pages source and dispatch that one workflow. No Pages
   configuration change or workflow dispatch has run.
4. The intended address is `https://himanshu748.github.io/silentshift/`. Confirm
   HTTP 200, the SilentShift title, all relative assets, keyboard/reduced-motion
   behavior and the capture links from a fresh signed-out browser. Re-run local
   quality measurements against HTTPS. Until then, the address is a target,
   not an advertised live site.

Prepared CLI operations for the Pages gate, after the workflow exists on main:

```sh
gh api --method POST repos/himanshu748/silentshift/pages -f build_type=workflow
gh workflow run pages.yml --repo himanshu748/silentshift --ref main
gh run list --repo himanshu748/silentshift --workflow pages.yml --limit 1
curl --fail --location --silent --show-error https://himanshu748.github.io/silentshift/
```

Use the Pages API creation command only if a fresh read confirms Pages is not
configured. If it is configured differently, stop and show the difference; do not
replace an existing site. If a workflow fails, preserve its log and stop before
retrying or changing publishing settings. Public-repository Pages needs no new
paid host; no account plan, billing or spend change is proposed.

Pages rollback, only with its own explicit approval: disable the Pages deployment
or restore the last approved static artifact. Neither operation affects IPM,
IRIS, Open Exchange or Crashcart. Do not delete the branch as part of deployment.

## Native demo: architecture preflight blocks deployment

The owner requested the existing Crashcart host. Read-only AWS CLI and
host-key-pinned SSH identified `crashcart-demo-nov10` at `32.193.44.79`,
us-east-1. It is **x86_64** with **2 vCPUs**, **1,998,614,528 bytes RAM**, no swap
and **58,375,380,992 bytes free disk** at the inspection time. The only observed
container was the existing Caddy static recorded Crashcart demo. These are
point-in-time measurements, not capacity or service-level guarantees.

SilentShift `compose.judge.yaml` pins **linux/arm64**, including the licensed
**2026.3.0AI.154.0 / 154U ARM64** image. The loaded/tested kit cannot run natively
on this x86_64 host. No x64 kit, emulation qualification or native cloud run is
available. Do not run Compose, copy the EAP image, enable emulation, add swap,
resize the host or replace the native requirement with a static mockup.

The following read-only guard describes the mandatory first check; it has no
remote mutation:

```sh
machine=$(uname -m)
case "$machine" in
  aarch64|arm64) printf '%s\n' 'Architecture matches the qualified image; capacity and deployment gates still remain.' ;;
  *) printf '%s\n' 'STOP: the qualified SilentShift image is ARM64; this host is not.' >&2; exit 1 ;;
esac
```

An architecture-matching host, or a separately supplied x64 build-154 kit plus
new native qualification, requires a new decision. Even then, capacity, licensed
image handling and read-only exposure must be verified before a deploy approval.
Compose exposes a local operator workflow; forwarding its whole web/API/Portal
to the public Internet would violate the requested read-only boundary. The
existing fixed-scenario demo gateway also admits bounded native runs, so it is
not a drop-in zero-write public interface. Do not silently expose either one.

No honest executable native deploy/rollback command can be prepared for this
incompatible target. There is no native URL, public viewer password or cloud
latency measurement to publish. The static Pages product page remains an
independent deliverable; it is not the hosted native app.

## Crashcart preservation and costs

Before/after inspection, Crashcart's root returned HTTP 200 with the same body
hash; `/healthz` returned HTTP 200 and explicitly described recorded static
serving. No remote files, containers, proxy, firewall, keys or services were
changed. Ephemeral local SSH credentials were removed. No rollback was necessary.
The [public preflight receipt](../evidence/landing-demo-nov10/host-preflight.json)
contains the measurements without credentials or account identifiers.

No resource was created or resized and no hosting spend was authorized/executed
in this pass. A safe native monthly cost cannot be quoted for the blocked
architecture; do not mistake use of an existing host for verified free capacity.
Any new host or resize needs a new measured proposal and cost approval before
its separate deployment **submit**. Never disturb Crashcart to make room.
