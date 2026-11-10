# v2 dev set, after tuning — full rerun not started

v2 is now development data. Its original labels and [historical evaluation](EVAL_HELDOUT.md) remain unchanged. No full three-repetition dev rerun was started because the new candidate failed its live core gate twice.

Two selected examples were used to inspect the mechanism before sealed access. They are not a representative accuracy estimate:

| Probe | HO-016: conflicting dispatch notes | HO-017: corrected product |
| --- | --- | --- |
| Prompt 1.4.0 | QUARANTINE; wrong exact route | REVIEW; malformed duplicate JSON keys |
| Prompt 1.4.1 | REQUEST_REVIEW; correct route, two quoted records | QUARANTINE; correct route, quoted buyer correction |

[First raw probe](../evidence/dev-prose-probe/), [second raw probe](../evidence/dev-prose-probe-final/), [diagnosis of all unstructured misses](EVAL_DIAGNOSIS.md).

The later prompt 1.4.2/final-format candidate did not pass the core entry point. No full-dev correct-route, wrong-delivery, false-hold, review-rate or timing result is available for it. No improvement over rules-only is claimed. Resume only after the live core is repaired, using the frozen protocol runner with `--dataset dev` and a separate new output directory. Never overwrite the original v2 run.
