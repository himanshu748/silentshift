"""Deployment-owned OpenAI-compatible provider configuration; no model calls."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from urllib.parse import urlsplit, urlunsplit

DEFAULT_MODEL = 'qwen3-silentshift:4b-instruct'
LOCAL_HOSTS = {'localhost', '127.0.0.1', 'host.docker.internal', 'host.lima.internal', 'ollama'}
DEFAULT_URLS = {'ollama':'http://host.lima.internal:11434/v1/',
    'openai':'https://api.openai.com/v1/',
    'gemini':'https://generativelanguage.googleapis.com/v1beta/openai/',
    'openrouter':'https://openrouter.ai/api/v1/'}


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    trace_provider: str
    model: str
    base_url: str
    host: str
    port: int
    path: str
    transport: str
    key_required: bool
    execution_mode: str

    def public(self):
        """No key, key fingerprint, authorization header or response content."""
        return asdict(self)


def resolve_provider(env) -> ProviderConfig:
    mode = env.get('SILENTSHIFT_PROVIDER_MODE','live') or 'live'
    if mode not in {'live','recorded-replay'}:
        raise ValueError('SILENTSHIFT_PROVIDER_MODE must be live or recorded-replay.')
    if mode == 'recorded-replay':
        # Frozen recorded Qwen responses never use a remote key or endpoint.
        return ProviderConfig('ollama','recorded-ollama/openai-compatible',DEFAULT_MODEL,
            DEFAULT_URLS['ollama'],'host.lima.internal',11434,'/v1/chat/completions','replay',False,mode)
    provider = env.get('SILENTSHIFT_PROVIDER','ollama') or 'ollama'
    if provider == 'compatible':
        provider = 'openai-compatible'
    if provider not in {*DEFAULT_URLS,'openai-compatible'}:
        raise ValueError('SILENTSHIFT_PROVIDER must be ollama, openai, gemini, openrouter or openai-compatible.')
    model = env.get('SILENTSHIFT_MODEL','') or (DEFAULT_MODEL if provider=='ollama' else '')
    if not isinstance(model,str) or not model.strip() or len(model)>160 or any(ord(c)<32 for c in model):
        raise ValueError('SILENTSHIFT_MODEL is required and must be bounded text for the selected provider.')
    url = env.get('SILENTSHIFT_LLM_BASE_URL','') or DEFAULT_URLS.get(provider,'')
    if not isinstance(url,str) or not url or len(url)>512 or any(ord(c)<=32 for c in url) or '\\' in url:
        raise ValueError('SILENTSHIFT_LLM_BASE_URL must be a bounded base URL without whitespace.')
    try:
        parsed=urlsplit(url)
        port=parsed.port or (443 if parsed.scheme=='https' else 80)
        host=parsed.hostname
    except ValueError:
        raise ValueError('SILENTSHIFT_LLM_BASE_URL has an invalid host or port.') from None
    if (parsed.scheme not in {'http','https'} or not host or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment or parsed.netloc.endswith(':')
            or not 1<=port<=65535 or any(c in parsed.path for c in ['%',';'])):
        raise ValueError('SILENTSHIFT_LLM_BASE_URL must not contain credentials, query, fragment or encoded path components.')
    if parsed.scheme=='http' and host not in LOCAL_HOSTS:
        raise ValueError('Remote SILENTSHIFT_LLM_BASE_URL requires HTTPS; plaintext HTTP is restricted to explicit local hosts.')
    path=parsed.path.rstrip('/')
    if not re.fullmatch(r'(?:/[A-Za-z0-9_.~-]+)*',path) or path.endswith('/chat/completions'):
        raise ValueError('SILENTSHIFT_LLM_BASE_URL must be the API base, not a chat/completions URL.')
    if provider=='ollama' and (host not in LOCAL_HOSTS or port!=11434 or parsed.scheme!='http' or path!='/v1'):
        raise ValueError('Ollama requires an explicit local http://host:11434/v1/ route; use openai-compatible for another deployment.')
    key_required=provider!='ollama'
    key=env.get('SILENTSHIFT_API_KEY','')
    if key_required and not key:
        raise ValueError(f"SILENTSHIFT_API_KEY is required for provider '{provider}'. Set it in the gitignored .env file.")
    if key and (not isinstance(key,str) or len(key)>4096 or key!=key.strip() or any(ord(c)<33 or ord(c)>126 for c in key)):
        raise ValueError('SILENTSHIFT_API_KEY must be a single bounded printable token; its value is never logged.')
    normalized=urlunsplit((parsed.scheme,parsed.netloc,path+'/','',''))
    return ProviderConfig(provider,provider+'/openai-compatible' if provider!='openai-compatible' else 'custom/openai-compatible',
        model,normalized,host,port,path+'/chat/completions','native-ollama' if provider=='ollama' else 'stdlib-http',key_required,mode)
