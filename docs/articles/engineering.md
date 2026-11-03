<!-- LOCAL DRAFT — NOT PUBLISHED. Public core source verified; native Workflow proof 43/43 in docs/evidence/workflow.json. Current extension changes and article remain local pending release review and separate publication authorization. -->

# A held transaction needs a review that survives failure

Holding a questionable transaction is only the start. The operator still needs to understand the evidence, record a decision and know whether the destination received it. If completion fails after the decision is saved, asking the operator to start again creates a second uncertainty.

SilentShift gives that review a native IRIS Workflow task. The original message, approved references, AI recommendation and deterministic policy stay with the investigation. The worklist owns the human task; the browser displays its persisted state.

The demonstration uses synthetic orders and payments. Delivery means a receipt in an IRIS destination simulator, with no real shipment or payment.

## Give a hold an owner

SilentShift catches changes in business meaning even when a message is technically valid. For example, `20 CASE` cannot replace an approved commitment of `240 EA` without approved conversion or amendment evidence. An effective amendment can make that same incoming value legitimate.

The native AI Hub agent investigates through four read-only, case-scoped tools. It recommends a decision. Embedded Python policy independently checks the evidence before IRIS chooses delivery, quarantine or review.

A new review or quarantine hold asks a separate native coordinator Business Process to create a task through `EnsLib.Workflow.Operation`. The task appears in the `ReviewWorklist` role. The demo configures one authorized reviewer; it does not claim a tested multi-user assignment scheme. The original processing request can finish while the human task waits durably.

The operator opens the reviewer-only Review view to see pending native tasks, then reads the case, references, precedent evidence, policy reasons and native task state together. Critical contradictions cannot be manually approved. A valid human decision requires reviewer permission, a reason, a current case version and an idempotency key.

## Separate a recorded decision from a completed route

The review API first checks policy and claims the native task for the authorized reviewer. It commits a review receipt containing the action, reason, identity, original case version and key. It then completes the native task and applies the permitted route.

If native completion fails after that commit, SilentShift returns an unavailable response and preserves `completion_pending`. The case stays held. The product offers **Resume recorded review**, reconstructing the exact request from its server-side receipt. The operator can inspect the reason but cannot silently change it into a different request.

A retry carries the original version, even when later workflow events have advanced the case version. IRIS recognizes the existing receipt, resumes completion and retains one destination receipt. A new key cannot replace an already committed native-task decision.

The native callback also checks reviewer authority and the matching committed receipt. Calling the Workflow action directly cannot bypass the application's policy.

## Test the interruption, then use the product to recover

We exercised a controlled completion failure on a new synthetic case. Its eleven-reference snapshot exceeded the model's evidence budget, so inference was skipped and the case entered review. The approved references were preserved for human inspection.

The test temporarily made that task's native deferred-response destination invalid. The review API returned HTTP 503 after committing the approval; the native task remained incomplete, the route stayed `REVIEW`, and there were zero delivery receipts. The original native token was restored immediately.

After reconnecting to the workbench, the persisted case offered its original review for resumption. The modal displayed the original version and locked reason. One click completed the native task and delivered once to the simulator. The first decision's identity, reason, version and key remained unchanged.

A separate conflicting-evidence case exercised rejection with zero deliveries, viewer denial, stale-version rejection and direct native-action denial. Its model request timed out safely; the receipt does not count that request as a successful native recommendation. The [43-check review evidence](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/workflow.json) separates this recovery experiment from the five-case model evaluation.

A later [54-check native worklist run](https://github.com/himanshu748/silentshift/blob/main/docs/evidence/review-queue.json) verified the pending-task API, rejection and two simultaneous identical approvals. Both approval requests returned 200 and produced one review receipt, one native completion response and one delivery. Separate workbench actions completed approval and rejection. The controlled failure above remains narrower evidence; recovery from every outage, crash or external destination failure is unverified.

## Try the same review journey

Follow the [native setup](https://github.com/himanshu748/silentshift/blob/main/README.md#native-build-154-setup) with an authorized Community AI Hub build 154 image and your own private configuration. Bootstrap installs the native worklist and coordinator without calling a model. The enclosing investigation wait is configurable from 10 through 120 seconds and defaults to 60; the tested constrained local 4B setup explicitly uses 120. Expiry keeps the case held and does not establish provider cancellation.

The focused verifier creates one new local-model conflict investigation and a separate no-model boundary case:

```sh
uv run python scripts/verify_native_workflow.py --allow-one-local-model-call
```

Use the explicit flag only with the documented local inference route. Inspect the investigation in the workbench, then compare its native worklist state, recorded decision and simulator receipt. The [source](https://github.com/himanshu748/silentshift/blob/main/src/SilentShift/Workflow) shows the native task lifecycle; the [build notes](https://github.com/himanshu748/silentshift/blob/main/docs/BUILD_STATUS.md) state the tested scope and remaining limits.

The operator can resume the recorded decision and inspect the one simulator receipt. The saved reason, version and key stay attached to that decision.
