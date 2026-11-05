# Build status

## Bug filed and OEX edits submitted — November 5, 2026

On the user’s explicit instruction, filed the reproduced quoted-method generator defect as [AI Hub issue #17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17), under `himanshu748`, after checking the 16 existing reports for a match. Readback confirmed the posted title/body and open state. Vendor confirmation and organizer qualification remain pending. [Filing receipt](evidence/ai-hub-bug-filed.json).

Saved the prepared product description in Open Exchange and used **Send for approval → Send edits**. The success confirmation was captured; after reload the full description matched and the checked contest/IPM options, dedicated DPI-I-689 URL, video and two article URLs persisted. Release **0.2.1** and native IPM **0.2.0** are unchanged. The owner view is **Awaiting Review**; anonymous retrieval still returned older copy. No new release, approval cancellation, article edit or questionnaire resubmission occurred. [Receipt and screenshot](evidence/oex-submitted-nov5.json).

Only documentation and publication receipts changed; the clean-clone/native/Python/web checks below remain the applicable runtime evidence. Staged text secret scan, receipt hashes, local links and whitespace checks passed; the confirmation screenshot was reviewed.

## Clean-clone judge path verified — November 5, 2026

A fresh remote clone of **960b6b6** followed both README command blocks with new local credentials and no provider keys. The public registry installed native **0.2.0** on official ARM64 Community **2026.3.0AI.154.0 / 154U** in a new container without mounts. Explicit setup and authenticated production health passed. The full native `%UnitTest` suite passed **5 classes / 12 methods**. Initial and repeated API replays each passed **12/12**, sessions **24** and **58** at port **52883**, with five provider pairs, four native tool reads and zero deliveries. [Commands and output](JUDGE_VERIFICATION.md) · [receipt and metadata](evidence/judge-clean-clone.json).

Fresh-clone Python: **174 passed in 8.66s**. Primary-checkout TypeScript and production build passed; Vite completed in **853 ms** with existing Lucide warnings. Application code, deterministic policy, app version **0.2.1** and native package **0.2.0** are unchanged. No fresh live inference, browser rerun or newer-build claim is made. The new test containers were stopped and retained; no cleanup was needed. This closes the earlier disk/check-out gate. Historical failures below remain dated evidence, not the current status.

OEX and DC were not edited, and no bug was filed. The public listing remains **0.2.1**, both articles are readable and SilentShift remains in contest 49. The dedicated idea association is still unconfirmed in anonymous retrieval; the owner moderation state was not refreshed. [Readback](evidence/freeze-public-readback-nov5.json). Organizer awards remain unconfirmed.

## Earlier stop — November 4, 2026

The resumed fresh clones verified the public IPM client permission correction, native **0.2.0** registry installation and explicit setup on **154U**. A sibling-clone gateway bind failed because that directory was not shared with Colima; the README prerequisite is corrected in **ed27019**. A new clone under the existing shared directory reached successful package install/setup, then stopped at the host disk floor before gateway creation. Full native tests and API replay did not complete. The user requested stopping; no more retries or cleanup were performed, and the two new test containers were stopped and retained. [Exact results](JUDGE_VERIFICATION.md).

Read-only checks confirmed CI **c92df33** passed and SilentShift remains on contest 49. OEX still serves the older recipe; no OEX/DC edit or bug submission was made. Source/workbench versions, deterministic policy and working app are unchanged.

## Earlier resumed verification: shared-directory prerequisite

The user resumed autonomous work. Clearing only inactive npx download caches recovered about 0.69 GiB and left the active cache entry intact. A new clean remote clone passed IPM-client loading with the documented installer permissions, public `install silentshift` at native version 0.2.0, and explicit production setup on 154U. Gateway creation then failed because this Colima profile shares only the existing project directory, not the sibling clone directory. No native test/replay pass is claimed for that attempt. The README now requires a shared clone location and checks VM visibility before creating configuration or containers. The next isolated clone will use that existing mount without changing/restarting the working VM.

## Earlier frozen-entry result — November 4, 2026

Four requested documentation/evidence gaps are closed locally: the minimal AI Hub bug reproduces on 154U with filing text; declared-build replay passes 12/12; public README idea/trace/Langfuse evidence is prominent; app 0.2.1/native IPM 0.2.0 and unconfirmed bonus states are consistent. OEX and DC were not edited.

**Clean-clone gate remains blocked after two attempts.** The first fresh clone reached pristine 154U but IPM could not read its mode-0600 installer. The README now adds `chmod 644` only for that public checksum-verified file. The fresh retry confirmed mode 0644 and private mode-0600 credentials, then stopped at the 1.8 GiB host disk floor before creating a container. No third attempt, new native-suite pass or clean-clone replay is claimed. [Exact commands, output, clone hashes and next step](JUDGE_VERIFICATION.md).

Repository validation: **174 Python tests passed in 4.87s**, TypeScript and production build passed (existing Lucide warnings), **38 desktop/mobile browser checks passed in 1.0m**. The retained public-registry instance passed new replay session **59**, then was stopped. Earlier five-case live and full native unit receipts remain historical evidence. User-authorized cache/test-container cleanup preserved credentials, source, models and active applications; host capacity remains the blocker.

## Frozen-entry verification: fresh-download permission gap — November 4, 2026

The first fresh GitHub clone reached a pristine build-154 container but failed before installing SilentShift: `fetch_ipm.py` produced the public installer at mode `0600`, Docker preserved UID 501, and IRIS reported `ERROR #5005: Cannot open file`. No clean-install pass is claimed for that attempt. The README now makes only the SHA-256-verified public installer readable (`chmod 644`); local `.env` credentials remain `0600`. This is a setup instruction correction, with no runtime feature change. One fresh retry remains; the first failed instance and logs are retained.

## Frozen-entry verification: consistent public copy — November 4, 2026

README, bonus evidence, submission checklist and the prepared OEX description now distinguish **app 0.2.1**, **native IPM 0.2.0** and verified **IRIS 2026.3.0AI.154.0 / 154U**. All organizer awards remain unconfirmed; the idea association and AI Hub bug filing remain pending; online demo, PEX and the unisolated Embedded Python candidate are Not claimed. Historical counts/versions remain explicitly historical. The judge-guide command now uses the same allowed container-name prefix and port as the README. OEX edits are prepared for the user only; neither OEX nor the two published articles was changed.

## Frozen-entry verification: public idea evidence — November 4, 2026

The README places DPI-I-689 immediately after the product introduction, with direct jumps to the native Body screenshot and fair Langfuse comparison. The keyless recipe now includes a fresh Git clone, generated private local credentials, explicit recorded-replay mode and public-registry install. It declares its preloaded licensed-image/Colima/storage prerequisites and distinguishes app 0.2.1 from native IPM 0.2.0. Dedicated OEX idea visibility and organizer qualification remain pending. No portal or article was edited. The exact fresh-clone run is the final verification step; no completion claim is made here.

## Frozen-entry verification: declared runtime — November 4, 2026

The retained public-registry instance reports **2026.3.0AI / Build 154U**, native package **0.2.0**. A new no-key judge replay passed **12/12**, session **59**: five provider pairs, four real native tool reads, `QUARANTINED`, zero deliveries, no fresh inference. [Command, exact runtime and metadata](evidence/freeze-build154-replay.json). This verifies the declared **2026.3.0AI.154.0** again; it is not the later fresh-clone test. No build 109 was run or added as supported.

## Frozen-entry verification: bug report — November 4, 2026

Re-ran the two minimal `%AI.Tool` classes in the existing build-154 container's development `USER` namespace, outside `SILENTSHIFT`. The camel-case control compiled (`SS_CAMEL_OK=1`); the quoted underscore method failed in generated `%Invoke` (`SS_UNDERSCORE_OK=0`, `MPP5376`, missing subscript). No inference, external key, application-class change or permission change was needed. [Exact transcript and paste-ready issue](bug-reports/ai-hub-quoted-tool-name.md). The contest criteria point to the dedicated `ai-hub-eap-bugreports` tracker. Filing and organizer qualification are pending; the agent did not submit it. No build-109 claim is made.

## Judge path and article clarification — November 4, 2026

The judge guide now leads with the verified no-key public-registry replay and accurately reports public IPM **0.2.0** installation, the full **5-class / 12-method** native suite and separate **5/5** live route evidence. Its older invocation-only trace receipt is explicitly distinguished from the later provider-message exports and native Body captures.

The tracing guide and published overview distinguish the current **192-token** agent request budget from the **700-token** provider-ingress ceiling. The existing article was updated in place with source links and the current companion URL; both a new signed-out Safari window and anonymous web retrieval show the correction. [Screenshot and receipt](evidence/article-clarification.json). No runtime class, model setting, historical measurement or package version changed.

Repository issue search and Open Exchange Issues both showed **0** issues; OEX Reviews showed **No reviews yet**. The preceding three GitHub CI runs passed; the run for **81d1ed4** was queued at this check, so no pass is claimed for it. Native/provider tests were not rerun for documentation corrections. The replay command's flags were checked through `--help`; recorded clean-install receipts support its expected results.

Validation passed for local/own-repository documentation links, source-to-documentation token limits, public-install receipt assertions, exact submitted article-source hash, screenshot hash and `git diff --check`. The known-pattern text scan found zero matches; the screenshot was visually reviewed.

## Signed-out listing check — November 4, 2026

The refreshed Open Exchange README and native Body image are now publicly visible in anonymous retrieval and a fresh Safari Private Browsing window. IPM install command, version **0.2.1**, video and article links remain present; native IPM stays **0.2.0**. The dedicated **Ideas to the app** section is still absent when signed out, although the owner view shows its correct DPI-I-689 URL. Listing edits remain **Awaiting Review** and contest 49 still lists SilentShift among 15 entries. [Readback and screenshot](evidence/public-visibility.json). No duplicate submission, release or approval cancellation was performed.

Reconciled stale registration/publication claims in the compliance and competitive-review documents, preserving dated historical observations. Local documentation links, JSON receipt validation, screenshot SHA-256 and `git diff --check` passed; the known-pattern text scan found zero matches. This changes documentation only; application/native tests were not repeated, and no new model call or runtime modification occurred.

## Native metadata screenshots — November 4, 2026

Captured the actual Visual Trace **Body** panel in Safari for success session **1667**, response header **1677** / body **1391**, and HTTP-400 diagnostic session **1807**, response header **1810** / body **1506**. Read-only inspection of both persisted cases passed; both remain quarantined with zero deliveries. No new provider call was made for the capture. [Images, exact values, commands and hashes](evidence/provider-body-captures.json).

The user-approved temporary `%Ens_MessageContent:USE` and SQL `SELECT` on `Ens.MessageHeader` were removed immediately after capture. Independent readback confirmed the exact original role resources, SELECT **0** and write **0**. Passwords, setup code, native package **0.2.0**, frontend **0.2.1** and deterministic policy are unchanged. This closes the native Body screenshot gap; listing moderation and organizer awards remain separate.

Documentation follow-up checks: **174 Python tests passed in 3.70s**, TypeScript check passed, production build passed (**724 ms**, existing Lucide warnings). Full native fresh-container results below are retained; no new five-case run is claimed for this evidence-only update.

Commit **1c3941b** was pushed to `main` and imported into Open Exchange. The description-only update was sent for approval successfully; the owner preview shows the new captures. Release **0.2.1** and IPM **0.2.0** remain unchanged. Anonymous retrieval still shows the previous description; public propagation remains pending. Contest 49 still lists SilentShift, now among 15 entries. [Publication receipt](evidence/trace-publication.json).

## Final pass and interactive UI — November 4, 2026

The native backend remains **0.2.0**, verified on official ARM64 Community **2026.3.0AI.154.0 (154U)**. Two new clean public installs used the literal **`install silentshift`** command. Each started the production and passed all **five native test classes / 12 methods**. Recorded replay passed **12/12**, session **24**, port 52823. The separate live install passed **5/5 final routes**, all four tools per case, sessions **30, 58, 86,113,141**, port 52833. One SDK warmup and one amendment embedding are disclosed separately from that five-case score. [Replay receipt](evidence/final-public-replay.json) · [live receipt](evidence/final-public-live.json).

The frontend is **0.2.1**: an interactive synthetic authority comparison and user-controlled stage walkthrough replace the screenshot-only hero; quick navigation supports ⌘K / Ctrl+K and full case IDs. Short detail transitions and reduced-motion behavior preserve the native workflows. **38** landing/disconnected checks and **16** connected checks passed; the final layout subset passed **6/6**. Python **174 passed in 5.74s**, final TypeScript/production build passed (Vite **1.69s**) with the existing Lucide directive warnings. [UI study and evidence](UI_REVIEW.md).

Both Developer Community articles are now publicly readable and link SilentShift on Open Exchange. Contest 49 still lists SilentShift. OEX 0.2.1 appears under Published releases and in anonymous retrieval; listing edits remain Awaiting Review. The dedicated idea association is saved/visible to the owner but absent from anonymous extraction. The approval request and contest flag were preserved. Public-registry installation is verified independently of listing moderation. The final shipping receipt is in FINAL_PASS_REPORT.md.

One valid-UDL AI Hub tool-name generator defect was reproduced locally without inference; a second historical signal-11 candidate has five log entries but no minimal isolated repro. Both are [drafts only](bug-reports/README.md). No bug bonus is claimed awarded. The EAP hosting terms explicitly exclude demonstrations; no public host was created. [Hosting decision](HOSTING_REVIEW.md).

The user approved removing only the failed stopped container `silentshift-bonus-load-final-20261104`, recovering about 854 MB. No volumes or successful test instances were removed. Saved source/evidence/models and the original production remain.

## Current bonus release — November 4, 2026

The verified target remains official ARM64 Community **2026.3.0AI.154.0 (Build 154U)**. Version **0.2.0** adds explicit provider metadata and recorded responses through the same native agent and queued operation. Replay performs no fresh inference and preserves the critical policy veto.

**Published and installed:** Open Exchange release 0.2.0 succeeded; public metadata/manifest returned 200. A fresh version-qualified community-registry install passed explicit production startup, all **five native test classes / 12 methods**, and API replay **12/12**, session **24**, zero deliveries. All **55** registry runtime/package files match the released source. [Receipt](evidence/bonus-020-registry-install.json). The README-backed description was separately sent for approval; SilentShift is still on contest 49.

**Live:** 5/5 final outcomes on sessions 1667, 1695, 1723, 1750, 1778; four tools per case and ten real local provider pairs. The new protocol-failure case in session 1807 records actual HTTP 400 and stays quarantined. Python **172 passed in 3.13s**, TypeScript/build passed; staged source scan had zero findings/omissions. [Live receipt](evidence/bonus-020-live.json) · [failure receipt](evidence/bonus-020-live-failure.json).

The first source-load test required two assertion-expression repairs, then the full suite and replay passed. A second source container was stopped after a disk-floor pause and a post-restart readiness failure; its unverified inspector refinement was removed. The later public-registry run above is an independent clean success. No files or volumes were deleted; local VM disk capacity grew from 16 to 20 GiB. No paid service, external model provider or EAP image publication was used.

The native message-body screenshot gap was closed in the later capture above; no password or permanent role change was made. Listing moderation and organizer awards remain separate from verification. Earlier 404/moderation-only observations below are historical.

## Submission package — November 4

Feature freeze retained: no application/runtime feature changes. The [2:30 MP4](../evidence/video/silentshift-demo.mp4) is verified at 1920×1080 / 30 fps, H.264 with AAC silence, burned-in captions, embedded English captions and [SRT](../evidence/video/silentshift-demo.srt). Size: 3,561,558 bytes; SHA and source crops are in its [manifest](../evidence/video/silentshift-demo.json). Full audio/video decoding, exact caption readback and decoded-frame inspection passed. Homebrew ffmpeg/ffprobe 9.0.2 repaired the earlier x265 loader mismatch. Python 172, TypeScript and the web build passed again; existing native gates below remain retained, with no new model calls for this documentation/media work.

The [demo](https://youtu.be/a4dOcqu89EA) is public; anonymous YouTube oEmbed returned HTTP 200, and the watch player exposed 1080p HD and English captions. [Open Exchange 0.1.0](https://openexchange.intersystems.com/package/SilentShift) is **sent for approval / awaiting review**, with contest and Package Manager selections saved. Both [overview](https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production) and [engineering](https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery) articles were submitted and revised in place; each remains **On moderation**. The contest Apply dialog requires a published app, so entry is not confirmed. Anonymous public IPM listing and manifest reads returned 404; public registry installation remains unverified. See the [ordered checklist](SUBMISSION_CHECKLIST.md) and [status receipt](evidence/submission-status.json).


The local operator journey catches semantic contradictions before the IRIS destination simulator accepts them. Native engineering evidence below is retained from November 3; the submission readback above is from November 4.

## Ordered sponsor extensions

| Step | Current verified state |
| --- | --- |
| 1. Provider traceability | **Passed.** Full native run `00d3f243-3532-4166-ab31-0ac05d3f1f39`:5/5 expected routes, native investigations and four actual provider calls per case. Ten transport contract checks passed. Actual local HTTP 400 failure remains held. Authenticated native Visual Trace screenshots and paired metadata are in [BONUS_EVIDENCE.md](BONUS_EVIDENCE.md). |
| 2. Native human review | **Passed.** Reviewer-only native task API/view, 54 queue/concurrency checks, actual UI approve/reject and native deferred responses. Full run `b5bc69f5-4823-47fe-8e44-f7af579f8f50` passed 5/5; all four held cases have tasks. [Gate](evidence/step2-gate.json). |
| 3. Case/amendment precedents | **Passed.** Native 384-dimensional VECTOR, actual resolved-case/amendment indexing, top 3 scoped search/fourth tool/UI and native misleading-precedent veto. Warmed serial run `fc12cbcf-c9fc-4813-8614-8ac944d6e8fd` passed 5/5. 172 Python / 32 disconnected / 16 native browser checks passed. Earlier timeout trials retained. [Gate](evidence/step3-gate.json). |
| 4. Custom inbound adapter | **Passed.** All 82 native contract/iterator/file assertions passed, including delivery, quarantine, ack-write recovery and replay. Four native tools per case; full run `a96c814e-0606-41a1-b469-10f1f94885a9` passed 5/5. Python 172, disconnected 32, native browser 16, TypeScript/build passed. [Gate](evidence/step4-gate.json). |
| 5. Clean IPM installation | **Passed locally.** Real `install LocalArchive/silentshift 0.1.0 -synchronous`, fresh official 154U, 43 classes / nine assets, no source mount, manager module origins and ten empty tables. After explicit setup, native run `07131314-9713-44ee-b2e1-72d36f777678` passed 5/5 final routes (4/5 model proposals), four tools per case. Registry publication/install remain unverified. [Gate](evidence/step5-gate.json). |

Final checks: **172 pytest tests**, TypeScript and web build, **32 disconnected/landing** and **16 connected desktop/mobile** browser checks passed. The clean IPM instance is stopped and retained after actual native Visual Trace capture; the original production is healthy. Model and embeddings are local only. Each feature has a milestone commit. The user subsequently authorized the prepared video, application and article workflow. Hosting and spending remain outside scope; moderation and registry acceptance are external gates.

On November 4, the verified source through `61b7278` was pushed and fast-forwarded onto public `main`. The current OEX approval request and earlier questionnaire receipt remain separate external states. Unknown cost/provider retries stay null. Synthetic fixed cases establish neither production readiness nor general AI accuracy uplift.

<details>
<summary>Earlier core and extension receipts, retained for provenance</summary>

Updated 2026-11-03 IST. **Core native verification and a fresh-volume five-scenario repeat passed. Overall release/submission is still in progress.**

## Observed checks

| Check | Result | Scope |
| --- | --- | --- |
| Python / Hypothesis | **135 passed** | Exact decimals, policy safety, metadata/build/redirect checks, read-only trace inspection, local embedding route/output validation |
| Full native run | **5/5 final outcomes; passed=true** | Run 20e7b28c-f317-4ad5-b585-49f19bd5e1e5, actual Community ARM64 Build 154U, Qwen3 4B, policy1.1 |
| Native model proposals | **4/5 correct, 5/5 schema-valid** | All five read message/contracts/related evidence; policy converted the model's unverified conflict quarantine to review |
| Fresh-volume installation | **Passed; 5/5 proposals and final outcomes** | Started with zero cases/evaluations; all 21 core classes compiled; run 0503b649-ee6f-495e-be37-166db508377c, traces 2/10/18/26/34 |
| Browser Scenario Lab | **Actual injection and delivery passed** | Approved amendment case D39226FC-D6B8-11F1-956F-F285F08CEB87, trace 42; opened persisted evidence/policy; distinct from benchmark cases |
| Safety / routes | **0/4 unsafe releases** | Quantity/currency/unsafe-output held; conflict reviewed; approved amendment delivered once |
| Duplicate / reviewer gate | Passed in actual native run | Replays retained case/receipt/count; reviewer could not release critical contradiction; evaluation matched server metrics |
| Agent latency | Mean 25,914.4 ms; p95 43,434 ms | Five synthetic cases, agent invocation only; not throughput/general performance evidence |
| Usage/cost | Session totals and billing cost null | Numeric final-response usage separate; no paid provider calls |
| Native access | **11/11 passed** | Anonymous 401, viewer review 403, critical reviewer release 403, strict JSON, numeric pagination |
| Native malformed reviews | **5/5 passed** | Invalid reason/key/version types rejected; held state unchanged |
| Review workflow | **3/3 rejection +4/4 approval/concurrency passed** | REJECTED state, blank reason 422, stale version 409, concurrent/repeat approval one simulator receipt; no model calls |
| Native Workflow Engine | **43/43 passed** | Task 80 rejected with zero deliveries; task 94 retained a committed review after real 503, resumed through actual UI and completed/delivered once. Native headers 114/134 prove deferred responses; original key repeat preserved version/receipt. Initial D model request timed out safely, separate from task proof. |
| Reference boundaries | **26/26 native assertions passed** | Eleven-approved/eleven-peer scopes; actual Partner/Semantic/Investigator headers, REVIEW, zero deliveries, model_invoked=false |
| Native traceability | **46/46 checks passed; 23 core classes compiled** | New C/session 52 delivered once; A/session 68 held with zero deliveries; session 84 evidence-limit skip made no model call. Actual headers/bodies/audit links verified; whole-Chat/tool scope only |
| Restart persistence | Six captured cases matched after container restart | Payloads/references/policies/audit prefixes retained; zero deliveries |
| Container recreation / rebootstrap | Passed; 16 cases +1 failed evaluation retained | Restored namespace mapping; all 21 core classes compiled |
| TypeScript / build | Passed after permission/null-metric repairs | Workbench source; no deployment claim |
| Connected Chromium | **10/10 passed in 21.8s**, 1440×960 and 390×844 | Real reads, seven routes, paired mobile values, case-selection navigation, reviewer veto/dialog, keyboard/reduced motion, memory-only auth |
| Disconnected Chromium | **20/20 passed in 21.8s** after Hallmark | Genuine unreachable upstream, all seven views and keyboard/mobile navigation |
| Public landing Chromium | **10/10 passed in 12.0s** | Zero API requests, real static proof assets, workbench CTA, keyboard focus, reduced motion and 320px layout; fresh non-author Hallmark review found one pending public-source link |
| Feedback questionnaire | **Submitted; official receipt observed** | User's stated views, verified technical facts and no publicity consent; bonus award remains unconfirmed |
| Hallmark UI review | Rendered seven routes; 35 captures; 0 FAIL / 0 REFLEX | One kept warning was a changing API-check clock. Fresh review found two residual eyebrows, now promoted to factual headings; targeted recapture pending |
| Secret scan / Git | Earlier staged scan passed; two local commits | Final diff/scan/milestone commit pending; no public repository |

## Native evidence

Ignored artifacts are under `evidence/native/`. Successful run `run-20e7b28c-f317-4ad5-b585-49f19bd5e1e5.json` is retained; `latest.json` may advance. Actual trace IDs were173,181,189,197,205. The fresh-volume run is `clean-install.json`, preceded by `clean-install-initial.json` proving zero cases/evaluations. Each benchmark's approved-amendment case has one receipt; its other four cases have zero. These benchmark cases have not been used for later review mutations. The sanitized [public summary](evidence/native-summary.json) preserves all four trial outcomes, including failures, with source-artifact hashes.

Failed trials remain preserved. The first complete4B run (`11b884ec-23ee-4ddc-8d31-a98192ab7e7f`) had five valid native proposals but3/5 final outcomes under policy1.0. A2B run had four returned proposals and one empty answer. Neither is presented as successful. The deterministic baseline solves all five frozen examples; this dataset demonstrates no AI accuracy uplift.

Scenario E injects a labeled hostile validator proposal after an actual native reply; the real native proposal is preserved. The destination is an IRIS simulator, not an ERP/bank.

## Runtime repairs and limits

- Official ARM64 Community 2026.3.0AI.154.0 was downloaded after explicit EAP acceptance and loaded as `silentshift-iris:2026.3.0AI.154.0`. The user approved deleting only the 3.2 GiB installer archive; it is gone. Runtime/source/models/evidence remain.
- Dedicated Colima profile/context `silentshift` / `colima-silentshift`; existing active Docker context preserved. VM 2 GiB, standalone Compose 5.6.1, gateway loopback 52773.
- Ollama 0.31.1, `qwen3-silentshift:4b-instruct`,8192-token context; earlier 1.7B alias retained. No paid provider, Docker cloud, purchase or billing change.
- Verified stream Business Service signature, underscore JSON property access, SQL NULL scope, numeric pagination and application-only SQL/Python grants. End users have no permanent DB/Python rights.
- Early Chat/callback runs logged signal 11 while audits nested Embedded Python. ObjectScript-only callback JSON/timestamps removed that boundary; later full native runs did not crash. This is observed application repair, not a vendor-confirmed defect/earned bug bonus.
- Six iterations/700 tokens per request, eight evidence reads, bounded content and a 60s process wait. Oversized reference snapshots fail before any model call; callback truncation cannot count as complete. Provider cancellation remains unverified.
- Policy 1.1 sends unverified model concerns to review while critical/invalid/duplicate cases stay quarantined. Authenticated human rejection is explicit, auditable and held.

## Remaining release gates

1. Dedicated landing page implemented and interaction-verified. Add its actual public source/setup link after repository publication. Native Workflow, custom file adapter, supporting vector retrieval and IPM package are under integration verification; their source alone does not establish bonus completion.
2. Network-loss/late-model recovery and repeated stochastic trials remain limits; no production readiness claim.
3. Final privacy/diff review, coherent local commit, public repository and remote CI.
4. Demo materials, actual Open Exchange application and separate contest confirmation. No deployment, YouTube publication, OEX application or contest entry is claimed.

The authenticated OEX Apply dialog showed no published application on this account. No separate pre-development registration was found; OEX publication/approval and contest application are separate. Rules/deadline and organizer clarification are in `CONTEST_COMPLIANCE.md`.

</details>
