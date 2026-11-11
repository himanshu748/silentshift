# Bonus review preparation — November 11, 2026 (IST)

## Scope and current state

Prepared from main `3bacc61c9f2a5acfa4c2d15ab21a2baab3df38c8` on local branch `chore/bonus-claims-nov11`. No runtime, policy, model, fixtures, package manifest, OEX fields or release metadata changed. The original worktree and the uncommitted landing refresh remain untouched.

Read the official [bonus post and its complete discussion](https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-interoperability-workflows). Staff ask for a registration-free video download. Entrants provide MP4 release assets followed by concise evidence links and a README bonus-table link. Staff are reviewing eligibility; acknowledgment is not an award. DPI-I-689 requires the README link, dedicated OEX field and a reproducible Visual Trace example; the comparison with Langfuse supports that review. Multiple entrants may implement the same idea.

[Current public/version/article/issue readback](../evidence/bonus-claims-nov11/public.json) · [read-only commands](../evidence/bonus-claims-nov11/commands.txt) · [MP4 proof](../evidence/bonus-claims-nov11/video.json) · [Embedded Python source audit](../evidence/bonus-claims-nov11/embedded-python.json).

The public OEX release is 0.3.1; its body still contains 0.3.0 wording. The dedicated DPI-I-689 association is visible. No listing edit was made. Issue #17 remains open without comments or labels. The organizer threads have no new qualification reply. The November 10 Dmitrij message explains the description update and future approval procedure; it does not confirm any bonus.

## Embedded Python decision

`src/SilentShift/Bridge.cls` defines `Assess` and `Policy` with `[Language = python]`. `src/SilentShift/Process/Semantic.cls` calls both inside the native business process. The methods import `silentshift.engine` in IRIS. Bridge, process and engine hashes equal the earlier live-qualified source. Historical native receipts establish execution; this docs-only pass does not rerun them.

The prior Not claimed status was an owner scope restriction, not a failed technical requirement. The explicit November 11 instruction changes **usage** to Claimed in README, BONUS_EVIDENCE and SUBMISSION_CHECKLIST. PEX, online demo and the separate Embedded Python bug remain Not claimed. Claimed means requested for review, never awarded.

## Video asset prepared, not uploaded

The existing file is `evidence/video/silentshift-demo.mp4`: 3,561,558 bytes, SHA-256 `9ad0e678ded827cf07dd087be936a8c2b168cacb7d07b3c7655357f6d91a5d7d`. The anonymous raw download returned HTTP 200 and matched the entire file. FFprobe reports 150.000 seconds, H.264 1920×1080, AAC and mov_text captions. It is the same earlier synthetic workflow recording linked on YouTube; it predates CSV.

