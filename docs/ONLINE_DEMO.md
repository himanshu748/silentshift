# Online demo deployment

**Status: four-hour AWS trial installing; no live URL verified.** The online-demo bonus is not claimed. Recorded playback is not accepted as live inference evidence.

The owner authorized a bounded AWS trial, a $150 budget alert and an ARM-based CPU instance using the already-loaded **ARM64 2026.3.0AI.154.0 / 154U** image. The official EAP portal now offers Community 109 and explicitly says earlier 2026.3 builds were removed. This deployment will preserve build 154; no other build is claimed and no EAP image will be uploaded to a registry.

InterSystems' November 8 reply permits a contest demo and says idea implementation will be reviewed separately. That reply is not four-point qualification. See [hosting review](HOSTING_REVIEW.md).

## Controls before launch

- **The owner approved the smaller four-hour trial on November 9.** It uses `t4g.large`: two ARM vCPUs, eight GiB RAM and fifty GiB encrypted gp3 disk, with standard CPU credits. Estimated base cost is **$0.31** before tax/transfer; credit coverage is unconfirmed. The instance launched at **13:13:47 UTC** and its absolute termination timer was read back as active for **17:13:47 UTC / 22:43:47 IST on November 9**. AWS confirms instance-initiated shutdown terminates it and the root disk deletes on termination. No resize, GPU or longer hosting is authorized. [Price receipt](evidence/top3-aws-trial-quote.json).
- Monitoring-only AWS budget `SilentShift-Nov2026-150USD`: $150 monthly, account-wide gross costs before credits, email alerts at 80% and 100% actual and 100% forecast. It is not a hard cap; AWS cost data and alerts are delayed.
- Every new resource must carry `project=silentshift` and a deployment tag. No IAM role or registry publication is needed.
- SSH is restricted to the operator's address. Public access is HTTPS to synthetic demo scenarios and a scoped read-only portal. No direct IRIS/Ollama port is opened.
- Inference must be live local Ollama using the release model. Guided runs, rate limiting and reset must be exercised before publishing a URL. Viewer credentials stay out of Git.
- The requested long-run target is through November 20, with termination November 21 at 05:00 UTC, after the full November 20 Eastern day. That duration is not authorized until its cost is confirmed. Record actual resource IDs privately and schedule teardown only after successful deployment.

## Smaller options reviewed before spending

The owner requested Lightsail and Vultr comparisons instead of approving the proposed launch. **The comparison itself did not authorize spending; the later explicit four-hour `t4g.large` approval is the only compute authorization.** Prices below were read on November 9; estimates exclude taxes and transfer overages.

| Option | Resources | Price readback | Fit for the retained image |
| --- | --- | --- | --- |
| EC2 `t4g.large` | 2 vCPUs, 8 GiB RAM; separate 50 GiB gp3 disk and IPv4 | $0.0672 compute/hour; estimated $0.31 total base for four hours, $22.23 through November 20 | ARM64 matches. Trial launched; public latency is still unverified. Use **standard** CPU credits to avoid surplus-credit charges; depleted credits throttle performance. |
| Lightsail `large_3_0` | 2 vCPUs, 8 GiB RAM, 160 GiB disk, IPv4 and transfer allowance | $44/month, $0.05913/hour | The available Ubuntu 24.04 blueprint links to an x86 image. No supported ARM option was verified. The x64 154 kit is still missing. |
| Vultr `vc2-4c-8gb` | 4 vCPUs, 8 GiB RAM, 160 GB disk | $40/month, $0.055/hour | This selected plan uses Intel. No ARM option or Vultr credit entitlement was verified. It does not resolve the missing x64 kit. |

Sources: [AWS Lightsail pricing](https://aws.amazon.com/lightsail/pricing/), [the Ubuntu product linked by the Lightsail API](https://aws.amazon.com/marketplace/pp/prodview-s4zvkzmlirbga), [Vultr's public plans API](https://api.vultr.com/v2/plans), [AWS standard CPU-credit behavior](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances-standard-mode.html). The EC2 and hourly Lightsail prices also have dated AWS Price List API readbacks in the [preflight receipt](evidence/top3-demo-preflight-nov9.json). A matching CPU architecture is necessary; it does not prove the complete demo runs or meets the latency target.

## Teardown

The private deployment receipt at `.local/top3/aws/trial-nov9/deployment.json` records the exact instance, security group, key pair, account and region. Preview the targets first:

```bash
python3 scripts/teardown_demo.py --receipt .local/top3/aws/trial-nov9/deployment.json
```

At the scheduled end, execute the same bounded plan:

```bash
python3 scripts/teardown_demo.py --receipt .local/top3/aws/trial-nov9/deployment.json --execute
```

The script validates both project and deployment tags, the AWS account and volume deletion settings before changing anything. It terminates only that instance and removes only its dedicated security group and SSH key pair. Its attached volume must delete on termination. The monitoring budget remains. No source, local models, other project resources or EAP images are deleted.

## Local boundary already exercised

[The local integration receipt](evidence/top3-demo-local.json) records two actual native cases and printable Visual Trace. Arbitrary intake, review actions and CSV commits are blocked by the demo gateway. Reset clears only the journey pointer; it retains native history and run quotas. One native investigation runs at a time, with per-address and whole-trial caps. A restarted gateway keeps uncertain attempts and refuses automatic redispatch.

The dedicated synthetic reader has database READ plus scoped SELECT, never application database WRITE, SSReview or SSImport. Its API application adds the read/serialization capability only while that API executes. The private runner is a separate account and can dispatch only fixed scenarios through the gateway. The interactive Production Configuration page was blocked after two unsuccessful renders; it is excluded from the public allowlist. Reviewer task access is also unavailable. The guided demo links actual workbench production status and printable native Visual Trace instead. These limits are not hidden as completed requirements.

## Verification still required

Record the HTTPS URL, deployed source hash, build readback, model digest and prompt version, timed live investigation, native trace session, production/viewer reads, denied viewer writes, rate-limit/reset checks and teardown schedule. Until those results exist, a prepared instance or landing page does not establish an online demo.
