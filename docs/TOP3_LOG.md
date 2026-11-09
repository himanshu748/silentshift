# Voting-week work log

Work is confined to `push/top3`. Main, the registry, Open Exchange and the published video are unchanged. The owner approved the measured benchmark wording after reviewing the completed results, and the README was updated on this branch. The newer quality pass below supersedes earlier verification blockers without rewriting their history.

## New serialized quality pass — November 9, 2026 UTC

Following the owner's request to strengthen the entry, the completed benchmark, recovered storage and repaired property-test deadlines allowed a new quality pass with one IRIS instance at a time. The full Python suite passed **248 tests in 21.49 seconds**. Separate newly created **154U ARM64** source-loaded instances, without application mounts, passed **5 native classes / 12 methods**, two **12/12** keyless replays (sessions **24 / 58**) and **5/5** fresh local Ollama scenarios (sessions **30 / 58 / 86 / 113 / 141**). The rebuilt frontend passed **16** actual native read-only checks against that fresh live backend in **16.6 seconds**. The normal local app was restored and authenticated health returned HTTP **200**, production running. [Receipt, commands and executable snapshot](evidence/top3-quality.json). Earlier timing/OOM failures remain below; none is relabeled as a pass.

The anonymous contest/listing readback now shows **43** entries, release **0.3.0** and the dedicated DPI-I-689 association. The OEX body still contains legacy **0.2.0/source-only CSV** wording. A correction is prepared; no listing edit or message was sent. Organizer qualification remains unconfirmed. [Public readback](evidence/top3-public-review.json).

The owner explicitly approved the README's honest comparison: fewer wrong simulator deliveries, no overall accuracy improvement and no unstructured-routing improvement. The opening now leads with the operator's task, measured result and short judge path. The design/architecture documents were aligned with the actual multi-page UI and source-versus-package boundary. The new Developer Community article remains a draft, not a post.

The owner separately approved a **four-hour**, **2-vCPU / 8-GiB / 50-GiB** ARM AWS trial at an estimated **$0.31** base before tax/transfer. Credit coverage is unconfirmed. No GPU, larger instance or longer duration is approved. Preparation must finish before launch, and automatic termination remains required. [Fresh AWS price readback](evidence/top3-aws-trial-quote.json). Hosting is not yet verified and the online-demo bonus remains Not claimed.

## November 9, 2026 UTC

- Provider configuration and a bounded forwarding transport were added behind the existing native gateway. Configuration/protocol tests passed; the native suite passed in a clean source-loaded 154U instance. External OpenAI, Gemini and OpenRouter execution has not been verified. [Provider receipt](evidence/top3-provider-partial-nov9.json) and [configuration guide](PROVIDERS.md).
- Two native provider verification attempts stopped when the VM killed IRIS processes under memory pressure. The VM has 2 GiB of RAM; running additional IRIS instances alongside the benchmark exceeded it. The first stopped during unit testing, the second after the native suite while attempting the replay. No third provider gate was attempted. These are failed/incomplete gates, not replay passes. Logs are preserved privately; the second attempt's completed unit output is retained with the receipt.
- The frozen held-out run paused after 64 persisted investigations at its unchanged host-disk safety floor. Completed cases and rule results were retained. A resume encountered the frozen IRIS instance before any new model call. No completed case is rerun, no label is changed, and an incomplete dataset will not be reported as a complete benchmark. Other local IRIS instances were stopped to recover VM memory before restoring the same benchmark container. Infrastructure interruptions will remain in its receipt.
- With exact owner approval, the failed `silentshift-bonus-load-top3-replay` container and inactive OpenCode updater cache were removed after retaining logs. The benchmark container, source, models and unique evidence remain.
- The AWS connector rejected two read-only calls as unauthenticated. Work moved to the already-configured AWS CLI; no repeated connector attempts were made.
- The signed-in official EAP page explicitly says earlier 2026.3 builds were removed and offers Community 2027.1.0AI.109.0. No x64 154 archive was found locally. No new build was downloaded or claimed. The owner authorized using the already-loaded ARM64 154 image on an ARM-based AWS instance, copied directly without a registry.
- A monitoring-only $150 monthly AWS budget was created before compute. Its alerts are delayed estimates, not a spending stop. No compute resource or hosted demo has yet been verified. Deployment status and teardown instructions belong in [ONLINE_DEMO.md](ONLINE_DEMO.md).
- The owner requested explicit money confirmation before any further cost-bearing action. The smaller CPU option is prepared only. A four-hour trial and any longer hosting period need separate approval; no launch or resize occurs while that answer is pending.
- Lightsail and Vultr were checked read-only at the owner's request. Their selected plans are cheaper than the original compute proposal, but the inspected Ubuntu Lightsail blueprint and Vultr Intel plan do not establish an ARM-compatible runtime for our retained image. A smaller `t4g.large` ARM option was priced as well. No comparison request is treated as launch approval.
- A later host-disk guard stopped the benchmark after 109 retained investigations (the earlier progress view showed 108). The owner approved removal of the second stopped failed provider-test container after its logs and unit results were saved. The benchmark resumed in the same instance; no storage floor was relaxed.

