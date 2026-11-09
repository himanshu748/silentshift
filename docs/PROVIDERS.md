# Choose a model provider

This is unpublished work on `push/top3`. The public IPM 0.3.0 package does not contain these provider options. Local Ollama remains the default; recorded playback still needs no model or provider key.

Copy `.env.example` to the gitignored `.env` and replace its active provider, base URL, model and key entries with one of the commented provider blocks. Do not append duplicate settings. Restart the source-built deployment after changing its environment. `scripts/bootstrap.py` checks configuration before starting containers and names missing settings without printing their values.

| Provider | `SILENTSHIFT_PROVIDER` | Default base URL |
| --- | --- | --- |
| Local Ollama | `ollama` | `http://host.lima.internal:11434/v1/` |
| OpenAI | `openai` | `https://api.openai.com/v1/` |
| Gemini compatibility API | `gemini` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| OpenRouter | `openrouter` | `https://openrouter.ai/api/v1/` |
| Another compatible deployment | `openai-compatible` | Set `SILENTSHIFT_LLM_BASE_URL` explicitly |

The endpoint must implement non-streaming OpenAI-compatible Chat Completions, function/tool calls and tool-result messages. Select a model supporting that contract. “Compatible” does not mean every model or provider option has been tested. External accounts and usage may cost money; no external provider call was made during this work.

The native AI Hub agent still calls the internal capability-scoped gateway. Each call passes through `SilentShift.Provider.Forwarder` as an interoperability request and response in its case session. Provider, model, prompt version, duration and tool-call metadata use the existing native message fields. The deployment selects the upstream; case content cannot select an endpoint. The remote transport checks TLS certificates, refuses redirects and bounds requests and responses. Credentials are read only when forwarding and are excluded from configuration metadata and messages. Local Ollama keeps the native HTTP transport. Deterministic routing and the investigator's system prompt are unchanged.

Remote providers require `SILENTSHIFT_API_KEY` and `SILENTSHIFT_MODEL`. Remote URLs require HTTPS. Credentials, queries, fragments and a full `/chat/completions` URL are rejected; supply the API base instead. Plain HTTP is limited to the explicitly supported local hostnames. The default Qwen-specific reasoning option is applied only to the Ollama route.

`SILENTSHIFT_PROVIDER_MODE=recorded-replay` ignores remote model, endpoint and key configuration and uses the existing frozen synthetic Qwen responses. It performs no inference and is not a provider compatibility test.

## What was checked

`uv run pytest -q` passed 242 tests. The 31 provider checks exercise parsing, missing-key errors, secret-free public metadata, UTF-8 request bodies, tool-call responses, redirect refusal and response bounds against a local HTTP test server. They do not verify the commercial services. A clean ARM64 154U source load compiled and passed the five native test classes and twelve methods. Two native attempts were interrupted by the local VM's out-of-memory condition; the end-to-end replay and per-provider Visual Trace demonstration remain unverified. [Partial receipt](evidence/top3-provider-partial-nov9.json).

Provider protocol references: [Google's compatibility API](https://ai.google.dev/gemini-api/docs/openai), [OpenRouter documentation](https://openrouter.ai/docs/quickstart). These describe the wire contract, not observed SilentShift service execution.
