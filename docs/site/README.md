# SilentShift product page — local candidate

A static introduction to the real SilentShift workflow. It uses recorded native
captures and an existing captioned video. It does not run IRIS, call a model,
expose the workbench API or provide a hosted native demo. The **Try live demo**
button explains that deployment is unavailable; it never starts a pretend run.

## Preview

From the repository root:

```sh
python3 -m http.server 5197 --bind 127.0.0.1 --directory docs/site
```

Open <http://127.0.0.1:5197/>. No build step, provider key or external font service
is required. The video downloads only after Play is pressed. GitHub Pages is
**not enabled by this folder**, and the intended Pages address is not live yet.

## Check the page

With Node, Chrome and the repository's web dependencies installed:

```sh
npm --prefix web ci
node scripts/check_static_landing.cjs http://127.0.0.1:5197/ .local/landing-check
```

Keep the preview server running in another terminal. The CLI harness checks
keyboard access, the gallery, clipboard, reduced motion, responsive pin cleanup,
no-JavaScript content and actual captioned MP4 playback. It creates local
screenshots and a JSON receipt; it does not contact the native API.

The [November 10 receipt](../evidence/landing-demo-nov10/browser.json) records the
actual check count. [Lighthouse results and commands](../evidence/landing-demo-nov10/quality.json)
cover local mobile and desktop previews, not a deployed host. See the
[implementation and deployment report](../agent-runs/landing-demo-nov10.md) for
screenshots, recording, limits and remaining gates.

## Assets and motion

The gallery uses existing November 10 synthetic recorded-replay captures,
native session 58. Open-full-capture links preserve the originals. Smaller WebP
copies change encoding and dimensions only; [hashes and provenance](assets/provenance.json)
record the source. The policy and provider images are evidence of recorded
execution, not fresh inference. The video is the earlier core-workflow recording
and predates CSV and the newer interface.

Manrope and IBM Plex Mono are self-hosted with their OFL licences. Vendored GSAP
3.15.1, ScrollTrigger and SplitText retain their original notices and link to
their [standard licence](https://gsap.com/standard-license). There are no
analytics or third-party font requests. Motion uses transforms and opacity;
OS reduced motion and the page's pause control remove pinning and reveal all
three steps. Navigation and the product story remain readable without JavaScript.

## Publication gates

Only `docs/site` is a Pages artifact. Never upload the repository root, `.local`,
credentials, model files or the EAP image. The prepared manual-only workflow is on this local branch at
[.github/workflows/pages.yml](../../.github/workflows/pages.yml), with a
[review copy](../agent-runs/pages.workflow.yml). It has not been pushed, enabled
in Pages or dispatched. It has no push/PR deployment trigger and only runs on main.

The owner's exact **submit** is required separately for source push/PR, merge
and Pages enable/deploy. Publishing the static page does not establish native
hosting or an online-demo bonus. The existing Crashcart host is x86_64, while the
qualified SilentShift Compose image is ARM64; the native deployment is blocked.
[Hosting preflight and rollback boundary](../agent-runs/landing-demo-deployment.md).
