# Static judge page — unpublished candidate

This folder is a portable static site. It does not run IRIS, expose an API or qualify as a hosted native demo. No Pages configuration or deployment workflow is enabled by this folder.

Preview from the repository root:

```sh
python -m http.server 5189 --bind 127.0.0.1 --directory docs/site
```

Open `http://127.0.0.1:5189/`. The page is a local preview. Publishing remains separately gated.

## Captures

The gallery copies five November 10 captures from `docs/assets/voting-week-nov10/`:
original order, policy evidence, native agent, Workflow review and persisted
provider metadata. They are one synthetic **recorded replay**, session 58, on the
unreleased source branch. No fresh inference or hosted demo is implied.
[Provenance and permission restoration](../evidence/backend-polish-nov10/11-native-ui.json).

The final local page was checked at 390px and 1440px with no horizontal overflow,
all seven images loaded, keyboard activation of the run anchor and no observed
browser errors. [Receipt](../evidence/voting-week-nov10/site-final-browser.json).
Reduced-motion CSS is present; OS-level emulation was not performed for this page.

Manrope and IBM Plex Mono Latin WOFF2 files were copied from the repository's installed `@fontsource` dependencies. Their OFL license files are included beside the fonts. There is no external font request. The only embedded third-party content is the privacy-enhanced YouTube player, loaded lazily with a visible fallback link.

The replay command points to the source branch's new shell entry. Do not publish this candidate until that entry and the final capture paths are verified and present on the public branch chosen by the owner.

## Publication gate

Publishing GitHub Pages requires the owner's exact `submit` approval as a separate action. Upload only this folder as a Pages artifact if approved. Do not publish the repository's `.local` directory, EAP archive, Docker image, credentials or model files. `assets/` contains only the logo, actual captures and licensed fonts.

## Prepared GitHub Pages workflow

A manual-dispatch-only candidate is at
[`docs/agent-runs/pages.workflow.yml`](../agent-runs/pages.workflow.yml). It has not
been installed under `.github/workflows`, enabled, dispatched or cloud-tested.
After separately approved source push and merge, publishing requires its own
exact **submit**. Then the approved action can install that workflow, select
**Settings → Pages → Build and deployment → GitHub Actions**, and dispatch it.
Upload only `docs/site`, never the repository root or `.local`. The host URL must
come from the successful Pages deployment; no live URL is claimed in advance.

The page advertises the new shell replay entry. Confirm that the chosen public
source branch contains it and its guide before publishing. A static page does
not qualify as the native online-demo bonus.

Workflow versions and minimal permissions follow [GitHub’s current Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), checked November 10. Deployment itself remains untested and gated.
