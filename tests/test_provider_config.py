import json

import pytest
from silentshift.provider_config import resolve_provider


def remote(provider='openai'):
    return {'SILENTSHIFT_PROVIDER':provider,'SILENTSHIFT_MODEL':'synthetic-tool-model','SILENTSHIFT_API_KEY':'synthetic-test-key'}


def test_default_is_local_ollama_without_external_key():
    c=resolve_provider({})
    assert c.provider=='ollama' and c.model=='qwen3-silentshift:4b-instruct'
    assert c.path=='/v1/chat/completions' and not c.key_required


@pytest.mark.parametrize(('provider','host','path'),[
    ('openai','api.openai.com','/v1/chat/completions'),
    ('gemini','generativelanguage.googleapis.com','/v1beta/openai/chat/completions'),
    ('openrouter','openrouter.ai','/api/v1/chat/completions')])
def test_documented_provider_endpoints(provider,host,path):
    c=resolve_provider(remote(provider))
    assert (c.host,c.port,c.path,c.transport)==(host,443,path,'stdlib-http')
    assert c.provider in c.trace_provider
    assert 'synthetic-test-key' not in json.dumps(c.public()) and 'synthetic-test-key' not in repr(c)


@pytest.mark.parametrize('provider',['openai','gemini','openrouter','openai-compatible'])
def test_missing_key_error_names_variable_and_provider(provider):
    env={**remote(provider),'SILENTSHIFT_API_KEY':''}
    if provider=='openai-compatible':env['SILENTSHIFT_LLM_BASE_URL']='https://synthetic.example/v1/'
    with pytest.raises(ValueError,match=f"SILENTSHIFT_API_KEY is required for provider '{provider}'"):
        resolve_provider(env)


@pytest.mark.parametrize('url',[
    'http://remote.example/v1/', 'https://user:secret@example.com/v1/',
    'https://example.com/v1/?key=secret','https://example.com/v1/#secret',
    'https://example.com:99999/v1/','https://example.com/v1/chat/completions',
    'https://example.com/%2e%2e/v1/','https://example.com/v1/\n',
    'https://example.com:/v1/','file:///tmp/models','https://example.com\\@other.test/v1/'
])
def test_endpoint_rejects_plaintext_secrets_redirectlike_or_ambiguous_forms(url):
    with pytest.raises(ValueError):resolve_provider({**remote(),'SILENTSHIFT_LLM_BASE_URL':url})


def test_custom_base_path_and_port_are_preserved():
    c=resolve_provider({**remote('compatible'),'SILENTSHIFT_LLM_BASE_URL':'https://models.example:8443/openai/v2'})
    assert c.provider=='openai-compatible' and c.path=='/openai/v2/chat/completions' and c.port==8443


def test_replay_cannot_use_remote_key_or_change_recorded_identity():
    c=resolve_provider({'SILENTSHIFT_PROVIDER_MODE':'recorded-replay','SILENTSHIFT_PROVIDER':'openai',
        'SILENTSHIFT_MODEL':'different','SILENTSHIFT_LLM_BASE_URL':'https://never-contact.example/v1/'})
    assert c.transport=='replay' and not c.key_required
    assert c.trace_provider=='recorded-ollama/openai-compatible' and c.model=='qwen3-silentshift:4b-instruct'


def test_key_control_characters_are_rejected_without_echoing_the_value():
    env={**remote(),'SILENTSHIFT_API_KEY':'private\r\nInjected:value'}
    with pytest.raises(ValueError) as e:resolve_provider(env)
    assert 'Injected' not in str(e.value) and 'private' not in str(e.value)


def test_unknown_provider_and_missing_model_fail_before_any_network_call():
    with pytest.raises(ValueError,match='SILENTSHIFT_PROVIDER must'):resolve_provider({'SILENTSHIFT_PROVIDER':'typo'})
    with pytest.raises(ValueError,match='SILENTSHIFT_MODEL is required'):resolve_provider({'SILENTSHIFT_PROVIDER':'openai'})
