# PR #4: required-variable false positive

GitGuardian extracted the literal `?Set` from the three password validation messages in the original `compose.judge.yaml`, commit `2fc57f7`, lines 7, 9 and 10. These were required-environment expressions, not embedded credentials. The incident grouped the same literal across ten template occurrences; all contexts were checked before classifying that one incident as **Not a secret (false positive)**. No other repository source was modified.

GitGuardian [scans every commit in a PR](https://docs.gitguardian.com/internal-monitoring/prevent/detect-secrets-in-real-time-in-github), so a later source edit alone does not remove a historical detection. Incident **38253018** is now **Ignored**, with the exact false-positive reason. No check was skipped, detector disabled, directory allowlisted, branch protection changed or Git history rewritten.

The current template uses `${VARIABLE:?}` for the same three required passwords. [Docker's required-value syntax](https://docs.docker.com/reference/compose-file/interpolation/) still rejects unset or empty values. The unchanged `docker/judge-prepare.py` requires three distinct private passwords, each at least twelve characters. No password default or example value was added.

Actual verification:

- Real Docker Compose configuration: valid values bind unchanged; unset and empty values for each password fail by variable name. **7/7** checks passed; no runtime resources or model calls. [Receipt](../evidence/gitguardian-pr4/compose-validation.json).
- `uv run pytest -q`: **393 passed in 21.78s**. [Output](../evidence/gitguardian-pr4/pytest.txt).
- [Triage/disposition receipt](../evidence/gitguardian-pr4/remediation.json). The final hosted result must be read from [PR #4](https://github.com/himanshu748/silentshift/pull/4) at its new head; this pre-push record does not assert that result.

The native classes, Python runtime assets, model/prompt, policy, package version and frozen fixtures are unchanged. Prior 154U native/live/replay receipts retain their original scope; no native-model rerun is implied. Main remains unmerged, and no package, OEX change, deployment or release is authorized by this fix.
