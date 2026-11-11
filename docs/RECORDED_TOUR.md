# Follow two recorded native cases

The static tour at `docs/site/evidence-tour.html` presents two historical synthetic local-model cases from November 11. It preserves their real message/reference snapshots, model recommendation, policy checks, outcome, native session ID and Java PEX receipt. Opening it starts no IRIS process, performs no fresh inference and changes no case.

```sh
python3 -m http.server 5199 --bind 127.0.0.1 --directory docs/site
```

Open `http://127.0.0.1:5199/evidence-tour.html`. The unsupported order starts with the actual ALLOW proposal and the policy's quarantine. Select the approved amendment to inspect its different reference authority and delivered outcome. Use the four steps, arrow keys in the tabs, or Previous/Next. A copied URL preserves case/step across refresh. Receipt inspection carries the chosen case into the separate local verifier.

The source is [the historical native API run](evidence/bonus-claims-nov11/java-pex-native-five.json), with [matching Java exports](evidence/bonus-claims-nov11/java-pex-frozen-cases.json). This was an earlier source checkpoint, not a new inference run on the current main. The later missing-citation repeat failure and subsequent fix remain in their own records; this selection does not conceal or replace them. These demonstration cases establish neither overall model accuracy nor superiority over the rule baseline.

Regenerate the selection without running cases:

```sh
python3 scripts/build_recorded_tour.py
node --test tests/recorded-tour.test.mjs
node scripts/check_evidence_tour.cjs
```

Source hashes, exact field comparisons, matching case/outcome bindings and verification of both signatures guard against invented or silently edited evidence. Only the displayed subsets are selected; raw model traces are not presented as new observations. Public capture links retain their original run scope. Browser checks use an isolated local static server, never the native API.

Pages publication is separately gated. This read-only tour is a recorded evidence viewer, not a hosted native app or a newly earned online-demo bonus.

[Tour browser receipt](evidence/voting-nov11-tour/browser.json) records the local inspection checks and captures; it is not a new native run.
