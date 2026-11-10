# Online demo status

**Not deployed. No live demo URL is verified, and the online-demo bonus is not claimed.** The November 9 AWS trial was stopped early after the direct/resumable archive transfer failed. Native installation never began and public application ingress never opened. AWS readback confirms the instance terminated and its root volume, security group and key pair were removed. The monitoring budget remains. [Closure receipt](evidence/top3-aws-trial-result.json).

Use [INSTALL.md](../INSTALL.md) for the qualified local path. Recorded playback is explicitly labeled and is not an online live-inference demo.

## What the trial established

The owner approved a four-hour ARM CPU trial, then explicitly approved eight hours total after the slow upload was measured. The machine was `t4g.large`: two vCPUs, eight GiB RAM and fifty GiB encrypted gp3 disk. Standard CPU credits were confirmed, avoiding surplus-credit charges. The estimated maximum base cost was **$0.62** before tax/transfer; actual billed cost and credit coverage are not yet established. Early teardown means that approval is not a claim that the entire estimate was spent.

The instance launched at **13:13:47 UTC on November 9**. Its extended absolute timer was read back for **21:13:47 UTC**, with a second shutdown scheduled earlier. AWS confirmed shutdown terminates the instance and deletes its root disk. Every created instance, volume, network interface, security group and key pair carried project/deployment tags. SSH was restricted to the operator's address; application ports stayed closed. No GPU, resize, tunnel, image registry push or longer hosting was performed.

[Original launch controls](evidence/top3-aws-trial-launch.json) · [Explicit extension and timer readback](evidence/top3-aws-trial-extension.json) · [Dated price readback](evidence/top3-aws-trial-quote.json).

The retained official ARM64 build-154 image and the exact local Qwen/minilm manifests were exported privately and hashed. Only **4 of 60** archive chunks were verified on the receiver before the transfer stopped. A resume harness also encountered an already-complete destination; complete files were checksum-verified before being excluded from the queue. The subsequent server-response timeout ended the attempt under the two-failure rule. Logs, local originals and partial-transfer evidence remain; there was no cloud model investigation and no cloud latency measurement.

This result identifies a transfer blocker. It does not establish that the selected CPU is fast enough or that another provider/model/build works.

## What works locally

[The local integration receipt](evidence/top3-demo-local.json) records two fresh native guided cases: a held quantity contradiction with no simulator delivery, and an approved amendment with one simulator receipt. Printable Visual Trace rendered actual provider request/response hops. These are local results, not deployment evidence.

The separate loopback demo gateway admits only fixed synthetic samples. It serializes investigations, applies per-address and whole-trial limits, and blocks arbitrary intake, review actions and CSV commits. Reset clears a journey pointer, preserving native history and quotas. A restarted gateway retains uncertain attempts and never redispatches them automatically. The second local result required explicit read-based reconciliation after a gateway restart; its gateway duration is unavailable.

A dedicated reader has database READ and scoped SELECT; it has no application database WRITE, SSReview or SSImport. The private runner is a different account. The reader's API application adds read/serialization capability only while that API executes. Credentials stay outside Git. Reviewer tasks are unavailable to this reader. The interactive Production Configuration page failed two restricted render attempts and was removed from the demo allowlist. The guided page links actual workbench production status and printable native Visual Trace instead.

The full Python suite passed **286 tests in 18.88 seconds**, including pure approval/timer checks. [Output](evidence/top3-final-pytest.txt). Fake-upstream and timer tests do not substitute for native execution or hosting proof.

## Prepared operator tools

`scripts/bootstrap_demo_host.py` is plan/compile-tested, not end-to-end cloud-qualified. It requires a privately prepared bundle, the separately licensed image, exact model hashes and an active absolute termination timer matching the approved bound. It loads current native source without application source mounts, includes the native unit gate and keeps Caddy stopped pending live-inference/HTTPS checks. Default execution is a plan; `--execute` is required to install. It does not create AWS resources or publish packages/images.

`scripts/teardown_demo.py` validates the exact account, project/deployment tags and root-volume deletion settings before terminating the one recorded instance and removing its dedicated security group and key pair. The successful trial cleanup used:

```bash
python3 scripts/teardown_demo.py \
  --receipt .local/top3/aws/trial-nov9/deployment.json --execute
```

The receipt and credentials are private. Do not reuse the terminated host address or try to reconnect to a potentially reassigned IP.

## What another attempt needs

A new paid trial or hosting through November 20 requires a **new cost approval**. The previous trial is closed. First establish a reliable direct transfer path for the retained ARM64 image and exact model bundle; the official portal no longer offers build 154. No other build is claimed tested.

Then verify native installation, the runtime/model/source identities, a timed fresh live investigation, public HTTPS, read-only access, denied writes, reset/rate limits and a bounded teardown. There is no prepared public login or URL to advertise until those checks pass. Any latency above the requested threshold must be reported before asking for a larger paid machine.

InterSystems' November 8 reply already permits a contest demo under the EAP clarification. Permission is not the present blocker and is not four-point qualification. [Hosting review](HOSTING_REVIEW.md). The dedicated DPI-I-689 association is now publicly visible; organizer qualification remains unconfirmed.
