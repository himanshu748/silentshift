# Native AI Hub integration evidence

Current November 4 live run passed 5/5 with four tools; sessions 1667, 1695, 1723, 1750 and 1778. A new actual HTTP-400 diagnostic is session 1807. [Current live metadata](evidence/bonus-020-live.json) · [current failure](evidence/bonus-020-live-failure.json). No-key replay and exact field boundaries are documented below.

Historical November 3 status: **the local provider-traced native journey passed all five scenarios on official ARM64 build 154U**, run `5bdbcc9c-2eb8-4d05-9a72-2f38299a4cc8`. Each `qwen3-silentshift:4b-instruct` investigation made four gateway requests, executed the three evidence tools, and persisted the expected policy/route. Approved amendment case `EB3307BB-D772-11F1-82EF-EED820A70F55` is native session 374; its four actual provider request/response pairs are headers 381–388. An isolated local SDK failure preserved upstream HTTP 400 in session 316, headers 318 ↔ 319, and remained held with zero deliveries. These are synthetic local cases, not hosted or production evidence. See [AI tracing](AI_TRACING.md), `BUILD_STATUS.md`, and the [public native summary](evidence/native-summary.json). Earlier runs and failures remain historical evidence.

The [provider-message export](evidence/provider-calls.json) verifies all five cases' native pairs plus the failure pair: **42 metadata messages**. Authenticated native IRIS Visual Trace captures show the [successful transaction, session 374](assets/provider-success-visual-trace.png), and [contained failure, session 316](assets/provider-failure-visual-trace.png). These portal captures are separate from private vendor-rendered SVG exports.

## Version boundary

