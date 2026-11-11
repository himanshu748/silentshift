# Static judge-facing site

This folder is the static GitHub Pages artifact. The landing, recorded evidence tour and receipt inspector were deployed November 11 from main 7ae03be. This branch prepares the agent-value view and headline correction; it has not deployed them.

Everything is recorded synthetic evidence. There is no IRIS connection, fresh inference, evaluation run or hosted native demo. The new prose view copies existing held-out files and keeps pending Workflow tasks distinct from completed human review.

## Preview and check

From the repository root:

```sh
python3 scripts/build_agent_value.py --check
python3 -m http.server 5201 --bind 127.0.0.1 --directory docs/site
```

Then, with the repository web dependencies installed:

```sh
node --test tests/receipt-inspector.test.mjs tests/recorded-tour.test.mjs tests/agent-value.test.mjs
node scripts/check_static_landing.cjs http://127.0.0.1:5201/ .local/agent-value/landing-browser
node scripts/check_agent_value.cjs http://127.0.0.1:5201/ .local/agent-value/cases-browser
```

The presentation builder only reads frozen observations and produces static HTML/JSON/Markdown; it never invokes the evaluation runner or a native API. Source hashes and all three selected-case trials are retained. Fonts are self-hosted. Existing GSAP animation and reduced-motion behavior are retained; the new prose page works without JavaScript.

## Publication

Only `docs/site` goes to Pages. No source merge or push automatically deploys it; the workflow is manual. This task requires the owner's separate exact submit for merging and for Pages deployment. Preserve existing recorded-mode and honest-limit labels. Do not treat this page as an online native-demo bonus.
