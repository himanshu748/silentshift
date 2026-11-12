"""Loopback-only fake provider. No model, credentials or outgoing requests."""
import http.server
import json
from pathlib import Path

LOG = Path("/tmp/stream-mock-requests.jsonl")

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.reply({"id": "mock-model", "object": "model", "owned_by": "local"})

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with LOG.open("a") as f:
            f.write(json.dumps({"path": self.path, "body": req}) + "\n")
        seen_tool = any(m.get("role") == "tool" for m in req.get("messages", []))
        if seen_tool:
            msg = {"role": "assistant", "content": "Mock completion after captured tool result."}
            finish = "stop"
        else:
            msg = {"role": "assistant", "content": None,
                   "tool_calls": [{"id": "call-stream", "type": "function",
                                   "function": {"name": "ReturnStream", "arguments": "{}"}}]}
            finish = "tool_calls"
        self.reply({"id": "local-stream-repro", "object": "chat.completion", "created": 0,
                    "model": "mock-model", "choices": [{"index": 0, "message": msg,
                                                          "finish_reason": finish}],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}})

http.server.HTTPServer(("127.0.0.1", 8123), Handler).serve_forever()
