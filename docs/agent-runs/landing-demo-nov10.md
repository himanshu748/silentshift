# Landing and demo candidate — local verification complete

Checked 2026-11-10 22:03:08 IST. Branch **landing-demo-nov10**, isolated from the owner's dirty
checkout, based on main **9f3178e3672d54df5eb711e94d9f688ed450d861 / v0.3.1**.
No source push, PR, merge, Pages dispatch, hosting deploy, OEX edit, release,
message or spending occurred. Native hosting is blocked separately below.

## What a judge encounters

The source README explains the technically successful but semantically wrong
order and shows real captures. It offers the historical video and a local native
path, but a judge cannot open a hosted native app. The licensed ARM64 image,
Docker/Compose and documented local prerequisites remain installation friction.
This is a first-screen/source audit, not a timed ten-second usability study.

The new [static page](../site/index.html) leads with **Successful messages.
Correct meaning.**, a real policy capture, the video and the native install
command. The unsupported **20 CASE / 240 EA** example explains the decision.
Visitors can explore policy, agent evidence, Workflow and Visual Trace without
installing. The live-demo control explicitly explains that hosting is unavailable;
it does not execute a simulated investigation or pretend to be a live service.

GSAP word entrance, pinned check/evidence/route steps, reveals and restrained
magnetic buttons use transforms/opacity. OS reduced motion and manual pause
remove pinning and make the story readable. Fonts and animation libraries are
self-hosted with notices. The existing captioned video is created on request,
avoiding its initial media-player work. No trackers or model calls were added.
The held-out results and their limits remain explicit; no accuracy gain is claimed.

## Verification from this pass

| Check | Result | Evidence |
| --- | --- | --- |
| New static page, Chrome CLI | **46/46** | [Browser receipt](../evidence/landing-demo-nov10/browser.json) |
| Existing disconnected workbench browser suites | **54 passed (1.0m)** | [Exact output](../evidence/landing-demo-nov10/workbench-browser.txt) |
| Python | **393 passed in 24.44s** | [Exact output](../evidence/landing-demo-nov10/pytest.txt) |
| TypeScript + Vite | **Passed** | [Types](../evidence/landing-demo-nov10/typescript.txt), [build and retained warnings](../evidence/landing-demo-nov10/build.txt) |
| Mobile Lighthouse | **97 / 100 / 100 / 100** | [Quality receipt and full compressed reports](../evidence/landing-demo-nov10/quality.json) |
| Desktop Lighthouse | **100 / 100 / 100 / 100** | [Quality receipt](../evidence/landing-demo-nov10/quality.json) |
| Existing runtime/package/workbench footprint | **163 tracked files compared; zero changed** | [Byte comparison](../evidence/landing-demo-nov10/change-boundary.json) |

Lighthouse order is performance/accessibility/best practices/SEO. These are local
loopback lab results, not deployed-host or real-user metrics. The latest mobile
repeat is retained rather than selecting the earlier higher score. Measured
initial transfer was **511940 bytes**,
excluding user-requested MP4 playback and opening full original captures.

The static harness exercises 360/768/1280/1920px layouts, tab arrows/Home/End,
mobile tab visibility, clipboard, modal Escape/focus, scroll pin cleanup,
OS/manual reduced motion, no-JavaScript content and actual captioned MP4 playback.
No console errors or failed requests were observed in the passing run.
[Reproduction commands](../evidence/landing-demo-nov10/commands.txt).