The [official development template](https://github.com/intersystems-community/ai-hub-dev-template/tree/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7) explicitly uses `2026.3.0AI.154.0` in its Dockerfile and installation instructions. This is the build anchor for SilentShift. Its native sample agent, tools and initialization sequence are preferable to assuming that every feature in the moving EAP documentation exists on build 154.

The [EAP documentation snapshot](https://github.com/intersystems-community/ai-hub-eap/tree/cf50da7d3074f09e58d6b2b9858aef22cfbd68b6) has broader features, some marked for other builds. In particular, do not infer that newer session persistence, RAG helpers, tool timeout attributes, provider aliases or configuration shortcuts are supported on the target build. Runtime class inspection and compilation are required.

## Supported native lifecycle

Sources: [Sample.Agent](https://github.com/intersystems-community/ai-hub-dev-template/blob/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7/src/Sample/Agent.cls), [template invocation instructions](https://github.com/intersystems-community/ai-hub-dev-template/blob/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7/README.md).

The official template's declarative lifecycle is:

1. Subclass `%AI.Agent`.
2. Configure `MODEL`, optional `TOOLSETS`, and `XData INSTRUCTIONS`.
3. In `%OnInit()`, create a `%AI.Provider` and assign `..Provider`.
4. Instantiate the subclass and check the status from `%Init()`.
5. Add any instance-scoped tools before session creation.
6. Call `CreateSession(...)`, followed by `Chat(session, request)`.
7. Read the `%AI.LLM.Response` object's `Content`; it is not a dynamic JSON object's `content` field.

The current implementation uses a `%RegisteredObject` helper and constructs the native agent inside the queued investigation operation. Its provider configuration follows this pattern after the operation has opened a server-bound lease:

```objectscript
Set settings = {
    "api_key": (providerToken),
    "base_url": "http://gateway/silentshift-provider/v1/"
}
Set provider = ##class(%AI.Provider).Create("openai", settings)
Set agent = ##class(%AI.Agent).%New(provider)
Set sc = agent.%Init()
$$$ThrowOnError(sc)
Set agent.Model = "qwen3-silentshift:4b-instruct"
```

`providerToken` is an opaque, short-lived capability issued inside IRIS, not an external API credential. The actual [`Investigator`](../src/SilentShift/AI/Investigator.cls) checks the host's case/session/invocation context, registers tools, calls `CreateSession`/`Chat`, and closes the lease on success or exception. This excerpt requires that production context; it is not a standalone investigation. The Business Process still contains incomplete or invalid proposals rather than substituting a synthetic success.

## Local-only LLM route

The official EAP guide has documented Ollama through the OpenAI-compatible provider since [commit d917f977, 2026-05-11](https://github.com/intersystems-community/ai-hub-eap/blob/d917f977cb561e9c8a258cf999b460805f6fe250/ObjectScript_SDK_Guide.md). A direct SDK illustration is:

```objectscript
Set provider = ##class(%AI.Provider).Create("openai", {
    "base_url": "http://host.docker.internal:11434/v1/",
    "api_key": "ollama"
})
```

This direct illustration is not SilentShift's traced production route. The application always sends native SDK calls to the fixed internal HTTP gateway; its separately pooled Business Operation forwards to `SILENTSHIFT_LLM_BASE_URL`. The observed local target is `http://host.lima.internal:11434/v1/`. Only known local hostnames on port 11434, the exact `/v1/` path, and model `qwen3-silentshift:4b-instruct` are accepted. External providers and fallback are not implemented on this path.

`host.docker.internal` and `host.lima.internal` are deployment-specific host addresses, not SDK features. Verify reachability from the actual container; container loopback points to the container itself.

[Ollama's official compatibility documentation](https://docs.ollama.com/api/openai-compatibility) confirms that local requests require an API key value which is ignored, and that `/v1/chat/completions` supports tools. An installed model must support the required function calling. Merely having an Ollama server or a model file is insufficient evidence. The acceptance test must observe native IRIS agent tool calls, a final response and persisted routing. A local LLM remains a real model; report its exact model identity and measured results.

No external provider API key is needed for the current route. The opaque per-investigation bearer must never be printed, stored in persistent message bodies, placed in a URL, or included in evidence exports.

## Narrow tool registration

Sources: [Sample.Tools](https://github.com/intersystems-community/ai-hub-dev-template/blob/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7/src/Sample/Tools.cls), [Sample.ToolSet](https://github.com/intersystems-community/ai-hub-dev-template/blob/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7/src/Sample/ToolSet.cls), [official ToolUsage example](https://github.com/intersystems-community/ai-hub-eap/blob/cf50da7d3074f09e58d6b2b9858aef22cfbd68b6/objectscript/cls/Sample/AI/Examples/ToolUsage.cls).

Typed methods on a `%AI.Tool` subclass are discoverable tools. `%AI.ToolSet` uses an XML `XData Definition` with `<ToolSet>` and `<Include Class="..."/>`. The official example also registers a tool object directly:

```objectscript
Set agent = ##class(%AI.Agent).%New(provider)
Set sc = agent.%Init()
If $$$ISERR(sc) Quit sc
Set tools = ##class(SilentShift.AI.EvidenceTools).%New()
Set tools.CaseId = caseId
Do agent.ToolManager.AddTool(tools)
Set session = agent.CreateSession({"max_iterations": 6, "max_tokens": 192})
Set response = agent.Chat(session, "Investigate the current transaction.")
Set rawRecommendation = response.Content
```

`CaseId` is a SilentShift-owned property, not an SDK property. Tools should derive the accessible message, contracts, references, history and reviewed cases from that bound case. The model must not choose arbitrary case identifiers, SQL, shell commands, table names or mutation targets. Methods should validate scalar input and cap returned records and text length.

## Bounded execution and audit

The [ObjectScript guide](https://github.com/intersystems-community/ai-hub-eap/blob/cf50da7d3074f09e58d6b2b9858aef22cfbd68b6/ObjectScript_SDK_Guide.md) documents `max_iterations` and `max_tokens` in `CreateSession` configuration. Use a positive small cap. Do not copy the uncapped examples intended for complex research agents. No build-154 SDK request-timeout property was established in this research; do not invent one. Enforce the enclosing interoperability job/request deadline and contain incomplete investigations. Verify cancellation and late-result behavior at runtime.

The [advanced policy guide](https://github.com/intersystems-community/ai-hub-eap/blob/cf50da7d3074f09e58d6b2b9858aef22cfbd68b6/ObjectScript_SDK_Advanced.md) documents these hooks:

- `%AI.Policy.Authorization.%CanExecute(toolref, call, metadata) As %Status`
- `%AI.Policy.Audit.%LogExecution(call, metadata, result, duration, status)`
- `agent.ToolManager.SetAuthPolicy(policy)` and `SetAuditPolicy(policy)`

Use an allowlist and persist bounded audit records. The first hook argument identifies a registration; use `call.name` for an individual invocation. Do not send console audit output into REST responses. Independently validate the final JSON schema, enum, evidence existence, relevance and policy conditions. An explanatory sentence or claimed confidence is never permission to deliver.

Application records should persist the raw response, validated proposal, referenced evidence, model identity, observed usage and final policy result. Do not assume newer `%AI.Agent.Session.%Save()` support on build 154; application persistence is sufficient and easier to inspect.

## Acquisition and reproducibility

[Official installation instructions](https://github.com/intersystems-community/ai-hub-dev-template/blob/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7/README.md) require downloading a suitable architecture image from the [AI Hub EAP portal](https://evaluation.intersystems.com/Eval/early-access/AIHub), then `docker load -i /local/path/to/image-docker.tar.gz`. The loaded tag can differ for ARM64; use the image identity actually printed by Docker. Do not pull a guessed public tag.

The [EAP README](https://github.com/intersystems-community/ai-hub-eap/blob/cf50da7d3074f09e58d6b2b9858aef22cfbd68b6/README.md) says the prerelease software is not for production use. Public source examples are MIT-licensed; this is not permission to republish the proprietary runtime image. Keep the runtime, download archive and derived runtime images outside public repositories and registries. Publish only source, configuration templates and scripts.

## Required runtime evidence

- Record `$ZVERSION` and the loaded image digest; reject a different EAP build.
- Compile native classes and confirm tool discovery only exposes the intended read operations.
- Ingest through a real `Ens.BusinessService`, execute a real `Ens.BusinessProcess`, invoke `%AI.Agent` there and route through real `Ens.BusinessOperation` components.
- Record message/session trace identifiers, native tool calls, raw and parsed response, persisted policy verdict and routing result.
- Prove an unsafe agent proposal cannot release a contradiction, missing evidence, or unverified transformation.
- Repeat after restart and duplicate injection; verify no duplicate downstream effect.

Until those observations exist, label the native integration **implemented/unverified** or **blocked**, never complete.

## Implemented adapter contract (compiled on build 154U)

`src/SilentShift/AI/Investigator.cls` implements the business-process entry point `Run(caseId, assessmentJSON, .recommendationJSON, .metadataJSON)`. It constructs native `%AI.Provider` and `%AI.Agent` objects, initializes the agent, and registers the bound `EvidenceTools` object. The helper itself is a `%RegisteredObject` to avoid overriding the SDK agent's own `Run` method.

`src/SilentShift/AI/EvidenceTools.cls` exposes four application methods: `GetCurrentMessage`, `GetApprovedContracts`, `GetRelatedRecords` and `find_similar_precedents`. The adapter inspects `%Discover()` and rejects any catalog other than those four exact names. Successful reads produce bounded audit metadata, and the invocation must observe all four reads before returning a proposal. No routing/review method, model-chosen case ID, generic SQL, shell or filesystem tool is registered. Reads are capped at eight successful calls per investigation; each response is capped at 16 KiB, with approved/peer references capped at ten. History contains at most three same-contract, same-scenario summaries, explicitly marked as context without contract authority.

Current configuration uses `SILENTSHIFT_MODEL=qwen3-silentshift:4b-instruct` and an explicit local `SILENTSHIFT_LLM_BASE_URL`, normally `http://host.lima.internal:11434/v1/` on the observed Colima target. The provider lease enforces both values. The earlier external-key environment variables are not read by the current investigator; the gateway capability replaces them. `SILENTSHIFT_AGENT_WAIT_SECONDS` accepts 10–120, defaults to 60, and the tested local setup uses 120. A timeout contains the case and does not establish provider cancellation.

The proposed response contract is `{"decision":"ALLOW|QUARANTINE|REQUEST_REVIEW","evidence_ids":["actual-reference-id"],"explanation":"...","uncertainty":0.0}` with uncertainty in `[0,1]`. The adapter preserves the bounded raw response unchanged; the independent semantic/policy engine must validate JSON, fields, reference relevance and safety before routing. Malformed output never receives an adapter-authored replacement decision.

Metadata reports `mode=native-ai-hub`, actual model identity, elapsed time, limits and successful tool reads. `agent.response_usage` remains the final SDK response only. The separate provider layer now records numeric `response_usage` for each actual HTTP response, with `usage_scope=actual_http_response_only`, plus HTTP outcomes and tool-call metadata. Neither scope is presented as SDK session totals or billing cost. The adapter does not call `session.GetStats()` on the synchronous routing path. The [template SDK reference](https://github.com/intersystems-community/ai-hub-dev-template/blob/37280e3d0252f1034cdd5b32f0eeea55ff34ffa7/skills/ai-hub-objectscript-sdk/references/objectscript-sdk-reference.md) documents that method, but totals remain uncollected. Provider exception details are withheld because diagnostics can contain sensitive data.

The discovery allowlist passed on build 154. Direct instance registration and native tool dispatch produce persisted `agent_tool_read` audit rows. Partial reads, empty answers and timeouts were observed and rejected. The earliest policy 1.0 run was 3/5 correct without unsafe delivery; later five-case runs passed, including the provider-traced run above. Neither native execution nor valid JSON alone proves a correct decision. Recovery evidence remains scoped to the separately documented tests.

For explicitly local Qwen3 inference, session configuration uses `extra_params: {"reasoning_effort":"none"}` with six iterations and 192 output tokens per request. Build154's installed `iris_llm`2.0.0 completion adapter documents that provider-specific options go through `extra_params`; unknown top-level fields are dropped by its native deserializer. [Ollama0.31.1's own request conversion](https://github.com/ollama/ollama/blob/v0.31.1/openai/openai.go#L591-L618) maps `none` to `think=false`. The prompt's `/no_think` soft instruction alone is insufficient evidence of that setting. No reasoning text is extracted or turned into an answer. The correct build154 dynamic-object type method is `%GetTypeOf`. The prompt asks for sequential tools, but no supported hard parallel-tool switch was found; actual audits establish which calls happened.

### Individual provider requests and responses

Installed source showed that `%AI.Agent.Chat` passes a native provider token directly into the bundled runtime, bypassing ObjectScript `Provider.ChatComplete` overrides. A supported `base_url` HTTP hop captures each completion request while the native agent and native tool manager retain orchestration.

Each admitted completion request travels through `SilentShift.Provider.API` → `ProviderIngress` → queued `ProviderForwarder` → local Ollama. A server-issued lease binds it to the case's original interoperability session and invocation span. The ingress uses `%PreserveSession=1` and the bound `%SessionId`; native `SendRequestSync` creates the actual `CallRequest`/`CallResponse` headers and reciprocal message IDs. Returning HTTP failures inside a typed response prevents the Business Operation framework from silently retrying inference.

The actual metadata field map for [`CallRequest`](../src/SilentShift/Provider/CallRequest.cls) and [`CallResponse`](../src/SilentShift/Provider/CallResponse.cls), schema `silentshift-provider-call/1`, is:

| Fields | Recorded meaning and boundary |
|---|---|
| `call_id`, `case_id`, `production_session_id`, `invocation_span_id` | Server-bound pair/case/session/parent correlation, checked against actual native header session and reciprocal message IDs. |
| `round` | Monotonic admitted HTTP-request number, capped at eight; not an SDK iteration or classified retry. |
| `provider`, `model`, `prompt_version` | Provider identity, local model and instruction version, currently `silentshift-investigator/1.3.1`; not a prompt-content hash. |
| Request `started_at`, `request_bytes`, `tool_names` | Admission time, original body bytes, and advertised tool names; offered tools do not establish execution. |
| Response `started_at`, `finished_at`, `duration_ms` | Forwarding-operation timing including validation, HTTP I/O, metadata parsing and cleanup; not pure network latency. |
| `http_status`, `upstream_http_status`, `error_code`, `response_bytes` | Relay outcome, upstream status if received, fixed safe failure code and response bytes. Transport/gateway failures can lack upstream status. |
| `tool_calls`, `finish_reason` | Bounded returned tool IDs/allowlisted names with `arguments_omitted=true`, and a recognized finish reason. Actual tool audits are separate. |
| `response_usage`, `usage_scope` | Numeric usage from this actual response or null, scoped `actual_http_response_only`; separate from final SDK response usage and session totals. |
| `application_retry_count`, `provider_retry_count`, `fallback_used` | Zero application retries, null SDK/provider retry classification, and false fallback. Admitted repeated requests get new pairs. |
| `billing_cost`, physical `CostStatus` | Null cost / unavailable status; no inferred billing or token-derived price. |
| `execution_mode`, `replay_record_id` | `live` or explicit `recorded-replay`; fixture ID only for playback. Playback has null upstream status and current usage. |
| `content_retained`, `payload_storage` | Persistent provider bodies omit raw content. Temporary IPC storage is `IRISTEMP_nonjournaled_until_relay_completion`; case evidence/final proposals are stored separately. |

The case's `agent.provider_transport` identifies this HTTP layer, and `provider_request_count` records admitted calls before lease closure. Invocation/tool events retain their own `agent.trace` scope. Historical invocation-only traces do not retroactively establish provider-call coverage. See [AI tracing](AI_TRACING.md) for exact case IDs, header pairs, and local reproduction commands, including the isolated real HTTP 400 probe.

The lease caps admitted requests at eight and each body at 262,144 bytes. It admits only nonstreaming local requests within the token budget. Raw bytes cross jobs in verified nonjournaled IRISTEMP and normal relay cleanup removes them; persistent provider bodies contain metadata only. Business payloads and bounded final proposals remain separately stored. UTF-8/raw-stream bounds, unknown-bearer denial, real upstream 200/400 outcomes, original-session pairing and normal transient cleanup were verified.

After interruption, expired entries are swept on the next lease `Open`, at most 64 entries per kind; there is no background TTL worker or removal guarantee exactly at expiry while idle. The forwarder requests identity encoding and rejects a changed sink or nonidentity encoding after the native HTTP read. Native HTTP code may already have staged an unexpected gzip response to a temporary file before rejection, so the bounded identity-response stream does not prove a bound on that native file. Cancellation, crash recovery and arbitrary upstreams remain outside this evidence.

[Langfuse](https://langfuse.com/docs/observability/overview) provides LLM traces with inputs/outputs, tools, usage, latency and relationships, plus cost analysis, scores, prompt management, experiments and dashboards. SilentShift's narrower advantage is direct correlation with the native business transaction: actual provider pairs, reference reads, policy consequence and delivery/hold share one IRIS session. It omits raw provider content and general LLM operations tooling; session totals, billing cost and SDK retry classification remain unavailable. This is an application-specific integration, not a feature-parity or superiority claim.

### Callback stability repair

Early ARM64 runs logged worker signal11 inside `Chat()` near tool callbacks. Removing the optional statistics getter did not resolve it. The original callback audit path nested Embedded Python through `Store.AddEvent`; changing its JSON serialization and UTC timestamp to native ObjectScript removed that nested language boundary. Subsequent complete 2B and4B benchmark runs did not crash. Semantic assessment and deterministic policy still execute through Embedded Python in the Business Process, outside the agent's tool callbacks. This is observed application-level repair evidence, not a vendor-confirmed SDK defect or a claimed bug-report bonus.

Each investigation now preserves `native_chat_returned` and `agent_operation_finished` events. An expired queued request checks the persisted routing state before starting model work; a held case receives no new investigation. A late operation has no policy or routing authority.

## Interoperability foundation source

The native source includes `SilentShift.Production`, adapterless `Service.Partner`, `Process.Semantic`, and independent queued `References`, `Investigation`, `Destination` and `Quarantine` operations. The generic contracts are verified in the official [Business Service guide](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=EGDV_busservice), [Business Process guide](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=EGDV_busproc) and [Ens.Director reference](https://docs.intersystems.com/irisforhealthlatest/csp/documatic/%25CSP.Documatic.cls?CLASSNAME=Ens.Director&LIBRARY=ENSLIB). Synchronous requests have explicit finite waits and each queued host has its own pool.

Persistent SQL classes hold cases, independent references, audit rows, review idempotency receipts and simulator delivery receipts. Structured source/event hashes identify duplicates; normalized content fingerprints reject event-key reuse with changed content. Locks, unique receipts and transactions protect the included simulator. The destination reevaluates policy before saving an effect. Actual replay, concurrent approval and restart checks support these invariants for the documented test paths; they do not establish real external-delivery guarantees.

Frozen scenario references use independently seeded `ScenarioScope` partitions because the scenarios deliberately reuse a contract ID with incompatible histories. Only the server scenario endpoint chooses a partition and replay clock. General ingress uses the unscoped approved catalog. Per-case snapshots are immutable. Reference retrieval reads up to 101 rows and refuses more than 100 rather than silently omitting a conflict. The narrower agent tools report their own reference truncation; missing citations cannot authorize release.

Reviews require the resource, current IRIS identity, expected version, reason and idempotency key. Human proposals pass the same deterministic policy; a veto returns `APP_FORBIDDEN`. The Partner service sends the outcome through native routing. Actual model output remains separate from human proposals and scenario E's labeled hostile validator input.

`Setup.Install` rejects other EAP builds, creates permissions/accounts from environment values, seeds references without cases, enables auto-start and starts the production. It never invokes a model. Existing application accounts are preserved; owned role/resource definitions are reconciled to remove stale grants. Viewer and reviewer roles have no permanent database or Embedded Python permission. The REST application's `MatchRoles="SSViewer:SSApplication"` adds scoped database, named-table SELECT and `%Service_EmbeddedPython:U` permissions only during application execution; it never grants reviewer permission. The native portal application uses `MatchRoles="SSReviewer:SSNativeTrace"` to add only `%Ens_MessageTrace:U`, `%Ens_Portal:U`, and `%DB_SILENTSHIFT:R` while an existing reviewer uses that application. It adds no database write, resend, or production control. Authenticated portal captures above verify trace access. The internal provider endpoint separately uses the always-add application role syntax `MatchRoles=":SSProviderTransport"`; its active bearer lease is checked before body access. Authenticated CallIn is enabled without changing its authentication bitmap or public resource permissions. The role format is documented in the official [Security.Applications reference](https://docs.intersystems.com/irislatest/csp/documatic/%25CSP.Documatic.cls?CLASSNAME=Security.Applications&LIBRARY=%25SYS). Password authentication uses `AutheEnabled=32` (bit 5), verified in the official [Security.System reference](https://docs.intersystems.com/healthconnectlatest/csp/documatic/%25CSP.Documatic.cls?CLASSNAME=Security.System&LIBRARY=%25SYS).

Compose uses the locally loaded IRIS image with `pull_policy: never`, a persistent manager volume and source at `/opt/silentshift`. Native port 1972 is internal to the Compose network; host access uses `docker compose exec`. A separate gateway configuration derives from the [official example at 923316d](https://github.com/intersystems-community/webgateway-examples/tree/923316d36da1b7ee8382f7faaf145139996f243d/demo-compose). Default passwords and wildcard management access were removed. Gateway credentials are generated under ignored `.local/`; its HTTP host port binds to loopback. A fresh-volume bootstrap and authenticated end-to-end verification passed with this gateway.

Bootstrap has run against the officially downloaded and locally loaded image with standalone Compose5.6.1 in an isolated `colima-silentshift` context. The production starts and the separate gateway returns authenticated health/cases over loopback. Real quantity cases reached quarantine with trace IDs and no delivery receipts. Actual runtime repairs include the registered-object character-stream Business Service signature, `%Get` for underscore JSON keys, correctly typed pagination, and `IS NULL` for the unscoped SQL reference catalog. Clean installation, five-scenario runs, restart/concurrency checks and connected browser coverage passed. Provider-side cancellation, network-loss recovery and broader repeated trials remain limits.

## Fourth tool and build154 dispatch compatibility

The current native catalog adds the exact no-argument `find_similar_precedents` name. Build154's inherited `%AI.Tool` invocation generator emits a bare ObjectScript method call; an underscore name needs quoting and failed compilation. `EvidenceTools` supplies an application-only `%Invoke` dispatcher for the exact four-method allowlist, preserving native discovery and result encoding. It rejects nonempty/nonobject arguments and unknown names. Vendor code is unchanged. A native no-model dispatch probe verified all four methods against an isolated diagnostic case; actual model callbacks are separately proven by the five-case run.

Current prompt `silentshift-investigator/1.3.1` uses192 output tokens and six iterations, with short final explanations. The gateway's admission ceiling remains700 tokens/eight actual HTTP requests. Run `fc12cbcf-c9fc-4813-8614-8ac944d6e8fd` passed5/5; all four tools ran and every actual provider call was paired. The SDK batched tool requests in this run, producing two provider calls per case despite the sequential prompt guidance. [Precedent evidence](PRECEDENTS.md) documents the vectors, source bindings, critical veto, earlier timeout trials and warmed/serial-run boundary. No provider cancellation or general performance guarantee is claimed.

## No-key recorded-provider example (0.2.0)

Follow the exact [README recipe](../README.md#see-it-in-visual-trace). The packaged `SilentShift.Provider.Replay` supplies the recorded final assistant content from original live session 1471. Its SHA-256 and original usage are provenance in `fixtures/provider-replay.json`; tool-call envelopes are reconstructed and usage is deliberately absent from playback responses. All four tools still execute through native AI Hub. Replay is restricted to the frozen synthetic quantity-mismatch case while PROCESSING, with its expected critical assessment and contract ID. It cannot be selected by partner payloads or used to authorize a real order.

`SILENTSHIFT_PROVIDER_MODE` defaults to `live`. `recorded-replay` is operator configuration at container creation; the lease binds and the operation rechecks it. Both modes traverse the same provider ingress, queued forwarder and typed native messages. Live continues to call the configured local Ollama model with a short-lived application bearer capability. External provider API keys are neither required nor supported by this local-only transport.

The native `%UnitTest` suite includes physical model/prompt/provider/session/timing/usage assertions, zero-token preservation, null cost, replay labeling, recorded-response progression, frozen-case restrictions and the critical-policy veto. `scripts/trace_example.py` additionally reads persisted paired headers/bodies from the packaged inspector and exercises the authenticated REST entry point. Playback `HTTPStatus=200` is a local relay result; `UpstreamHTTPStatus` remains empty/null. `DurationMS` measures this playback operation, not the original inference.

For every requested comparison dimension, see [SilentShift vs Langfuse](../README.md#silentshift-iris-interoperability-vs-langfuse). Native Workflow task creation shares the intake session; subsequent human requests have independent sessions linked by case/task/decision records. No claim is made that an entire multi-day review has one session ID.

The public-registry 0.2.0 install independently repeated the full native suite and no-key replay, session 24 at port 52813. [Complete receipt, paired headers and metadata](evidence/bonus-020-registry-install.json). All 55 runtime/package files from the downloaded registry source match the released source.
