# Final contest pass — November 4, 2026

The native backend remains public IPM **0.2.0** on official ARM64 **2026.3.0AI.154.0 (154U)**. The interactive frontend is **0.2.1**. No native runtime class, model or deterministic policy changed. The accepted 2027.1.0AI.109.0 Community build was not tested.

## Fresh public installs

These commands ran from the repository root. The pinned IPM client and authorized official image were already available. Each new container began without a SILENTSHIFT namespace or source mounts, used the public community registry and explicitly started the installed production. Existing runtimes were preserved. The helper runs native `%UnitTest.Manager.RunTest` and inspects individual assertion/class results, rather than treating its status return alone as success.

```sh
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest \
  --container silentshift-bonus-registry-final-replay-20261104 --api-port 52823 --execute
```

Selected exact output:

```text
IPM install silentshift
[SILENTSHIFT|silentshift] Compile SUCCESS
[SILENTSHIFT|silentshift] Activate SUCCESS
All PASSED
SS_UNIT_RESULT=1
SS_UNIT_OK
execution_mode=recorded-replay; fresh_inference=false
case_id=D543CD3F-D828-11F1-9BF4-5511A76931C1; session_id=24
visual_trace_url=http://127.0.0.1:52823/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID=24
provider_pairs=5; four_tools=1_each; routing=QUARANTINED; delivery_count=0
checks=12/12; passed=true
```

Full suite: **five native classes / 12 test methods passed**. [Sanitized receipt, pass lines, native paired headers and actual metadata](evidence/final-public-replay.json). The replay container and its gateway were stopped after this successful run to free memory for the live check; they remain retained. The URL becomes available when those retained resources are started. Replay performs no fresh inference.

```sh
uv run python scripts/verify_bonus_release.py --source public-registry --install-latest \
  --execution-mode live --allow-model-calls \
  --container silentshift-bonus-registry-final-live-20261104 --api-port 52833 --execute
```

Selected exact output:

```text
IPM install silentshift
All PASSED
SS_UNIT_RESULT=1
SS_UNIT_OK
quantity-mismatch: policy=QUARANTINE route=QUARANTINED native=True
currency-scaling: policy=QUARANTINE route=QUARANTINED native=True
approved-amendment: policy=ALLOW route=DELIVERED native=True
conflicting-references: policy=REQUEST_REVIEW route=REVIEW native=True
unsafe-agent-output: policy=QUARANTINE route=QUARANTINED native=True
```

Full suite: **five native classes / 12 test methods passed**. Native final outcomes **5/5**, four actual evidence tools per case; sessions **30, 58, 86, 113, 141**. Only the approved amendment has one simulator delivery. Preparation made one approved-amendment local embedding and one real SDK warmup call, excluded from the five-case score. All inference used local `qwen3-silentshift:4b-instruct`; embeddings used local `all-minilm:22m`. [Live receipt and per-case checks](evidence/final-public-live.json). No paid provider was used. These fixed synthetic scenarios do not establish general accuracy or production readiness.

## Interface and local checks

The landing page has an explicitly synthetic contract comparison, two evidence states, four selectable stages and a bounded, user-initiated walkthrough. The workbench adds keyboard navigation and short detail transitions, with reduced motion and the existing native review safety preserved. Public Hookdeck, n8n and Langfuse product/documentation patterns informed the design. [Study, screenshots and limits](UI_REVIEW.md).

| Command | Observed result |
| --- | --- |
| `uv run pytest -q` | `174 passed in 5.74s` |
| `npm --prefix web run test:e2e` | `38 passed (1.1m)`; desktop/mobile, disconnected API, 320px, keyboard, motion |
| `SILENTSHIFT_NATIVE_E2E=1 uv run --env-file .env npm --prefix web run test:e2e:native` | `16 passed (1.7m)` final repeat; actual API reads, no scenario/review mutations |
| `npm --prefix web run test:e2e -- --grep 'public landing and section\|illustrated decision\|reduced motion keeps'` | `6 passed (17.7s)` final landing layout subset |
| `SILENTSHIFT_NATIVE_E2E=1 uv run --env-file .env npm --prefix web run test:e2e:native -- --grep 'Review worklist'` | `2 passed (16.4s)` after modal-stacking guard |
| `npm --prefix web run build` | TypeScript and build passed; Vite `built in 1.69s`; existing Lucide directive warnings |

