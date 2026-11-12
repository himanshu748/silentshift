# AI Hub second-bug investigation

Updated 2026-11-12T21:06:57.474365+05:30. **One reportable candidate found: character-stream tool values are not transported according to their advertised schema.** Draft only, unfiled, bonus qualification pending.

## Boundaries

- Branch `research/aihub-bug2-nov12`, based on main `c4dca45c06c30235192057f6653442cdd71f762a` in a new local clone.
- Research began November 12 at 20:53:06 IST; four-hour upper bound November 13 at 00:53:06 IST. Stopped the hunt early once one standalone, repeatable, apparently non-duplicate defect was established.
- Only local Colima/IRIS containers ran. Network mode `none`, no published ports or source mounts. The optional fake provider runs on container loopback, makes no outgoing requests and performs no model inference.
- No SilentShift main changes, release, IPM/OEX edit, DC post, issue filing, push or PR. No cloud resource or unrelated application was accessed. Four task containers are stopped and retained; no container was deleted.

## Rules and existing claim

See [rules.md](rules.md). The designated tracker is `intersystems-community/ai-hub-eap-bugreports`; first reproducible bug is 2 points and second is +1, subject to review. SilentShift already has #17, quoted underscore method generation. New corrections belong on the bonus-results article, where Semion says he checks claims. No additional credit is assumed.

## Candidate decisions

| Candidate / probe | Observed result | Decision |
| --- | --- | --- |
| Character-stream return loses its contents | Advertised string; direct call reads the text; tool manager returns bookkeeping object; repeated 3/3 fresh containers | **Keep, high confidence**. Primary report in [issue.md](issue.md). |
| Character-stream argument is not decoded | Advertised string input reaches `data.Read()` as a scalar and fails with INVALID OREF; direct stream argument succeeds; repeated 3/3 | Include as related inbound symptom in the same stream-codec report, not a second bonus claim. |
| Agent path for stream return | Two local mock-provider HTTP requests; second request's tool message contains metadata, not the text | Corroborates the same defect; no claim about an actual model's inference. |
| Quoted underscore method compilation | Existing SilentShift report #17 | Excluded before probing; duplicate. |
| Missing/wrong primitive arguments; nested object supplied as string | Object accepted through Echo; existing input-validation defect #20 covers this family | Rejected as duplicate. |
| Omitted optional method parameters | Default integer 7 and string fallback preserved; 20 repeated calls stable | No bug. |
| Omitted query default | Initial SQL probe lacked `[ SqlProc ]`, a harness mistake. Corrected probe returned null for an absent parameter. Guide explicitly says query defaults are not applied | Rejected: documented limit, not vendor bug. |
| Unicode/emoji/RTL | Printed terminal output looked damaged, but native equality and lengths confirmed the exact round trip | Rejected: terminal rendering/encoding was not payload loss. See unicode control. |
| Empty string, null string input | Empty string round-tripped; null coerced to empty string | Not reported: not established as a defect distinct from documented/ObjectScript coercion or #20. |
| Long text | Exact 200000-character round trip | No bug within this tested size. No larger-size claim. |
| Nested dynamic object / mixed array / binary | Values round-tripped in the tested cases | No independent defect established. Schema validation is already covered by #20. |
| Repeat calls, concurrent managers, error recovery | 20 repeated optional calls; 4 concurrent local sessions × 10 text calls all passed; post-error text control passed | No observed state corruption in this bounded check. |
| Startup sharding diagnostic | The known startup message appeared on this image | Rejected as existing #1, not another report. |
| Unreachable providers, retries, timeouts, cancellation, error codes, malformed responses | Existing reports #5, #6, #9, #10 and #18 already cover adjacent error/timeout concerns | Not re-run or claimed as a new defect. Cancellation and malformed-response behavior were not newly tested. |
| Enum enforcement and repeated nested-class schema | Already-advertised schema validation and repeated-class reflection reports #20/#22 | Not pursued as a fresh claim. |

## Evidence

- [Minimal class](StreamTools.cls), [exact terminal input](repro.in), [fresh-container runner](run_repro.py).
- [Fresh reproduction receipt](outputs/fresh-reproduction.json): 3/3 independent fresh containers reproduced; class absent before every load; direct controls passed.
- Exact outputs: [run 1](outputs/fresh-1.txt), [run 2](outputs/fresh-2.txt), [run 3](outputs/fresh-3.txt).
- [Agent terminal output](outputs/agent-mock.txt), [actual mock requests](outputs/agent-mock-requests.jsonl), [loopback mock](mock_provider.py), [agent commands](agent-mock.in).
- [Edge controls](outputs/edge-controls.escaped.txt), [Unicode equality](outputs/unicode-control.txt), [concurrency receipt](outputs/concurrency.json).
- [Initial harness failures](outputs/probe-initial.escaped.txt) and [registration-corrected probe](outputs/probe-corrected.escaped.txt) are retained as raw diagnostics, not vendor-bug proof. Escaped text copies preserve their non-UTF-8 diagnostic bytes; the original byte-for-byte files remain local and Git-ignored. Their SQL messages contain native non-UTF-8 bytes; do not mistake diagnostic rendering for another Unicode bug.
- Private vendor-source inspection stayed outside Git at `/tmp/aihub-sdk-private-nov12.xml`; no vendor class was changed or bundled with this repro.

## Duplicate check

Current filing tracker snapshot: 27 open, 0 closed issues. Original EAP tracker: 12 open and 34 closed issues, excluding 2 pull requests. Available comments from 44 issue threads were fetched and searched. The current tracker list is in [issues-index.md](reference/issues-index.md), with [original issue list](reference/original-issues-index.md) and [search results](reference/duplicate-searches.json) alongside it. Full upstream source/body/comment snapshots remain local and Git-ignored; [their manifest](reference/snapshot-manifest.json) records sizes and hashes. No GlobalCharacter / GlobalBinary / stream-codec match was found. Broad searches have unrelated hits, all retained; no search is a guarantee against an unpublished vendor ticket.

Closest reports checked: #17 (name quoting), #20 (input validation), #22 (nested schema), original #18 (MCP JSON framing) and original #45 (provider stream callback visibility). The standalone no-argument outbound mismatch is distinct from those reports. Refresh duplicate checks immediately before an authorized filing.

## Next gates — none executed

1. File the exact [issue draft](issue.md) in the designated tracker, after an exact `submit`; read back the issue signed out.
2. Add the actual issue link as filed/review pending in the README bonus table, then push this branch and open a PR, after a separate exact `submit`. Do not merge main as part of this action.
3. Reply under the existing DC bonus-results claim with only this second AI Hub bug and its issue link, asking for +1 eligibility review, after a separate exact `submit`. Do not duplicate the prior Embedded Python/demo request.
