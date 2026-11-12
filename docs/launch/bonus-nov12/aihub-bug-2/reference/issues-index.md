# Duplicate-check snapshot

Captured 2026-11-12T15:25:12.711804+00:00

- [#27](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/27) — open — IRIS AI Hub EAP build 154U keeps the default IRISLOCALDATA database mounted read-write after relocation
- [#26](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/26) — open — `iris-main` aborts with exit 134 when the working directory isn't writable
- [#25](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/25) — open — A tool hidden by %CanList is rejected with no audit record (2027.1.0AI.109.0)
- [#24](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/24) — open — The OpenAI provider sends `max_tokens`, which current OpenAI models refuse; there is no setting for `max_completion_tokens` (2027.1.0AI.109.0)
- [#23](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/23) — open — A fresh instance has no Config Store descriptor for AI.LLM: Create fails with #26414 until RebuildRegistry() runs (2026.3.0AI.154.0, 2027.1.0AI.109.0)
- [#22](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/22) — open — A tool argument's JSON Schema describes only the first of several properties that share one class; the others become a bare `object` (2026.3.0AI.154.0, 2027.1.0AI.109.0)
- [#21](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/21) — open — %AI.RAG.VectorStore.IRIS makes its table in SQLUser whatever its Schema property says (154U)
- [#20](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/20) — open — %AI.ToolMgr.ExecuteTool runs a tool with arguments its own advertised schema refuses (154U)
- [#19](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/19) — open — %AI.RAG.Embedding.FastEmbed: the class description says the model is bundled and no network is needed; the first Create() downloads 87 MB and fails offline
- [#18](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/18) — open — Agent tool loop in EnsLib.AI.Agent.PassthroughOperation has no default bound and keeps running after the caller's SendRequestSync timeout
- [#17](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/17) — open — %AI.Tool generates an unquoted call for a valid quoted underscore method (154U)
- [#16](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/16) — open — An empty assistant turn is sent back without `content`, so the next `Chat()` in the session fails with HTTP 400 on Ollama
- [#15](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/15) — open — `%AI.Agent` process dies with signal 11 when a response has several tool calls and a tool uses Embedded Python
- [#14](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/14) — open — %AI.Policy.Audit receives call.arguments as a JSON string, while %AI.Policy.Authorization receives an object
- [#13](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/13) — open — iris-mcp-server 2.0.0: after a rejected server/discover, tools/list fails in the same session
- [#12](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/12) — open — `Run()` never calls the callback's `OnIterationStart` and `OnIterationComplete` on build 154
- [#11](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/11) — open — `%AI.Agent.Run()` takes three arguments on build 154; the documented four-argument form raises `<PARAMETER>`
- [#10](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/10) — open — Provider errors that AI Hub recognises (model not found, billing, timeout) are thrown as <%AICore>ProviderError instead of their dedicated codes
- [#9](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/9) — open — OpenAI-compatible providers drop finish_reason: a reply cut at the token limit looks like a complete answer
- [#8](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/8) — open — %AI.RAG.Embedding.FastEmbed: EmbedBatch() throws 'use the Rust bridge directly' instead of returning vectors
- [#7](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/7) — open — ToolSet Policies: a child element under one policy is copied into every policy getter, so %Init() fails with PROPERTY DOES NOT EXIST
- [#6](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/6) — open — Session timeout_ms does not stop a slow provider request: Chat returns after 20 s with timeout_ms = 3000
- [#5](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/5) — open — %AI.Provider silently retries HTTP 429 and 503 (4 requests per Chat), with no setting and no signal to the caller
- [#4](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/4) — open — Audit policy example in `ObjectScript_SDK_Advanced.md` does not compile, and `call.arguments.%ToJSON()` fails silently
- [#3](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/3) — open — EnsLib.AI.Agent.OutboundAdapter ignores the model in its ProviderConfig; the provider default (claude-sonnet-5, max_tokens 131072) is sent
- [#2](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/2) — open — Agent runs a tool call from a response that stopped at max_tokens, and Chat() reports only the last stop reason
- [#1](https://github.com/intersystems-community/ai-hub-eap-bugreports/issues/1) — open — Startup error `<METHOD DOES NOT EXIST>Sharding+2^STU *Sharding,SYS.ICM` on every start
