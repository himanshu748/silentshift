"""Loopback-only demo gateway. All investigation and policy work stays in IRIS.

The public reader and private fixed-scenario runner are separate native users.
No arbitrary message intake, review, import commit, SQL or production control is
proxied. SQLite records admission before dispatch; uncertain calls are not retried.
"""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import hashlib
import hmac
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

SCENARIOS = {"quantity-mismatch", "currency-scaling", "approved-amendment", "conflicting-references", "unsafe-agent-output"}
UUID = re.compile(r"[A-Fa-f0-9]{8}(?:-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12}\Z")
API_READS = {"health", "overview", "cases", "reviews", "scenarios", "policies", "evaluations"}
PORTAL_PAGES = {"EnsPortal.VisualTrace.zen", "EnsPortal.MessageContents.zen", "EnsPortal.SVG.VisualTrace.cls"}


class Refused(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def strict_json(raw: bytes):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError("Duplicate field")
            result[k] = v
        return result
    def invalid(_):
        raise ValueError("Non-finite number")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


@dataclass(frozen=True)
class Config:
    origin: str
    upstream: str
    reader: str
    reader_password: str
    runner: str
    runner_password: str
    session_secret: str
    database: Path
    web_root: Path
    expires_at: float
    max_runs: int = 30
    runs_per_ip: int = 2
    run_window_seconds: int = 600

    def __post_init__(self):
        o, u = urlsplit(self.origin), urlsplit(self.upstream)
        if not o.hostname or o.scheme not in {"http", "https"} or o.path not in {"", "/"} or o.username or o.password or o.query or o.fragment:
            raise ValueError("Explicit public origin required")
        if u.scheme != "http" or u.hostname not in {"127.0.0.1", "localhost"} or u.path != "/silentshift/api" or u.username or u.password or u.query or u.fragment:
            raise ValueError("Native gateway must be explicit loopback HTTP")
        if self.reader == self.runner or min(len(self.reader_password), len(self.runner_password), len(self.session_secret)) < 16:
            raise ValueError("Distinct native accounts and private configuration required")
        if not math.isfinite(self.expires_at):
            raise ValueError("Finite trial expiry required")
        if not 1 <= self.max_runs <= 100 or not 1 <= self.runs_per_ip <= 5:
            raise ValueError("Admission bounds required")

    @classmethod
    def environment(cls):
        return cls(*(os.environ[n] for n in ("DEMO_ORIGIN", "DEMO_UPSTREAM", "DEMO_READER", "DEMO_READER_PASSWORD", "DEMO_RUNNER", "DEMO_RUNNER_PASSWORD", "DEMO_SESSION_SECRET")),
                   Path(os.environ["DEMO_DATABASE"]), Path(os.environ["DEMO_WEB_ROOT"]), float(os.environ["DEMO_EXPIRES_AT"]))

    def authorization(self, runner=False):
        user, password = (self.runner, self.runner_password) if runner else (self.reader, self.reader_password)
        return "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        raise Refused(502, "UPSTREAM_REDIRECT", "Native redirect is not permitted.")


class Native:
    def __init__(self, config):
        self.config = config
        self.opener = build_opener(NoRedirect())

    def request(self, path, *, body=None, runner=False, portal=False):
        if runner and not re.fullmatch(r"/scenarios/(?:" + "|".join(SCENARIOS) + r")/run", path):
            raise ValueError("Runner can dispatch only fixed native scenarios")
        base = self.config.upstream.removesuffix("/silentshift/api") if portal else self.config.upstream
        headers = {"Accept": "application/json" if not portal else "*/*", "Authorization": self.config.authorization(runner),
                   "Host": urlsplit(self.config.origin).netloc, "X-Forwarded-Proto": urlsplit(self.config.origin).scheme}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(base + path, data=None if body is None else json.dumps(body).encode(), headers=headers)
        try:
            response = self.opener.open(request, timeout=170 if runner else 20)
        except HTTPError as exc:
            response = exc
        with response:
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise Refused(502, "UPSTREAM_SIZE", "Native response exceeded the demo bound.")
            return response.status, response.headers.get("Content-Type", "application/octet-stream"), raw

    def case(self, path, *, body=None, runner=False):
        status, kind, raw = self.request(path, body=body, runner=runner)
        if status != 200 or "json" not in kind:
            raise Refused(502, "NATIVE_UNAVAILABLE", "The native operation did not return a usable result.")
        value = strict_json(raw)
        if not isinstance(value, dict):
            raise ValueError("Native object required")
        return value


class State:
    def __init__(self, config, native=None, clock=time.time):
        self.config, self.native, self.clock = config, native or Native(config), clock
        self.lock = threading.RLock()
        config.database.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(config.database, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, current_job TEXT, created REAL);
          CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, actor TEXT, request_id TEXT, ip TEXT,
             scenario TEXT, run_id TEXT, state TEXT, created REAL, finished REAL, result TEXT,
             UNIQUE(actor,request_id));
        """)
        # A restarted gateway never redispatches an unconfirmed native call.
        self.db.execute("UPDATE jobs SET state='uncertain' WHERE state='running'")
        self.db.commit()
        os.chmod(config.database, 0o600)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.futures = {}
        self.read_rates = {}

    def close(self):
        self.executor.shutdown(wait=True)
        self.db.close()

    def token(self, value):
        return hmac.new(self.config.session_secret.encode(), value.encode(), hashlib.sha256).hexdigest()

    def session(self, value):
        with self.lock:
            row = self.db.execute("SELECT * FROM sessions WHERE id=?", (value or "",)).fetchone()
            if row:
                return dict(row)
            if self.db.execute("SELECT count(*) FROM sessions").fetchone()[0] >= 1024:
                raise Refused(429, "DEMO_CAPACITY", "The trial session limit has been reached.")
            value = secrets.token_urlsafe(24)
            self.db.execute("INSERT INTO sessions VALUES(?,NULL,?)", (value, self.clock()))
            self.db.commit()
            return {"id": value, "current_job": None}

    def read_limit(self, ip):
        with self.lock:
            now = self.clock()
            self.read_rates = {k: v for k, v in self.read_rates.items() if now - v[0] < 60}
            if ip not in self.read_rates and len(self.read_rates) >= 1024:
                raise Refused(429, "DEMO_CAPACITY", "Please try again later.")
            start, count = self.read_rates.get(ip, (now, 0))
            if count >= 240:
                raise Refused(429, "READ_LIMIT", "Please wait before refreshing again.")
            self.read_rates[ip] = (start, count + 1)

    def public_job(self, row):
        if row is None:
            return None
        return {"id": row["id"], "scenario": row["scenario"], "state": row["state"], "created": row["created"],
                "finished": row["finished"], "result": json.loads(row["result"]) if row["result"] else None}

    def status(self, session):
        with self.lock:
            return self.public_job(self.db.execute("SELECT * FROM jobs WHERE id=(SELECT current_job FROM sessions WHERE id=?)", (session,)).fetchone())

    def reserve(self, actor, request_id, ip, scenario, session=None):
        if scenario not in SCENARIOS or not isinstance(request_id, str) or not UUID.fullmatch(request_id):
            raise Refused(400, "FIXED_SAMPLE_REQUIRED", "Choose a fixed synthetic sample.")
        with self.lock:
            existing = self.db.execute("SELECT * FROM jobs WHERE actor=? AND request_id=?", (actor, request_id)).fetchone()
            if existing:
                if existing["scenario"] != scenario:
                    raise Refused(409, "REQUEST_REUSED", "This request already names another sample.")
                return self.public_job(existing), False
            now = self.clock()
            if now >= self.config.expires_at - 180:
                raise Refused(503, "TRIAL_ENDING", "The timed trial is closing; no new investigation was admitted.")
            if self.db.execute("SELECT count(*) FROM jobs WHERE state IN ('running','uncertain')").fetchone()[0]:
                raise Refused(409, "INVESTIGATION_BUSY", "An investigation is running or awaiting reconciliation. No new run was admitted.")
            if self.db.execute("SELECT count(*) FROM jobs").fetchone()[0] >= self.config.max_runs:
                raise Refused(429, "TRIAL_LIMIT", "The trial investigation limit has been reached.")
            if self.db.execute("SELECT count(*) FROM jobs WHERE ip=? AND created>?", (ip, now-self.config.run_window_seconds)).fetchone()[0] >= self.config.runs_per_ip:
                raise Refused(429, "INVESTIGATION_LIMIT", "This address has reached its demo-run limit. Existing cases remain readable.")
            job = str(uuid.uuid4())
            self.db.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,'running',?,NULL,NULL)", (job, actor, request_id, ip, scenario, str(uuid.uuid4()), now))
            if session:
                self.db.execute("UPDATE sessions SET current_job=? WHERE id=?", (job, session))
            self.db.commit()
            return self.public_job(self.db.execute("SELECT * FROM jobs WHERE id=?", (job,)).fetchone()), True

    def dispatch(self, job):
        with self.lock:
            self.futures[job] = self.executor.submit(self._investigate, job)

    def _investigate(self, job):
        with self.lock:
            row = dict(self.db.execute("SELECT * FROM jobs WHERE id=?", (job,)).fetchone())
        try:
            result = self.native.case(f"/scenarios/{row['scenario']}/run", body={"run_id": row["run_id"]}, runner=True)
            deadline = self.clock() + 30
            while result.get("routing") == "PROCESSING" and self.clock() < deadline:
                time.sleep(1)
                case_id = result.get("id", "")
                if not UUID.fullmatch(case_id):
                    raise ValueError("Native case id required")
                result = self.native.case("/cases/"+case_id)
            if result.get("routing") not in {"QUARANTINED", "DELIVERED", "REVIEW"} or not UUID.fullmatch(result.get("id", "")):
                raise ValueError("Terminal persisted native case required")
            state = "completed"
        except Exception:
            state, result = "uncertain", None
        with self.lock:
            self.db.execute("UPDATE jobs SET state=?,finished=?,result=? WHERE id=?", (state, self.clock(), json.dumps(result) if result else None, job))
            self.db.commit()

    def wait(self, job, timeout=175):
        future = self.futures.get(job)
        if future:
            try:
                future.result(timeout=timeout)
            except TimeoutError:
                pass
        with self.lock:
            return self.public_job(self.db.execute("SELECT * FROM jobs WHERE id=?", (job,)).fetchone())

    def reset(self, session):
        with self.lock:
            current = self.status(session)
            if current and current["state"] != "completed":
                raise Refused(409, "KEEP_UNCONFIRMED_RESULT", "Reset cannot hide a running or uncertain investigation.")
            self.db.execute("UPDATE sessions SET current_job=NULL WHERE id=?", (session,))
            self.db.commit()


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, state):
        self.state = state
        self.slots = threading.BoundedSemaphore(32)
        super().__init__(address, Handler)

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        super().process_request(request, address)

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    server_version = "SilentShiftDemo"

    def log_message(self, *_):
        # Never log authorization, credentials, cookies, query strings or bodies.
        pass

    def do_GET(self): self.handle_request()
    def do_POST(self): self.handle_request()
    def do_PUT(self): self.handle_request()
    def do_DELETE(self): self.handle_request()
    def do_PATCH(self): self.handle_request()
    def do_OPTIONS(self): self.handle_request()

    def send(self, status, raw, kind="application/json", cookie=None):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        if status == 401:
            self.send_header("WWW-Authenticate", 'Basic realm="SilentShift read-only demo"')
        if status == 429:
            self.send_header("Retry-After", "600")
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def json(self, value, status=200, cookie=None):
        self.send(status, json.dumps(value, allow_nan=False).encode(), cookie=cookie)

    def authenticated(self):
        if not hmac.compare_digest(self.headers.get("Authorization", ""), self.server.state.config.authorization()):
            raise Refused(401, "AUTHENTICATION_REQUIRED", "Use the dedicated read-only viewer credentials from the guided demo, not a personal IRIS password.")

    def body(self):
        if self.headers.get("Transfer-Encoding") or self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
            raise Refused(400, "JSON_REQUIRED", "A bounded JSON request is required.")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not lengths[0].isdigit() or not 0 < int(lengths[0]) <= 262144:
            raise Refused(413, "REQUEST_BOUND", "The demo request is outside its size bound.")
        try:
            return strict_json(self.rfile.read(int(lengths[0])))
        except (ValueError, UnicodeError, RecursionError):
            raise Refused(400, "INVALID_JSON", "Strict JSON is required.") from None

    def origin(self):
        if self.headers.get("Origin") != self.server.state.config.origin.rstrip("/"):
            raise Refused(403, "ORIGIN_REQUIRED", "Use the same-origin demo page.")

    def visitor(self):
        cookie = SimpleCookie()
        try: cookie.load(self.headers.get("Cookie", ""))
        except Exception: pass
        value = cookie["ss_demo"].value if "ss_demo" in cookie else None
        session = self.server.state.session(value)
        return session, "ss_demo="+session["id"]+"; Path=/demo/; HttpOnly; SameSite=Strict" + ("; Secure" if self.server.state.config.origin.startswith("https:") else "")

    def handle_request(self):
        state, config = self.server.state, self.server.state.config
        try:
            self.connection.settimeout(20)
            if self.headers.get("Host") != urlsplit(config.origin).netloc:
                raise Refused(400, "HOST_REQUIRED", "Use the configured demo address.")
            parts = urlsplit(self.path)
            if parts.scheme or parts.netloc or "%" in parts.path or "\\" in parts.path or any(p.startswith(".") for p in parts.path.split("/") if p):
                raise Refused(400, "PATH_REFUSED", "Unsupported demo path.")
            ip = self.client_address[0]
            if ip in {"127.0.0.1", "::1"}:
                import ipaddress
                forwarded = self.headers.get("X-Forwarded-For", "")
                if forwarded:
                    ip = str(ipaddress.ip_address(forwarded))
            state.read_limit(ip)
            path = parts.path
            if self.command == "GET" and path in {"/demo/session", "/demo/status"}:
                visitor, cookie = self.visitor()
                return self.json({"csrf": state.token(visitor["id"]), "job": state.status(visitor["id"]), "expires_at": config.expires_at,
                                  "limits": {"runs_per_address": config.runs_per_ip, "window_seconds": config.run_window_seconds, "trial_runs": config.max_runs}}, cookie=cookie)
            if self.command == "GET" and path == "/demo/access":
                # Deliberately public, synthetic-only READ account, never the runner/admin.
                return self.json({"username": config.reader, "password": config.reader_password, "scope": "Read-only synthetic workspace and native portal; no review or production-control rights."})
            if self.command == "POST" and path in {"/demo/run", "/demo/reset"}:
                self.origin()
                visitor, _ = self.visitor()
                if not hmac.compare_digest(self.headers.get("X-Demo-CSRF", ""), state.token(visitor["id"])):
                    raise Refused(403, "DEMO_SESSION_REQUIRED", "Reload the guided demo before starting a sample.")
                data = self.body()
                if path.endswith("reset"):
                    if data != {}: raise Refused(400, "EMPTY_RESET_REQUIRED", "Reset only clears the journey selection.")
                    state.reset(visitor["id"])
                    return self.json({"reset": True, "native_history_deleted": False})
                if not isinstance(data, dict) or set(data) != {"scenario", "request_id"}:
                    raise Refused(400, "FIXED_SAMPLE_REQUIRED", "Only a fixed sample and request identity are accepted.")
                job, fresh = state.reserve("visitor:"+visitor["id"], data["request_id"], ip, data["scenario"], visitor["id"])
                if fresh: state.dispatch(job["id"])
                return self.json({"job": job}, 202)
            if path.startswith("/api/"):
                self.authenticated()
                sub = path.removeprefix("/api/")
                if self.command == "GET" and (sub in API_READS or sub.startswith("cases/") and UUID.fullmatch(sub[6:])):
                    query = parse_qs(parts.query, keep_blank_values=True)
                    if set(query)-{"limit", "offset"} or any(len(v)!=1 or not v[0].isdigit() for v in query.values()):
                        raise Refused(400, "QUERY_BOUND", "Only bounded pagination is supported.")
                    if int(query.get("limit", ["50"])[0]) > 50 or int(query.get("offset", ["0"])[0]) > 2000:
                        raise Refused(400, "QUERY_BOUND", "Pagination exceeds the demo bound.")
                    status, kind, raw = state.native.request("/"+sub+("?"+urlencode({k:v[0] for k,v in query.items()}) if query else ""))
                    return self.send(status, raw, kind)
                if self.command == "POST" and sub == "imports/csv/preview":
                    self.origin()
                    status, kind, raw = state.native.request("/imports/csv/preview", body=self.body())
                    return self.send(status, raw, kind)
                if self.command == "POST" and re.fullmatch(r"scenarios/[a-z-]+/run", sub):
                    self.origin()
                    scenario = sub.split("/")[1]
                    data = self.body()
                    if not isinstance(data, dict) or set(data) != {"run_id"}:
                        raise Refused(400, "FIXED_SAMPLE_REQUIRED", "A fixed sample run identity is required.")
                    job, fresh = state.reserve("reader:"+state.token(ip), data["run_id"], ip, scenario)
                    if fresh: state.dispatch(job["id"])
                    job = state.wait(job["id"])
                    if job["state"] != "completed": raise Refused(503, "UNCERTAIN_NATIVE_RESULT", "Native completion is unconfirmed; no automatic retry or new run was admitted.")
                    return self.json(job["result"])
                raise Refused(403, "READ_ONLY_DEMO", "Only fixed, bounded sample runs and read-only inspection are available. Arbitrary intake, review and import commits are disabled.")
            if path.startswith("/csp/"):
                name = path.removeprefix("/csp/silentshift/")
                asset = path.startswith(("/csp/broker/", "/csp/silentshift/")) and bool(re.fullmatch(r"[A-Za-z0-9_./-]+\.(?:js|css|png|gif|svg|ico|woff2?)", path))
                if self.command != "GET" or not (name in PORTAL_PAGES or asset):
                    raise Refused(403, "READ_ONLY_PORTAL", "Only the read-only production and trace pages are exposed.")
                status, kind, raw = state.native.request(path+("?"+parts.query if parts.query else ""), portal=True)
                return self.send(status, raw, kind)
            if self.command != "GET": raise Refused(405, "METHOD_REFUSED", "This demo route is read-only.")
            if path in {"/demo", "/demo/"}:
                html = (Path(__file__).parent/"start.html").read_text()
                entry = (config.web_root/"index.html").read_text()
                css = re.findall(r'<link[^>]+href="([^"]+\.css)"', entry)
                html = html.replace("<!-- APP_STYLES -->", "\n".join('<link rel="stylesheet" href="'+v+'">' for v in css))
                return self.send(200, html.encode(), "text/html; charset=utf-8")
            if path in {"/demo/client.js", "/demo/demo.css"}:
                file = Path(__file__).parent/path.rsplit("/",1)[1]
            else:
                file = config.web_root/path.lstrip("/")
                if path.endswith("/"): file /= "index.html"
                if not path.endswith("/") and (file/"index.html").is_file():
                    self.send_response(308);self.send_header("Location",path+"/");self.end_headers();return
                if not file.resolve().is_relative_to(config.web_root.resolve()) or file.is_symlink():
                    raise Refused(404, "NOT_FOUND", "No such demo asset.")
            if not file.is_file() or file.stat().st_size > 10_000_000:
                raise Refused(404, "NOT_FOUND", "No such demo asset.")
            return self.send(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or "application/octet-stream")
        except Refused as exc:
            return self.json({"error": {"code": exc.code, "message": exc.message}}, exc.status)
        except Exception:
            return self.json({"error": {"code": "DEMO_UNAVAILABLE", "message": "The demo could not complete this request. No private diagnostic or automatic retry is exposed."}}, 503)


def main():
    state = State(Config.environment())
    server = Server(("127.0.0.1", int(os.environ.get("DEMO_PORT", "8090"))), state)
    try: server.serve_forever()
    finally: server.server_close();state.close()


if __name__ == "__main__": main()