No native suite, live model investigation or native scenario was rerun here.
The native source and package are unchanged; this pass does not qualify another
build or architecture. Existing main CI is green at
[run 42827208709](https://github.com/himanshu748/silentshift/actions/runs/42827208709).
There is no branch CI result until an approved push. [Public readback](../evidence/landing-demo-nov10/public-state.json).

## Captures and recording

| Desktop | Mobile |
| --- | --- |
| [Hero](../evidence/landing-demo-nov10/desktop-hero.png) | [Hero](../evidence/landing-demo-nov10/mobile-hero.png) |
| [Workbench](../evidence/landing-demo-nov10/desktop-workbench.png) | [Workbench](../evidence/landing-demo-nov10/mobile-workbench.png) |
| [Footer](../evidence/landing-demo-nov10/desktop-footer.png) | [Footer](../evidence/landing-demo-nov10/mobile-footer.png) |

[Scroll recording](../evidence/landing-demo-nov10/scroll-preview.mp4):
**19.96s**, actual **1920×1080 H.264 / 25 fps**,
no narration, 9270208 bytes. It records the actual
static page and scroll behavior, not native execution. [Midpoint](../evidence/landing-demo-nov10/scroll-midpoint.png)
and [ffprobe receipt](../evidence/landing-demo-nov10/recording.json).

## Public link and listing audit

[Unauthenticated link checks](../evidence/landing-demo-nov10/links.json) resolved
all checked destinations except the intended, **not-yet-published** canonical
Pages target. The intended `https://himanshu748.github.io/silentshift/` returns
404; it is not advertised as a live clickable demo. In-page anchors resolve.
The video and MP4 are reachable without sign-in, and the actual MP4 played with
English captions in Chrome. Both Developer Community article links resolve.

The public [OEX listing](https://openexchange.intersystems.com/package/SilentShift)
shows **0.3.1** and the dedicated DPI-I-689 idea association. Its body still says
native **0.3.0**; the earlier source-only CSV/0.2.0 text has been replaced. The
editor, fields, contest selection and approval state were not changed or inferred
from the anonymous page. No idea/bonus award is claimed.

## Native hosting blocker and preservation

Read-only AWS CLI and pinned SSH verified the specified Crashcart instance is
**x86_64**. The qualified SilentShift image and Compose stack are **ARM64 154U**.
The host has two vCPUs and approximately 2 GB RAM; native capacity/latency there
is unverified. No emulation, image transfer, resource change, public write path
or deployment was attempted. Crashcart root and `/healthz` returned **200**, with
the same root body hash before/after inspection. That endpoint describes a
recorded static demo, not payment/model health.

[Host receipt](../evidence/landing-demo-nov10/host-preflight.json) ·
[Exact preflight, deployment gates and rollback boundary](landing-demo-deployment.md).
No honest native monthly quote or demo URL exists for this incompatible target.
The native-demo and online-demo-bonus statuses remain unverified / Not claimed.

## Repairs and retained attempts

- The installed Playwright skill wrapper could not find `playwright-cli`. The
  owner's CLI preference was fulfilled with the repository's real Playwright
  library and Chrome, not a fabricated browser result.
- Early mobile audits missed performance and exposed a contrast/name issue.
  Darker registration text, visible-label alignment and on-request native video
  loading resolved the final quality gates. [Earlier results](../evidence/landing-demo-nov10/quality-attempts.json).
- An initial reduced-motion assertion read before the browser dispatched its
  change event. The harness now waits for that actual state; no assertion was
  removed. [Retained failure](../evidence/landing-demo-nov10/browser-initial.json).
- The first isolated workbench config merged an old server entry and stopped at
  the occupied 5189 preflight; zero tests ran. Only the temporary configuration
  was corrected to 5207; all original assertions then passed. The temporary file
  was removed. [Initial output](../evidence/landing-demo-nov10/workbench-browser-first.txt),
  [executed config](../evidence/landing-demo-nov10/workbench-port-config.txt).

The three unmodified upstream GSAP distributions retain their original trailing
whitespace. The scoped authored-file whitespace check passes; the full check
reports only those vendor lines. [Exact warnings](../evidence/landing-demo-nov10/vendor-whitespace.txt).
No ignore rule or lint suppression was added.

## Approval order

The next exact **submit** permits **push landing-demo-nov10 and open its PR**,
using the [prepared PR description](landing-demo-pr-draft.md). It permits no merge
or deployment. Then stop separately for merge after CI, and for Pages publication.
The manual-only Pages workflow has no push/PR deployment trigger and only runs
on main. It has not been dispatched or cloud-tested.

Native deployment cannot proceed on the checked Crashcart architecture. A new
compatible plan requires review before its separate hosting approval. README
live-link edits/merge, OEX demo-link save and the two requested stale-branch
deletions remain separate future gates; neither `imgbot` nor
`chore/ipm-030-judge-freeze-nov8` was deleted. No IPM, release, OEX description,
article, email or community change was made.

## Local source commits

- `3ec6827` — ci(pages): prepare a manual-only landing deployment
- `f935f92` — test(site): exercise keyboard motion and captioned playback
- `02971e8` — feat(site): build an interactive recorded-evidence landing page

The following documentation/evidence commit changes no measured page code.
