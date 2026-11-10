import base64
import json
import ssl
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from silentshift.provider_config import resolve_provider
from silentshift.provider_transport import MAX_BYTES, forward


@contextmanager
def endpoint(status=200,body=b'{"choices":[]}',encoding=None,redirect=None):
    seen=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            seen.append({'path':self.path,'body':self.rfile.read(int(self.headers['Content-Length'])),
                'authorization':self.headers.get('Authorization'),'accept_encoding':self.headers.get('Accept-Encoding')})
            self.send_response(status)
            if encoding:self.send_header('Content-Encoding',encoding)
            if redirect:self.send_header('Location',redirect)
            self.send_header('Content-Length',str(len(body)));self.end_headers()
            try:self.wfile.write(body)
            except (BrokenPipeError,ConnectionResetError):pass
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}/test/v1/',seen
    finally:server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('provider',['openai','gemini','openrouter','openai-compatible'])
def test_wire_contract_is_preserved_without_key_in_result(provider):
    raw=json.dumps({'model':'synthetic-tool-model','messages':[{'role':'user','content':'café'}]},ensure_ascii=False).encode()
    response=b'{"choices":[{"message":{"tool_calls":[{"id":"one","type":"function","function":{"name":"GetCurrentMessage","arguments":"{}"}}]}}],"usage":{"prompt_tokens":7,"completion_tokens":2}}'
    with endpoint(body=response) as (url,seen):
        env={'SILENTSHIFT_PROVIDER':provider,'SILENTSHIFT_MODEL':'synthetic-tool-model','SILENTSHIFT_API_KEY':'synthetic-test-key','SILENTSHIFT_LLM_BASE_URL':url}
        cfg=resolve_provider(env);r=forward(raw,cfg.public(),env,5)
    assert r['http_status']==200 and base64.b64decode(r['body_base64'])==response
    assert seen==[{'path':'/test/v1/chat/completions','body':raw,'authorization':'Bearer synthetic-test-key','accept_encoding':'identity'}]
    assert 'synthetic-test-key' not in json.dumps(r)


def test_redirect_does_not_forward_bearer_to_another_endpoint():
    with endpoint() as (destination,dest_seen):
        with endpoint(status=307,redirect=destination) as (url,seen):
            env={'SILENTSHIFT_PROVIDER':'openai','SILENTSHIFT_MODEL':'m','SILENTSHIFT_API_KEY':'synthetic-test-key','SILENTSHIFT_LLM_BASE_URL':url}
            r=forward(b'{}',resolve_provider(env).public(),env,5)
    assert r['error_code']=='PROVIDER_REDIRECT_REJECTED' and len(seen)==1 and dest_seen==[]


@pytest.mark.parametrize(('body','encoding','expected'),[(b'x'*(MAX_BYTES+1),None,'PROVIDER_RESPONSE_BOUNDS'),(b'compressed','gzip','PROVIDER_CONTENT_ENCODING_REJECTED')])
def test_response_is_bounded_before_any_relay(body,encoding,expected):
    with endpoint(body=body,encoding=encoding) as (url,_):
        env={'SILENTSHIFT_PROVIDER':'openai','SILENTSHIFT_MODEL':'m','SILENTSHIFT_API_KEY':'synthetic-test-key','SILENTSHIFT_LLM_BASE_URL':url}
        r=forward(b'{}',resolve_provider(env).public(),env,5)
    assert r['error_code']==expected and not r['body_base64']


def test_route_change_is_rejected_before_io_and_tls_verification_is_enabled():
    env={'SILENTSHIFT_PROVIDER':'openai','SILENTSHIFT_MODEL':'m','SILENTSHIFT_API_KEY':'synthetic-test-key'}
    cfg=resolve_provider(env)
    r=forward(b'{}',cfg.public(),{**env,'SILENTSHIFT_LLM_BASE_URL':'https://changed.example/v1/'},5)
    assert r['error_code']=='PROVIDER_ROUTE_CHANGED'
    context=ssl.create_default_context()
    assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
