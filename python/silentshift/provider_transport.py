"""Bounded, TLS-verified HTTP inside the native forwarding operation.

No redirects/retries, disk staging, or secret/content logging. The caller owns
native request/response tracing; credentials never enter that message body.
"""
from __future__ import annotations

import base64
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

MAX_BYTES=262144


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None


def forward(raw: bytes, config, env, timeout: int) -> dict:
    from .provider_config import resolve_provider
    current=resolve_provider(env)
    if current.public()!=config or current.transport!='stdlib-http':
        return {'error_code':'PROVIDER_ROUTE_CHANGED','http_status':502,'body_base64':'','response_bytes':0}
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_BYTES or not 1<=timeout<=125:
        return {'error_code':'PROVIDER_REQUEST_BOUNDS','http_status':502,'body_base64':'','response_bytes':0}
    headers={'Accept-Encoding':'identity','Accept':'application/json','Content-Type':'application/json; charset=utf-8'}
    headers['Authorization']='Bearer '+env['SILENTSHIFT_API_KEY']
    request=Request(current.base_url+'chat/completions',data=raw,headers=headers,method='POST')
    opener=build_opener(NoRedirects(),HTTPSHandler(context=ssl.create_default_context()))
    response=None
    try:
        try:
            response=opener.open(request,timeout=timeout)
        except HTTPError as error:
            response=error
        status=response.code
        encoding=response.headers.get('Content-Encoding','').lower().strip()
        if encoding not in {'','identity'}:
            return {'error_code':'PROVIDER_CONTENT_ENCODING_REJECTED','http_status':502,'upstream_http_status':status,'body_base64':'','response_bytes':0}
        length=response.headers.get('Content-Length')
        if length is not None and (not length.isdecimal() or int(length)>MAX_BYTES):
            return {'error_code':'PROVIDER_RESPONSE_BOUNDS','http_status':502,'upstream_http_status':status,'body_base64':'','response_bytes':0}
        body=response.read(MAX_BYTES+1)
        if len(body)>MAX_BYTES:
            return {'error_code':'PROVIDER_RESPONSE_BOUNDS','http_status':502,'upstream_http_status':status,'body_base64':'','response_bytes':0}
        if 300<=status<400:
            return {'error_code':'PROVIDER_REDIRECT_REJECTED','http_status':502,'upstream_http_status':status,'body_base64':'','response_bytes':0}
        return {'error_code':'UPSTREAM_HTTP_ERROR' if status>=400 else '', 'http_status':status,
            'upstream_http_status':status,'body_base64':base64.b64encode(body).decode('ascii'),'response_bytes':len(body)}
    except (OSError,ValueError,URLError):
        return {'error_code':'PROVIDER_TRANSPORT_FAILED','http_status':502,'body_base64':'','response_bytes':0}
    finally:
        if response is not None:
            response.close()
