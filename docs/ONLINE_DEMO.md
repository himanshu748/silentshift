# Hosted replay demo

Verified from outside the host on November 12, 2026 (IST): **[Open the guided demo](https://34.239.152.223.sslip.io/demo/)**. The root page also returns HTTP 200 and discloses replay mode. This runs native IRIS 2026.3.0AI.154.0 / 154U ARM64, including evidence reads, deterministic policy, routing and Java PEX receipt export. **The agent proposal is recorded; no fresh model inference or new evaluation is claimed.**

The supported fixed sample is 20 CASE versus 240 EA without an approved conversion. Its native outcome is QUARANTINED with zero deliveries. Other samples are refused by the public admission layer: the shipped recording is intentionally scoped to this one synthetic case. An initial amendment attempt safely went to REVIEW after the provider rejected its replay scope; neither the policy nor that replay restriction was changed.

## Try it

1. Open the guided demo and press **Replay this investigation**.
2. Inspect the native case, evidence and routing reason. The demo admits two investigations per address per ten minutes, with thirty admitted runs per host boot. A third same-address attempt returned HTTP 429 in this verification.
3. For the workbench, use **Show read-only viewer login** on the guided page and the separate viewer account shown there. Never enter a personal InterSystems password. The reader cannot approve reviews, commit CSV imports or control production. Actual browser sign-in and persisted-case inspection passed; reviewer actions were disabled.

The reset button clears only the visitor's journey selection. Host restart recreates the synthetic native database and gateway admission state. A real reboot was verified: the boot ID changed, the case list was empty, and a new native replay completed afterward.

## Evidence and limits

- [Dated summary](evidence/demo-nov12/summary.json): thirteen outside-host checks passed, including native production health, case inspection, management-path refusal and closed native ports.
- [Admission checks](evidence/demo-nov12/guard-checks.json): unsupported sample refused; per-address run cap enforced.
- [Actual native result](evidence/demo-nov12/after-reboot-job.json) and [signed Java PEX receipt](evidence/demo-nov12/after-reboot-pex-receipt.json). The receipt was read from the native export store; it is not a fabricated delivery receipt or an extra REST field. [Independent SHA-256/RSA verification](evidence/demo-nov12/after-reboot-pex-receipt-verification.json) returned `Verified OK`.
- [Default-view capture](evidence/demo-nov12/guided-result-after-reboot.jpg) and [390 px mobile capture](evidence/demo-nov12/guided-mobile.jpg). The mobile viewport had no horizontal overflow.
- Printable Visual Trace renders the native message graph, including ReceiptExporter. Its interactive HyperEvent calls raise a warning under the restricted gateway. This was observed twice and retained as a [known limitation](evidence/demo-nov12/native-trace-warning.jpg); no generic broker POST access was enabled to hide it. Use the case's retained evidence and policy for the reliable inspection path.

The deployment adds only host-level disclosure, single-sample admission and resource limits. The native source, agent and deterministic policy match source commit `a5b5329a0cd0e558b4f6f55819861c918cf320c1`; no native package was changed or published for hosting. The public native package remains 0.3.3 and React remains 0.2.1.

## Operating window and cost

Automatic stop is scheduled for **16 November 2026, 12:30 PM IST** (`1794812400`). Shutdown behavior is **stop**, not terminate. Caddy is disabled at boot; the reset service explicitly starts it only after native production and gateway health pass. IRIS/default-account passwords are refreshed at startup and retained only in private host files; the intentionally shared reader is separate from the private scenario runner.

The USD 10 budget has confirmed email subscribers for actual spend above USD 5 and forecast above USD 10. Alerts are not a hard cap, and delivery of an alert email has not been tested. Standard CPU credits disable surplus-credit billing. At the owner's planning rate of approximately USD 0.04 per compute hour, compute is estimated at USD 3.69 through the stop time, excluding storage, tax and transfer. Actual charges and credit coverage are unverified. Stopped storage remains billable and requires a separate cleanup decision.

No online-demo points or organizer qualification are asserted by this deployment receipt. Adding its URL to PR #17, merging, updating OEX and posting a bonus reply remain separate owner gates. Crashcart and its AWS resources were not accessed.

---

# November 9 trial history

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
