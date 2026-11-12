# Online demo plan (2 pts): NOT DEPLOYED, waiting for go-ahead

Prepared 12 Nov 2026. Nothing below has been created, changed or paid for.

## 1. Licence gate (your decision)

- **Clause.** IRIS Early Access Program Evaluation/Testing License Agreement (https://evaluation.intersystems.com/Eval/early-access/tos), section 2, as retained in [HOSTING_REVIEW.md](../../HOSTING_REVIEW.md) on 4 Nov: the licence is limited to internal testing/evaluation and "does not permit production, development or demonstration use". Section 6 restricts disclosure of the licensed software. Keyless replay mode still runs the licensed IRIS/AI Hub runtime, so removing API keys does not remove this clause.
- **Exception on record.** HOSTING_REVIEW.md quotes a reply from Irène Mykhailova (InterSystems, 8 Nov) in your correspondence: "Regarding the license, you are welcome to publish a demo as mentioned in the annoucement." Other entrants also host online demos with the same image (Readback, OcuTalon, Shutter and Mercurius in the bonus thread).
- **What I could not verify.** The live TOS page renders only through JavaScript, so I could not re-read the clause today. I can't see the 8 Nov reply myself; it is quoted from the repo.
- **Reading.** The text forbids a demo; the organizer reply permits a contest demo. Go ahead only if you're satisfied that the reply covers a public replay demo. If not, stop here.

## 2. Host choice

| Option | Arch | RAM | Fits? | Notes |
| --- | --- | --- | --- | --- |
| Crashcart Lightsail `crashcart-demo-nov10` (32.193.44.79), `small_3_0` | x86_64 | 2 GB, no swap (1.5 GB free on 10 Nov) | **No** | The only qualified image is 154U **ARM64**. The judge stack gives IRIS `mem_limit: 3g`. SSH is allow-listed to an old IP (223.188.47.133/32), so a live check would need a firewall change. Running IRIS here would also risk Crashcart. |
| Second Lightsail `embodiweave-demo` | x86_64 | 2 GB | No | Same arch problem; another project. |
| **New EC2 `t4g.medium`, us-east-1, Ubuntu 24.04 arm64** | **arm64** | **4 GiB** | **Yes** | Separate instance, so Crashcart's Caddy config and certificates are never touched. |
| Free tiers (Render, Fly, Railway, Oracle Always Free Ampere) | various | various | Not pursued | 6.9 GB licensed image would have to go through a registry (not allowed for the EAP image); Oracle needs a new account and card. |

Recommendation: a **new t4g.medium** with its own Caddy. Crashcart keeps running untouched; the only "rollback" is terminating the new instance.

## 3. Cost (on-demand, AWS Pricing API, 12 Nov)

| Item | Rate | ~100 h (12 Nov to 16 Nov 10:29 IST, plus margin) |
| --- | --- | --- |
| t4g.medium | $0.0336/h | $3.36 |
| 30 GB gp3 | $0.08/GB-month | ~$0.33 |
| Public IPv4 | $0.005/h | $0.50 |
| Data transfer out | first 100 GB/month free | ~$0 |
| **Total** | | **~$4.20**, then $0 after termination |

A billing alarm at $10 is part of the deploy step.

## 4. What runs

- `compose.judge.yaml` unchanged in substance: `SILENTSHIFT_PROVIDER_MODE=recorded-replay`, `SILENTSHIFT_API_KEY=""`, no LLM or embedding endpoint, partner files disabled. No routing policy, agent, eval or package change.
- Banner on every page and in `/healthz`: **"Replay mode: recorded agent proposals, live IRIS policy and receipts."**
- Public entry point is only `demo_gateway/server.py` behind Caddy (TLS via `<ip>.sslip.io`). It already refuses writes (`READ_ONLY_DEMO`, `READ_ONLY_PORTAL`, `METHOD_REFUSED`), rate-limits reads per address and caps trial runs.
- IRIS superserver 1972, Web Gateway and Portal ports bind to loopback only. Security group: 80/443 from anywhere; 22 from your current IP only.

## 5. Hardening

- Container limits: IRIS `mem_limit 3g`, `cpus 1.5`; gateway and web 256 MB each; log rotation 10 MB x 2.
- Reset on start: fresh `judge-state` and manager volumes on every `up` (the judge prepare step already seeds synthetic cases), plus a systemd timer that resets every 6 hours.
- Read-only: source mounted `:ro`; a public viewer account with no review, production-control or admin rights; only the fixed scenarios can be run.
- No secrets: the reviewer, viewer and gateway passwords are generated on the host in a root-only `.env` and never committed. Check: `grep` served assets and API responses for each generated password and for `api_key` before going public.
- Image transfer: `docker save` streamed over SSH straight to the host. No registry and nothing in Git.

## 6. Steps after "go"

1. Create a $10 billing alarm, the security group and the t4g.medium instance (tag `silentshift-demo-nov12`).
2. Install Docker, then copy the image over SSH and check its SHA256 matches `8fa0ae85777d`.
3. Clone v0.3.3, generate `.env`, run `docker compose -f compose.judge.yaml up -d`.
4. Add Caddy with only this site, run `caddy validate`, then start it.
5. From an anonymous browser: page loads, banner visible, a fixed replay run completes, Visual Trace opens, every write route returns 403/405, native URL traversal is refused, no secret appears in responses.
6. Check the Crashcart health URL before and after (`https://crashcart.32.193.44.79.sslip.io/healthz` was 200 today).
7. Report the URL and evidence, then stop before any bonus claim.

## 7. Rollback and teardown

- Something goes wrong: `aws ec2 terminate-instances` on the tagged instance, then delete its security group. Nothing else is touched.
- Crashcart: no change is planned, so no rollback is needed. If you'd rather reuse that host later, the old plan's rule still applies: back up the Caddyfile, add one site block, `caddy validate`, reload, restore the exact file on failure.
- End of voting (16 Nov after 10:29 IST): terminate the instance.