The unreachable proxy errors in disconnected tests are intentional failure-state coverage. They are not native execution evidence. No extra UI library or remote model service was introduced.

## Listing, articles and hosting

OEX release **0.2.1** appears under **Published releases (3)** with the prepared notes. Its refreshed README/version are also visible in anonymous web retrieval. The owner view retains **Awaiting Review** for listing edits. Submit to Contest and Publish in Package Manager remained checked; the dedicated DPI-I-689 field and YouTube `a4dOcqu89EA` remained saved. Both article URLs were added to their dedicated fields. No Cancel approval or Unpublish action was taken. The dedicated idea association is visible in the owner preview but absent from the anonymous extract, so its public-field readback remains pending. SilentShift was confirmed among **13 registered applications** on contest 49 after the update.

Both [semantic-validation](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [recoverable-review](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery) articles are publicly readable and each links the Open Exchange application. The overview's 700-token passage describes its older recorded setup; the current prompt uses 192, so an author clarification remains useful. No duplicate post was created.

There is **no hosted demo**. The displayed EAP kit agreement limits internal evaluation and excludes demonstrations; general repository terms do not establish an exception. Hosting stopped at that gate. No host/card/spending was created. [Primary sources and decision](HOSTING_REVIEW.md).

## Unfiled defects and manual work

- [Quoted underscore tool dispatch](bug-reports/ai-hub-quoted-tool-name.md): valid minimal UDL reproduced a generated-code failure on 154U, with a successful camel-case control. Ready for author review/filing; vendor acceptance unconfirmed.
- [Callback signal 11 candidate](bug-reports/callback-signal11-candidate.md): five historical log entries and the application workaround are preserved, but there is no isolated minimal repro or stack attribution. Investigate before filing; no Embedded Python bug bonus claimed.
- Organizer/moderator approval and bonus awards remain external decisions. A native metadata Body-panel screenshot still requires an account allowed to view that panel. Existing graph capture and body exports are distinguished.
- Both articles and the video are public. The earlier questionnaire has its receipt; no new questionnaire submission is required. Personal eligibility is for the entrant to confirm.

## Shipping receipt

- **770baab** — `feat: add interactive product walkthrough and verify contest evidence`; pushed to `origin/main`. Remote `refs/heads/main` read back as `770baabd2c5e317918003dde05986eed476a75ef` before this documentation receipt.
- Open Exchange frontend/product **0.2.1**: submission success observed; listed under Published releases, three releases total. The listing still has **Awaiting Review**. [Success confirmation](assets/oex-021-approval-submitted.jpg) · [release readback](assets/oex-021-release-readback.jpg).
- Public IPM **0.2.0**: post-update anonymous metadata returned HTTP 200, unchanged reported artifact hash `198fc630f90cf990481dd93f64946e34596e1018`, size 7,914,399 bytes. No new native package publication is claimed. [Final publication receipt](evidence/final-publication.json).
- Contest 49: SilentShift remained registered after the update. Latest bonus award counts are organizer decisions, not inferred from local verification.
- The initial browser connection failed twice and work paused; the user resumed work, access recovered and submission succeeded. This was not a moderation rejection.

The final Python repeat returned `174 passed in 22.55s`. The staged known-pattern secret scan found **0** findings, with **three image files omitted** in the implementation commit. Those synthetic UI screenshots were inspected visually. The two later publication screenshots contain public listing data and were also inspected visually; automated binary/unknown-format coverage is not claimed. No credentials, environment files or runtime binaries are staged.