The dataset labels were committed before any held-out execution. See [FROZEN.md](../fixtures/v2-heldout/FROZEN.md). The benchmark container retains the release's original provider code and prompt; provider changes in this branch are not loaded into that instance.

The teardown utility passed six isolated ownership/account/volume tests without contacting AWS. The complete Python suite then passed **248 tests in 9.08 seconds**. These are local test results, not a live teardown or deployment.

The resumed benchmark subsequently reached **114 / 144** before the same host-disk guard stopped it again. macOS swap storage occupied 6 GiB; approximately 1.4 GiB remained free. Further retries stopped. No additional deletion or storage-floor reduction was attempted. All results are retained and the incomplete run is explicitly documented in [EVAL_HELDOUT.md](EVAL_HELDOUT.md); no final comparison or agent-superiority claim is published. The benchmark instance is preserved for resumption after host space is available.

After stopping the paused evaluation instance and unloading its idle local model, the original workbench backend was restored and authenticated health returned HTTP 200 with `SilentShift.Production` running. The evaluation container and gateway remain stopped, with their state retained. No application source or model configuration was changed by this resource cleanup. The runner now writes its paused/resumed state to the manifest at the existing disk guard; this is a harness-only change, not another inference attempt.

## CoCo frontend preparation — November 9

The owner requested Snowflake CoCo / Cortex Code for the frontend remake. The official stable CLI **1.2.35** was installed and its version/help checked. The owner's correspondence confirms approval of a twelve-month free CoCo offer and activation of the existing account. No new subscription, card, warehouse or cloud workspace was created; no model-generation request has run.

