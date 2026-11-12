# Draft: bonus follow-up reply (NOT POSTED)

Where: https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows, reply under my 11 Nov claim (thread "Himanshu Kumar, to Tatiana Tikhonova").

Post only after the issues are filed. Replace `#EP1` and `#EP2` with the real numbers and delete any line whose action did not happen (for example the online demo).

---

Hi Tatiana, one more update for SilentShift's bonus review:

- Find a bug in Embedded Python (2 + 1), both reproduced in fresh containers on 2026.3.0AI build 154U ARM64 with a standalone class and script:
  - python-bugreports #EP1: an argument skipped in an ObjectScript call (`Py(,"Z")`) reaches a `[ Language = python ]` method as `None` instead of its declared default
  - python-bugreports #EP2: a class rejected by the compiler because of a Python method stays installed and its other methods still run, unlike the same failure in ObjectScript
- Online demo (2): <URL>, running the IRIS production in replay mode (recorded agent proposals, live IRIS policy and receipts; synthetic data, read-only, no API keys)

The README Contest bonuses table is updated with the same links. Thank you!
