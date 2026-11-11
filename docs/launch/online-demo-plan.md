# Native online demo — blocked preparation, not deployed

The online-demo bonus is 2 points under the official post. The static recorded tour and receipt inspector do not establish a hosted native application and remain outside that claim. Written contest-demo permission was received earlier; see [HOSTING_REVIEW.md](../HOSTING_REVIEW.md). Permission is not the missing step.

## Current technical boundary

Only the already loaded 154U ARM64 image is qualified. The earlier [Crashcart-host inspection](../evidence/landing-demo-nov10/host-preflight.json) found an x86_64 host with limited memory. That is historical resource evidence, not a current capacity measurement. No new cloud session, instance, resize, firewall, proxy, registry upload, image transfer or spend has been performed in this pass. Do not deploy an ARM64 image onto that host or infer a currently free compatible host.

A deployable native proposal requires an architecture-matching host with measured RAM/disk headroom, owner-approved cost/teardown bounds and independent confirmation that the existing application is unaffected. The local Compose launcher is an operator workflow; publishing all its web/API/Portal endpoints would expose writes. It is not a drop-in public read-only demo.

## Required preflight before any deployment approval

1. Read the proposed host's architecture, memory, CPU, disk, running containers and existing reverse-proxy configuration without changing them. Preserve another project's host and certificates.
2. Use an owner-supplied licensed ARM64 kit copied privately; never put the image, a derivative, model weights, keys or signing state in Git or a registry.
3. Run only synthetic seeded cases with recorded-provider mode unless live local inference is separately prepared and measured. Label mode prominently; never call recorded responses live inference.
4. Put a narrow inspection gateway in front of IRIS. Deny arbitrary ingest, review approvals, adapter writes, arbitrary native URLs, production control and account administration. Keep privileged/native ports loopback-only. Use distinct private roles, rate limits and container CPU/RAM/log limits.
5. Back up the proxy configuration, add only the new site block, validate before reload, and retain a rollback that removes the new app and restores the exact old proxy file. Do not alter another app's data or certificates.
6. Establish a reset/retention boundary, check no secret appears in served assets/responses, and test disallowed writes and native URL traversal from an anonymous browser. Verify the existing site's health before and after.
7. Present the exact resource cost, URL, expiry and rollback. STOP for a separate deployment approval. After deployment, inspect the real native trace and scenario externally before claiming hosting or proposing a bonus follow-up.

No native demo URL, viewer password, cloud latency, uptime or online-demo bonus is claimed. This is a gated plan with an unresolved host prerequisite, not an executable deployment receipt. There is no reason to publish another native package solely for these static/local tooling improvements.