An SSO-only local connection was prepared outside Git with the existing account, PUBLIC role, no password and no warehouse. Authentication returned Snowflake error **390190** (the account's SAML identity-provider configuration). The alternative browser-sync flow timed out before a signed-in browser session was available. Attempts stopped after these two failures. The existing account's native sign-in page is open for the owner; no password or access token is requested in chat. Once the owner signs in, the changed browser state can unblock account synchronization.

The local frontend preview was started and its existing landing and unauthenticated investigation view inspected in a real browser. No frontend implementation has changed yet. The review and proposed acceptance criteria are in [TOP3_FRONTEND_BRIEF.md](TOP3_FRONTEND_BRIEF.md). Native policy, frozen benchmark and public listings remain untouched.

### Authentication follow-up

The owner completed the Snowflake homepage sign-in, but the CLI's browser-sync flow still returned zero connections from a different browser session. Native OAuth was configured in a separate `silentshift-frontend` profile, leaving the other active CoCo session and its profile untouched. The automatic OAuth attempt timed out while Safari waited for authentication. No model call ran.

The CLI's manual OAuth handoff is now open in the same side browser used for the account login. That account-specific authorization endpoint requests a separate sign-in; the homepage session alone does not authenticate it. The username is filled in. The CLI's two-minute browser window expired before that sign-in completed, so a new authorization attempt must wait for the owner's completed account sign-in. The owner must enter the existing password on that page, never in chat. Repeated sync attempts have stopped. This is an authentication blocker, not a completed frontend remake. No warehouse, cloud workspace or paid resource was created.

Frontend preflight: TypeScript and the production build passed. The first browser suite could not launch because its cached headless executable had been removed. Restoring the matching official Playwright headless shell repaired the test setup; the unchanged frontend then passed **38 browser checks in 1.3 minutes**. These are disconnected/landing checks, not new native integration evidence or proof of a redesign. [Preflight receipt](evidence/top3-frontend-preflight-nov9.json).

### CoCo connected; unrestricted visual brief

The SilentShift OAuth connection subsequently authenticated: the native CoCo request returned HTTP 200. Completed generation usage identifies the selected mode as `auto`, resolving to `claude-opus-5-5`. No Snowflake warehouse, cloud workspace or infrastructure was started. Earlier authentication blockers above are history, not current connection status.

The owner explicitly requested a rebuild from the product description and actual integrations, without a prescribed palette or design recipe. The [frontend brief](TOP3_FRONTEND_BRIEF.md) now records that instruction. CoCo is working in a separate frontend copy containing no credentials, native runtime, frozen fixtures or private evidence. The first complete-rebuild pass saved nine frontend files, then reached its 35-iteration cap before the landing/styles were complete. It did not complete successfully, despite the CLI process returning exit code zero. A focused continuation supplies the saved component context and is restricted to completing the remaining four frontend files. No generated rebuild is called verified before review and tests.


The focused CoCo continuation completed successfully in ten iterations, finishing the landing page and three stylesheets. The API client, schemas, dependencies and Vite configuration remained byte-identical. The generated component tree passed TypeScript and the production build. Integration review also found and repaired two responsive presentation defects: narrow screens hid the connection-status badge, and laptop-width navigation overlapped the session tools. Reduced motion now disables transitions and animations rather than shortening them.

Browser verification exposed old layout selectors after the rebuild; their assertions were migrated to the new responsive value ledgers, accessible regions and actual navigation controls without dropping native-record or review-veto checks. The first native browser attempt stopped on those stale selectors. A subsequent concurrent browser run passed all eight desktop native checks and the first two mobile checks, then stopped on API/test timeouts. The parallel disconnected run also had action timeouts. No timeout is reported as a product pass. With those suites stopped, a direct authenticated read returned health in 0.217 seconds and the first case page in 0.335 seconds; both returned HTTP 200. Further verification is serialized to avoid repeating the contended run. The initial mobile status-visibility failure was a real UI issue and was fixed, not hidden by removing an assertion.


The Python full-suite check failed twice on Hypothesis's incidental 200 ms wall-clock deadline: first two Decimal properties (395.83/267.75 ms initially versus 0.23/0.64 ms on replay), then the critical-release property (262.06 ms versus 0.29 ms on replay). All reported failures were timing-only `FlakyFailure` results; their functional assertions succeeded on replay. The first run had 246 passes and the second 247 passes. The two-run full-suite limit is retained: no third full-suite attempt is made in this pass. The property-test harness now consistently disables wall-clock deadlines for its correctness properties, keeping the generation strategies, example limits and assertions, including the critical-release veto, unchanged. A separate focused engine-module verification checks that harness repair. Production policy and arithmetic code are untouched.

### Verified frontend checkpoint

The focused engine module passed **71 tests in 4.66 seconds** after the harness repair. The rebuilt frontend passed TypeScript/build, **42** serialized landing/offline/session browser checks and **16** serialized native read-only browser checks. The CSV workbench passed **32** live checks with fresh local-model cases and traces **3256 / 3284**: quarantine with no delivery, and delivery with one receipt. The five fresh native scenarios also passed **5/5**, all with actual native AI Hub execution and the four evidence-tool reads, traces **3311 / 3339 / 3367 / 3394 / 3422**. No policy, provider behavior, schema or runtime code was changed to get these results.

Source is committed as `7b8b17087f4d2c43b47a16e4a5aafbc55f494118`; the separate timing-harness repair is `7d7c235`. [Machine-readable receipt and exact scope](evidence/top3-coco-frontend.json). Curated desktop/mobile captures show the new UI reading actual persisted synthetic IRIS records, and the labeled landing illustration. Full-suite Python follow-up remains explicitly unverified after the repair. Native `%UnitTest` and clean-install claims retain their earlier scope.

The separate owner-authorized disk-cleanup chat preserved the exact paused held-out container/gateway pair after coordination, along with the running app, volumes, images, models and evidence. Historical stopped test copies were removed there; no container was deleted by this frontend work. The frozen benchmark inputs and their labels remain untouched.

### Held-out comparison completed

The retained ARM64 154U release instance completed all **144** investigations: **48** per trial, with **139** returned agent results and **5** failed attempts retained. The final resume preserved all **114** earlier raw records byte-for-byte and checked every persisted order and reference snapshot against the frozen inputs. Labels, model, prompt and shipped policy were unchanged. [Coverage](../evidence/heldout/coverage.json), [integrity receipt](../evidence/heldout/verification.json), [resume output](../evidence/heldout/resume-output.txt) and [report output](../evidence/heldout/report-output.txt). The earlier blocked report/coverage receipt remains as [history](../evidence/heldout/coverage-paused-114.json). The four metric-harness tests passed in **1.29 seconds**.

Rules-only scored **33/48** correct routes. Agent-only scored **35/48**, **34/48** and **31/48**; agent + policy scored **33/48**, **33/48** and **30/48**. The shipped arm had **2**, **3** and **3** actual wrong simulator deliveries, compared with **6** counterfactual bad-order release recommendations from the baseline. Agent + policy **does not beat rules-only on correct routes in the unstructured split**: both achieved **1/16** in every trial. The shipped arm pooled **30/75** false holds versus the baseline's **9/25**; this is not an overall correct-routing improvement. Missing durations and failed invocations remain visible, and constrained-host transport failures limit interpretation. Every failure and case where rules won appears in [EVAL_HELDOUT.md](EVAL_HELDOUT.md).

The comparison concerns the frozen release implementation, not the later configurable-provider branch. It is a synthetic, implementation-aware challenge set, not independent customer-data validation. No README, listing, release, infrastructure or paid-provider change follows from these results. Public-facing benchmark wording waits for the owner's approval. The separate multi-page UI request is continuing without changing benchmark inputs or native behavior.

### Multi-page follow-up completed

The owner requested multiple pages and asked whether `AGENTS.md` imposed a single-page restriction. Both applicable instruction files were checked; neither did. No global or repository instruction file was edited. CoCo received the product/integration brief without a prescribed palette or layout and generated **6** HTML entry points. One preparatory invocation was stopped after reads to restrict the tool catalog; its private log remains. The restricted generation completed successfully in **26** iterations with only local read/write/edit/grep/glob tools, Auto resolving to `claude-opus-5-5`. No warehouse, cloud workspace or new infrastructure was created.

Review retained the critical-release veto and simulator/synthetic limits, pointed setup at the single installation guide and clarified the currency example: numeric equivalence does not authorize an interface representation change. The first browser run had **50** passes and **2** failures: a real footer badge overflow at **320px**, and a test locator that continued looking for Open after the menu changed its label to Close. The badge now wraps, the locator follows both accessible states, and all assertions remain.

Committed source `252bdd62ac60a1088320586cfc71e766766c0fb5` passed TypeScript/build, **54** browser checks, **16** native read-only browser checks and **12** production-build document journeys on a plain static server. The fresh CSV run passed **32** checks, with native traces **3451 / 3479**. The fresh live native run passed **5/5**, traces **3506 / 3534 / 3562 / 3589 / 3617**. The temporary static server was stopped; the normal working production and frontend preview remain running. [Complete scope and receipts](evidence/top3-multipage.json).

Backend/runtime and deterministic policy were untouched by this UI follow-up. Main and all public releases remain unchanged. No new full Python, clean-install or native `%UnitTest` pass is claimed. The original full-Python stop condition, provider replay limits, cost-approval gate and owner approval before README/listing benchmark wording remain in force.


### Four-hour trial authorization and local demo boundary

The owner approved the smaller ARM CPU trial: two vCPUs, eight GiB RAM, fifty GiB disk, four hours, estimated $0.31 base before tax/transfer. Credit coverage remains unconfirmed. No longer hosting, GPU or resize is authorized. The locally exported official 154 ARM image and exact Qwen/minilm manifests have private hashes; no proprietary image is uploaded to a registry.

The new loopback demo gateway passed 30 fake-upstream boundary tests in 12.32 seconds after adding finite-expiry and exact-path checks. The first test invocation failed collection on a decorator typo; that output remains private. Native reader setup initially raced IRIS startup, then exposed an ObjectScript terminal-loop syntax error; an unrolled role configuration completed. A scoped SELECT grant is necessary for SQL-backed case reads. Native viewer review/import actions remain forbidden.

Two local guided samples reached the real native production: quantity mismatch was quarantined with zero simulator deliveries (trace 170); approved amendment delivered once (trace 198). The gateway was restarted during the second attempt, correctly retaining it as uncertain and refusing redispatch. The operator reconciled the one persisted native case by exact correlation ID using reads only; its gateway wall time is unavailable, not a measured latency. No investigation was repeated. Reset retained native history.

Printable Visual Trace rendered its actual provider request/response hops through the read-only principal. The interactive Production Configuration page did not render: after its initial missing READ privilege was corrected, the restricted gateway still refused encoded SVG and HyperEvent broker requests. After two failed render attempts, further portal expansion stopped. The demo links production status in the workbench and native printable Visual Trace; it does not claim a working interactive Production Configuration page or reviewer task access.


### Timed AWS trial launched

The explicitly approved `t4g.large` trial launched at 13:13:47 UTC on November 9. The absolute timer was read back active for 17:13:47 UTC, AWS instance-initiated shutdown is `terminate`, the encrypted root disk deletes with the instance, and standard CPU credits are confirmed. Public application ingress stays closed during installation. The monitoring budget is an alert, not a cap. [Launch/control receipt](evidence/top3-aws-trial-launch.json).

The sequential direct image transfer was too slow; its partial archive was retained. A first chunk-upload invocation started before its local manifest finished and exited before copying any chunk; that operator sequencing failure is retained privately. Once the manifest existed, four bounded transfer workers started. The original image/model archives are unchanged and will be hash-checked on the host. This transfer change does not extend the termination timer or authorize a larger instance.


### Main documentation integrated without rewriting frozen history

Remote main advanced to `a10de3f61e1d809b374832a4db67761318bc16ea` with a README-only plain-English judge path. It was merged into `push/top3`, preserving that shorter setup and the owner's approved three-line held-out result, new source screenshot and explicit public-package/source boundaries. No native code changed, and label-first evaluation commits were not rebased or rewritten. Local main was not advanced or pushed.


### Owner-approved eight-hour trial bound

After the slow upload was measured, the owner explicitly approved eight hours total, estimated $0.62 base before tax/transfer. The absolute timer now ends no later than 21:13:47 UTC on November 9 / 02:43:47 IST on November 10, with a separate shutdown scheduled earlier. No larger machine or hosting through November 20 is authorized. [Approval/control receipt](evidence/top3-aws-trial-extension.json).

Four complete chunks were verified against their original hashes. The resume harness initially treated an already-complete destination as an SFTP failure; the complete files were read and hash-checked, then excluded from the remaining queue. The bounded worker retains partial files, cancels its owned processes on failure and stops admissions before the approved deadline. No data label, image content or model manifest changed. The operator embedding base was corrected before deployment from an endpoint path to the base URL the existing validator requires. The native installer remains pending transfer completion; no live cloud result is claimed.

[The final source-footprint receipt](evidence/top3-final-source.json) confirms all 59 native package source files still match the fresh quality-gate snapshot byte-for-byte. The new edge gateway and operator setup have only the explicitly named local/host checks; this does not turn them into previously qualified native source.


### Cloud attempt closed; source work continues to draft PR

The bounded resumable worker failed again with `Timeout, server … not responding`. Under the two-failure stop rule, no further transfer or cloud-deployment retry was attempted. The receiver still had only 4 of 60 chunks hash-verified, so native installation had not started. Its status/journal were saved, the waiting receiver was stopped, and the exact tagged trial was terminated early. AWS readback confirms the instance terminated and its root volume, security group and key pair are absent. The budget alert remains; actual billed cost and credit coverage are not yet established. [Closure receipt](evidence/top3-aws-trial-result.json).

No public application port was opened, no cloud model investigation ran, and there is no verified live demo URL. Printable trace and two guided cases remain local evidence only. Hosting through November 20, a larger CPU/GPU or another trial requires a new cost approval. The local source, original image/model bundles, benchmark results and unique logs remain protected. No image was pushed to a registry.

The final full Python run passed **286 tests in 18.88 seconds**, including eight approval/timer cases. [Output](evidence/top3-final-pytest.txt). The operator installer is prepared and plan/compile-tested, not end-to-end cloud-qualified. Its pure timer tests do not substitute for deployment evidence. The README retains no-hosted-demo wording and now makes the removed build-154 download prerequisite explicit. None of the 59 native package source files changed after the qualified native snapshot. The separate demo gateway retains its own local-only qualification.


### Prose repair and sealed-evaluation preparation — November 9 UTC

This branch now intentionally changes native source; the earlier unchanged-source statements describe the d1d752c checkpoint only. v3 labels and their digest were committed at 9c8d937 before inspecting v2 failures; the sealed case file remains unopened during diagnosis. v2 is the development set and its original labels and raw historical runs remain unchanged.

The diagnosis separates missing authority to release a baseline hold, model interpretation errors, and the old policy's unconditional downgrade of model-only quarantine concerns. New quotation validation grants containment only, never release. Quotation provenance is not semantic entailment. Multi-record prose concerns require review. The probe receipts retain both the unsuccessful early response format and the later observed mechanism.

Verification history is retained rather than overwritten: the first native test attempt failed on an unsupported AssertFalse macro in the new test, then passed after using AssertTrue with negation. A private continuation helper first failed import before any native action; after that was corrected, the native suite passed but an optional SDK probe copy failed because its destination directory had not been created. That continuation path was stopped; the already completed amendment-index evidence was retained and the separate five-case API command passed. No failed attempt was counted as a pass.

On the subsequent fresh replay instance, the new citation projection test failed because SaveCase correctly refused to mutate immutable references. The test now uses real scoped catalog insertion and SnapshotReferences. The second attempt passed the suite and two separate keyless API replays. These were test-harness repairs, not relaxed runtime checks. All original failed logs remain private; no provider secrets are in repository evidence.

No new AWS resource, upload or paid provider call has been authorized or executed in this pass. The eight-hour trial is closed. The proposed private S3 transfer, ARM-compatible compute choice, $60 budget alert and longer hosting remain behind a fresh cost approval after the sealed result is reported.


### Two failed live core gates; sealed set remains unopened

The prompt 1.4.1 core gate failed because approved-amendment ALLOW was malformed JSON and the fail-closed policy correctly kept it in review. A local protocol experiment found that global structured output prevented tool selection; a final-only structured request worked in a toy protocol test. The new native final-format integration then passed the operator-run native suite and two keyless replays, but its fresh live core gate failed before provider trace pairs were created. The service-role SQL read added in Lease.ShapeFinal has no matching AuditEvent SELECT grant in the transport role's setup; this is a likely integration defect, not a confirmed vendor issue.

Two failed live gates are saved, not overwritten. Repair/model attempts stopped under the owner's rule. No further runtime code or permissions were changed. v3 remains unopened and unrun; the full v2 rerun is also unrun. No sealed score, improvement claim, live demo, spending or external publication followed. [Complete blocked status](EVAL_SEALED.md) and [machine-readable receipt](evidence/prose-repair-status.json).

The repaired source remains local on push/top3. Main, the remote draft PR, IPM, OEX, articles and videos were not updated in this pass. Earlier uncommitted landing/session copy, browser tests and the README anchor cleanup remain outside these commits and are preserved.