Use the **existing** [v0.3.1 release](https://github.com/himanshu748/silentshift/releases/tag/v0.3.1), which currently has no assets. Adding one asset does not create a tag, change its release notes or publish IPM. Recheck that the asset name remains absent before executing; never use `--clobber`.

**Separate gated mutation, NOT EXECUTED:**

```sh
gh release upload v0.3.1 evidence/video/silentshift-demo.mp4 \
  --repo himanshu748/silentshift
```

Expected new URL, **not live yet**:

```text
https://github.com/himanshu748/silentshift/releases/download/v0.3.1/silentshift-demo.mp4
```

After that single authorized upload, verify with no cookies or authorization headers:

```sh
mkdir -p .local/bonus-review
curl --fail --location --proto '=https' --silent --show-error \
  --output .local/bonus-review/release-download.mp4 \
  --write-out 'HTTP %{http_code}; bytes %{size_download}\n' \
  https://github.com/himanshu748/silentshift/releases/download/v0.3.1/silentshift-demo.mp4
wc -c .local/bonus-review/release-download.mp4
shasum -a 256 .local/bonus-review/release-download.mp4
cmp evidence/video/silentshift-demo.mp4 .local/bonus-review/release-download.mp4
```

Expected: HTTP 200, 3,561,558 bytes, the SHA-256 above and successful `cmp`. Record the actual result; none of these release-asset download checks has run yet. The already-working raw MP4 remains the README link until that action is verified.

## Draft reply

[Exact DC reply](bonus-comment-draft-nov11.md), not posted. Its future release-asset URL is deliberately blocked until uploaded and verified. Use the prepared text only after a successful anonymous asset check; review any changed external state before requesting comment approval. Keep every factual claim tied to evidence. Do not post a broken proposed URL.

## Optional Java PEX plan

**Estimate: 6–10 focused engineering hours; medium-to-high release risk. Not started, not claimed.** This is an effort estimate, not measured implementation time. The [official PEX documentation](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=EPEX) is background; exact build-154 Java gateway/SDK compatibility must first be checked locally.

A useful minimal integration would be an `AuditExport` Java PEX business operation receiving the committed simulator receipt and decision evidence IDs from the actual production. It would export an immutable, bounded synthetic audit JSON to a dedicated operator-owned directory, using receipt ID as an idempotency key. It must run through the native Java PEX gateway and appear as request/response messages under the case trace; a standalone Java program or an unused class would not qualify.

Proposed work, only after a separate go-ahead:

1. Check the Java PEX SDK/JDK and ARM64 gateway shipped or supported with this legally loaded 154U build; prove one local gateway request before editing the production (1–2 hours).
2. Implement bounded export, atomic write and duplicate-content checking in Java; add the real production operation without granting it routing or release authority (2–3 hours).
3. Add a native test exercising delivered and held receipts, retry idempotency, and export failure without duplicate delivery. Build/run inside Docker; capture the trace (2–3 hours).
4. Run the native regression, replay and documentation checks; record the exact build and package/source boundary (1–2 hours).

Risks: gateway/JDK/image compatibility, additional production lifecycle/dependency, export retry semantics, and regression time during voting. No EAP image would be published. If the gateway spike fails twice, log it and stop. No implementation is authorized by this plan; preserve the existing core workflow first.

## Optional second AI Hub bug review

No additional filing-ready defect was established from `docs/DECISIONS.md`, BUILD_STATUS, the bug inventory and the recorded workaround history. The historical signal-11 callback failure has an application workaround but neither a standalone failing reproduction nor attribution to AI Hub versus Embedded Python. It must not be repackaged as a second AI Hub bug.

Other recorded mistakes were application API usage, iterator handling, HTTP-stream semantics, provider-option placement, short model deadlines or interpreting a test-runner return value. These are not evidence of a second vendor defect. [Existing inventory and exclusions](../bug-reports/README.md). Issue #17 remains the only bug claim; no duplicate or new issue is drafted for filing.

## Validation and review captures

The documentation link check resolved **370 relative file links with no missing targets**. All new JSON receipts parse, the verification script compiles, `git diff --check` passes, and the complete raw MP4 matches the existing source file. Both public article pages returned HTTP 200 with OEX backlinks. These are document/artifact checks, not renewed native or model tests.

- [Local claims and asset-plan screenshot](../evidence/bonus-claims-nov11/claims-preview.png)
- [Local exact-comment screenshot](../evidence/bonus-claims-nov11/comment-preview.png)
- [Validation receipt](../evidence/bonus-claims-nov11/validation.json)

The captures are local draft-review pages, not screenshots of a saved GitHub release or posted DC comment. No upload/form save was performed.

## Exact approval order

Every action needs a new exact `submit`; no approval has been consumed in this pass.

1. Push `chore/bonus-claims-nov11` and open one PR to main with the reviewed diff. **This is the next gate.** No PR URL exists yet.
2. Merge that PR after the required checks pass. Do not force-push or bypass checks.
3. Upload only the existing MP4 asset to v0.3.1, then perform the anonymous full download/hash check.
4. Post the one reviewed reply to Tatiana, only after its links work publicly.
5. Delete `imgbot` only after reviewing its ancestry and unique work; separate approval.
6. Delete `chore/ipm-030-judge-freeze-nov8` only after reviewing its ancestry and unique work; separate approval.
7. Delete `landing-demo-nov10` only after its public merge/ancestry is checked and the protected uncommitted local landing refresh is preserved; separate approval. Never delete a local worktree as part of a remote branch deletion.

The branches currently exist remotely; no deletion is prepared as a blind force operation. No package/OEX publication, email, questionnaire, model call, deployment or spend is included.
