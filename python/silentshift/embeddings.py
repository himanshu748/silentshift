"""Bounded local embeddings for procedural guidance, never release authority."""
from __future__ import annotations

import json
import math
import re
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

DIMENSIONS = 384
LOCAL_HOSTS = {"localhost", "127.0.0.1", "host.lima.internal", "host.docker.internal", "ollama"}


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_endpoint(base_url: str) -> str:
    try:
        url = urlsplit(base_url)
        if (url.scheme != "http" or url.hostname not in LOCAL_HOSTS or url.port != 11434
                or url.username or url.password or url.query or url.fragment
                or url.path not in {"", "/", "/v1", "/v1/"}):
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("LOCAL_EMBEDDING_ROUTE_REQUIRED") from None
    return f"http://{url.netloc}/api/embed"


def encode(texts: list[str], base_url: str, model: str) -> dict:
    endpoint = local_endpoint(base_url)
    if not isinstance(model, str) or not re.fullmatch(r"[a-zA-Z0-9_.:/-]{1,120}", model):
        raise ValueError("INVALID_EMBEDDING_MODEL")
    if (not isinstance(texts, list) or not 1 <= len(texts) <= 16
            or any(not isinstance(text, str) or not text.strip() or len(text) > 1800 for text in texts)):
        raise ValueError("INVALID_EMBEDDING_INPUT")
    body = json.dumps({"model": model, "input": texts, "truncate": False}, allow_nan=False).encode()
    if len(body) > 24_000:
        raise ValueError("EMBEDDING_INPUT_LIMIT")
    started = time.monotonic()
    request = Request(endpoint, body, {"Content-Type": "application/json"}, method="POST")
    try:
        with build_opener(NoRedirects()).open(request, timeout=8) as response:
            raw = response.read(200_001)
        if len(raw) > 200_000:
            raise ValueError
        result = json.loads(raw)
        if not isinstance(result, dict) or result.get("model") != model:
            raise ValueError
        vectors = result.get("embeddings") if isinstance(result, dict) else None
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise ValueError
        for vector in vectors:
            if (not isinstance(vector, list) or len(vector) != DIMENSIONS
                    or any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) for x in vector)
                    or not math.isfinite(sum(x * x for x in vector))
                    or sum(x * x for x in vector) <= 0):
                raise ValueError
        return {"model": model, "dimensions": DIMENSIONS, "vectors": vectors,
                "elapsed_ms": round((time.monotonic() - started) * 1000, 3)}
    except Exception:
        # Never propagate HTTP bodies, text, environment values or transport
        # exception details through the native error/audit path.
        raise ValueError("LOCAL_EMBEDDING_UNAVAILABLE") from None
