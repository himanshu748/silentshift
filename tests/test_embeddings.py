"""Check the optional embedding trust boundary, without model or network calls."""
import io
import json
from unittest.mock import patch

import pytest
from silentshift.embeddings import encode, local_endpoint


@pytest.mark.parametrize("route", [
    "https://example.com", "http://example.com:11434", "http://127.0.0.1:80",
    "http://user:password@localhost:11434", "http://localhost:11434/?key=x",
    "http://localhost:11434/other", "http://localhost:11434/#secret",
])
def test_unapproved_embedding_route_never_reaches_transport(route):
    with patch("silentshift.embeddings.build_opener") as opener:
        with pytest.raises(ValueError, match="LOCAL_EMBEDDING_ROUTE_REQUIRED"):
            encode(["business procedure"], route, "all-minilm:22m")
        opener.assert_not_called()


def test_local_route_strips_compatible_v1_suffix():
    assert local_endpoint("http://host.lima.internal:11434/v1/") == "http://host.lima.internal:11434/api/embed"


def reply(payload):
    return io.BytesIO(json.dumps(payload).encode())


@pytest.mark.parametrize("payload", [
    {"model": "other-model", "embeddings": [[1.0] * 384]},
    {"model": "all-minilm:22m", "embeddings": [[1.0] * 383]},
    {"model": "all-minilm:22m", "embeddings": [[True] * 384]},
    {"model": "all-minilm:22m", "embeddings": [[0.0] * 384]},
    {"model": "all-minilm:22m", "embeddings": [[float("nan")] * 384]},
    {"model": "all-minilm:22m", "embeddings": [[1e308] * 384]},
    {"model": "all-minilm:22m", "embeddings": []},
])
def test_unusable_model_output_cannot_be_saved_as_vectors(payload):
    with patch("silentshift.embeddings.build_opener") as opener:
        opener.return_value.open.return_value = reply(payload)
        with pytest.raises(ValueError, match="^LOCAL_EMBEDDING_UNAVAILABLE$"):
            encode(["business procedure"], "http://localhost:11434", "all-minilm:22m")


def test_valid_vector_is_preserved_and_silent_truncation_is_disabled():
    vector = [0.1] * 384
    with patch("silentshift.embeddings.build_opener") as opener:
        opener.return_value.open.return_value = reply({"model": "all-minilm:22m", "embeddings": [vector]})
        actual = encode(["business procedure"], "http://localhost:11434", "all-minilm:22m")
        request = opener.return_value.open.call_args.args[0]
        assert json.loads(request.data)["truncate"] is False
        assert actual["vectors"] == [vector]
        assert actual["dimensions"] == 384


def test_transport_diagnostics_cannot_escape_into_native_audit():
    with patch("silentshift.embeddings.build_opener") as opener:
        opener.return_value.open.side_effect = OSError("private request content")
        with pytest.raises(ValueError, match="^LOCAL_EMBEDDING_UNAVAILABLE$"):
            encode(["business procedure"], "http://localhost:11434", "all-minilm:22m")
