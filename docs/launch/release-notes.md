# SilentShift 0.3.3 — prepared release notes

**Candidate only; not tagged, released or published.** The current public native/IPM/OEX version remains 0.3.2. The candidate manifest, Python project metadata and lockfile agree on 0.3.3; React remains separately built 0.2.1.

## Documentation and static evidence presentation

**No native code changes.** The native classes, agent, deterministic policy, Java/Python runtime sources, fixtures and install hooks are unchanged from 0.3.2.

- Put the existing recorded wrong-delivery/review trade-off and its accuracy limits at the front of the README, landing and evidence tour. No new evaluation was run.
- Add three source-linked prose examples showing the original clause, rule result, agent citation/recommendation and final policy hold. Pending review is not presented as a correct final route or a completed human decision.
- Provide a guided recorded evidence tour and a browser receipt inspector. The inspector checks a real saved payload/signature and detects an edited copy; signing-key identity and business correctness remain separate questions.
- Refresh the judge/install documentation and prepare a re-cut video script. Existing video and article links stay unchanged. These static recorded pages are not a hosted native demo.
- Keep the public keyless launcher pinned to its current 0.3.2 release until 0.3.3 is actually published and independently installed. The isolated local-archive verifier can exercise literal `zpm "install silentshift"`; it now explicitly checks the installed manifest identity against the inspected archive.

## Publication prerequisites

The 0.3.3 candidate must pass CI and a fresh-container install of its locally built archive before merge. Then separately approve the matching v0.3.3 tag/GitHub release and OEX/IPM publication. Type 0.3.3 manually; never use 1.0.0. After publication, download the registry archive, compare its manifest/tag identity and run a new fresh public install before claiming that gate passed.

Only IRIS 2026.3.0AI.154.0 Community / 154U ARM64 is locally qualified. Examples remain synthetic and downstream delivery is to a simulator. No new inference, accuracy improvement, hosted native demo, new-build qualification, awarded bonus or ranking is claimed.
