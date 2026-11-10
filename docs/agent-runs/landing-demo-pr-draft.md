Judges currently need the video or a local licensed IRIS setup to understand
SilentShift. This adds a fast static product page with the concrete order example,
real native captures, an interactive evidence gallery, captioned video and the
existing keyless install path. GSAP motion respects OS reduced motion and a manual
pause; the product story remains readable without JavaScript.

The live-demo control explicitly reports that native hosting is unavailable. The
requested Crashcart host is x86_64 and the qualified image is ARM64 154U, so no
native hosting, emulation, resource change or replacement mockup was deployed.

## Validation

- [x] `uv run pytest -q` — 393 passed in 24.44s.
- [x] `npm --prefix web run check` and `npm --prefix web run build` passed.
- [x] Original disconnected workbench suites — 54 passed, unchanged assertions;
  temporary port 5207 preserved the owner's existing preview. Executed config and
  output are in `docs/evidence/landing-demo-nov10/`.
- [x] `node scripts/check_static_landing.cjs http://127.0.0.1:5197/` — 46/46:
  keyboard, clipboard, gallery, modal, reduced motion, responsive pin cleanup,
  no-JavaScript content and actual MP4/caption playback.
- [x] Latest local Lighthouse mobile **97/100/100/100** and desktop
  **100/100/100/100**. Order: performance/accessibility/best practices/SEO.
- [x] 163 existing runtime/package/workbench/launcher/front-door files match
  `9f3178e` byte-for-byte. No new native suite or build/architecture qualification.
- [x] Desktop/mobile screenshots and actual ~20s H.264 scroll recording prepared.

See `docs/agent-runs/landing-demo-nov10.md` and its linked receipts. The video,
orders and captures are synthetic/recorded; no accuracy advantage or awarded bonus
is claimed. The site's expected Pages address is currently 404 and is not a live
demo link. All other checked destinations resolve; OEX's public body still says
native 0.3.0 despite the visible 0.3.1 release. Its fields were not edited.

## Owner gates

- [ ] This PR's hosted CI after the approved push; then separate merge approval.
- [ ] Separate Pages approval: manual-only, main-only workflow; no push/PR deploy
  trigger. This PR alone does not enable or publish Pages.
- [ ] A compatible native hosting plan and separate deploy approval; current host
  is blocked. No monthly quote or public native viewer login is prepared.
- [ ] README/OEX live links only after verified publication, each at its own gate.
- [ ] Requested stale-branch deletions, each separately approved.

IPM/module.xml, v0.3.1, native runtime, policy, workbench source, Open Exchange and
articles are unchanged. No spending or EAP/model publication.
