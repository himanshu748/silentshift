"""Demo-boundary tests with an explicit fake upstream; not native IRIS evidence."""
from dataclasses import replace
import http.client
import json
from pathlib import Path
import sys
import threading
import uuid

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo_gateway.server import Config, Refused, Server, State


class NativeFixture:
    def __init__(self):
        self.calls = []
        self.fail = False

    def request(self, path, *, body=None, runner=False, portal=False):
        self.calls.append((path, body, runner, portal))
        return 200, "application/json", json.dumps({"read": True, "path": path}).encode()

    def case(self, path, *, body=None, runner=False):
        self.calls.append((path, body, runner, False))
        if self.fail: raise RuntimeError("private upstream diagnostic")
        return {"id": str(uuid.uuid4()), "routing": "QUARANTINED", "delivery_count": 0,
                "agent": {"status": "returned", "model_invoked": True}}


@pytest.fixture
def config(tmp_path):
    web = tmp_path/"web"; web.mkdir(); (web/"index.html").write_text('<title>Fixture</title>')
    return Config("http://127.0.0.1:0", "http://127.0.0.1:1/silentshift/api", "reader", "fixture-reader-value", "runner", "fixture-runner-value", "fixture-session-value", tmp_path/"state.sqlite", web, 20000)


@pytest.fixture
def state(config):
    s = State(config, NativeFixture(), clock=lambda: 1000)
    yield s
    s.close()


@pytest.fixture
def endpoint(state):
    server = Server(("127.0.0.1", 0), state)
    state.config = replace(state.config, origin=f"http://127.0.0.1:{server.server_port}")
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    def call(method, path, body=None, *, auth=False, origin=True, headers=None, raw=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        hs = {"Content-Type": "application/json"}
        if auth: hs["Authorization"] = state.config.authorization()
        if origin: hs["Origin"] = state.config.origin
        hs.update(headers or {})
        data = raw if raw is not None else json.dumps(body).encode() if body is not None else None
        connection.request(method, path, data, hs)
        response = connection.getresponse(); result = response.read(); fields = dict(response.getheaders()); status = response.status;connection.close()
        try: result=json.loads(result)
        except ValueError: pass
        return status, result, fields
    yield call
    server.shutdown();server.server_close();thread.join()


def test_native_upstream_cannot_be_an_arbitrary_url(config):
    with pytest.raises(ValueError): replace(config, upstream="https://example.com/silentshift/api")
    with pytest.raises(ValueError): replace(config, upstream="http://127.0.0.1:1/other")
    with pytest.raises(ValueError): replace(config, reader=config.runner)


@pytest.mark.parametrize("method,path", [
    ("POST","/api/messages"), ("POST","/api/cases/"+str(uuid.uuid4())+"/review"),
    ("POST","/api/imports/csv/commit"), ("POST","/api/evaluations"),
    ("DELETE","/api/cases"), ("PUT","/api/health"), ("PATCH","/api/cases"),
    ("POST","/csp/silentshift/EnsPortal.ProductionConfig.zen"),
    ("GET","/csp/sys/%25CSP.Portal.Home.zen"),
])
def test_non_demo_mutations_and_admin_routes_never_reach_upstream(endpoint, state, method, path):
    status, _, _ = endpoint(method, path, {}, auth=True)
    assert status in {400,403,405}
    assert state.native.calls == []


def test_reader_authentication_and_separate_runner_are_enforced(endpoint, state):
    assert endpoint("GET", "/api/health")[0] == 401
    status, result, _ = endpoint("GET", "/api/health", auth=True)
    assert status == 200 and result["read"]
    assert state.native.calls == [("/health",None,False,False)]
    status, public, _ = endpoint("GET", "/demo/access")
    assert status == 200 and public["username"] == state.config.reader
    assert state.config.runner_password not in json.dumps(public)
    assert state.config.session_secret not in json.dumps(public)


@pytest.mark.parametrize("path", ["/api/cases?limit=51", "/api/cases?offset=2001", "/api/cases?method=delete", "/api/cases?limit=2&limit=3", "/../runtime.env", "/.env", "//elsewhere.invalid/api/health"])
def test_traversal_and_query_bounds(endpoint, state, path):
    assert endpoint("GET", path, auth=True)[0] in {400,404}
    assert state.native.calls == []


def test_preview_remains_read_only_and_preserves_json_content_type(endpoint, state):
    status, result, headers = endpoint("POST", "/api/imports/csv/preview", {"synthetic":"fixture"}, auth=True)
    assert status == 200 and result["read"]
    assert headers["Content-Type"] == "application/json"
    assert state.native.calls[-1][2] is False


def visitor(endpoint):
    status, value, headers = endpoint("GET", "/demo/session")
    assert status == 200
    return {"Cookie":headers["Set-Cookie"].split(";",1)[0], "X-Demo-CSRF":value["csrf"]}


def test_cross_origin_missing_session_and_extra_fields_cannot_dispatch(endpoint, state):
    headers=visitor(endpoint); body={"scenario":"quantity-mismatch","request_id":str(uuid.uuid4())}
    assert endpoint("POST","/demo/run",body,headers=headers,origin=False)[0] == 403
    assert endpoint("POST","/demo/run",body)[0] == 403
    assert endpoint("POST","/demo/run",{**body,"prompt":"replace evidence"},headers=headers)[0] == 400
    assert endpoint("POST","/demo/run",{**body,"scenario":"arbitrary-feed"},headers=headers)[0] == 400
    assert endpoint("POST","/demo/run",headers=headers,raw=b'{"scenario":1,"scenario":2}')[0] == 400
    assert state.native.calls == []


def test_same_request_is_not_redispatched_and_reset_retains_history(endpoint, state):
    hs=visitor(endpoint);body={"scenario":"quantity-mismatch","request_id":str(uuid.uuid4())}
    status, data, _=endpoint("POST","/demo/run",body,headers=hs);assert status==202
    done=state.wait(data["job"]["id"]);assert done["state"]=="completed"
    status, repeated, _=endpoint("POST","/demo/run",body,headers=hs)
    assert status==202 and repeated["job"]["id"]==done["id"]
    assert len(state.native.calls)==1
    assert endpoint("POST","/demo/reset",{},headers=hs)[0]==200
    assert endpoint("GET","/demo/status",headers=hs)[1]["job"] is None
    assert state.db.execute("SELECT count(*) FROM jobs").fetchone()[0]==1


def test_concurrent_admission_has_one_lease(state):
    barrier=threading.Barrier(3); results=[]
    def reserve():
        barrier.wait()
        try:results.append(state.reserve("actor",str(uuid.uuid4()),"127.0.0.1","quantity-mismatch"))
        except Refused as e:results.append(e.code)
    threads=[threading.Thread(target=reserve) for _ in range(2)]
    for t in threads:t.start()
    barrier.wait()
    for t in threads:t.join()
    assert sum(isinstance(x,tuple) for x in results)==1
    assert "INVESTIGATION_BUSY" in results


def test_reset_cannot_bypass_per_ip_quota(endpoint, state):
    hs=visitor(endpoint)
    for _ in range(2):
        _, result, _=endpoint("POST","/demo/run",{"scenario":"quantity-mismatch","request_id":str(uuid.uuid4())},headers=hs)
        state.wait(result["job"]["id"])
        assert endpoint("POST","/demo/reset",{},headers=hs)[0]==200
    assert endpoint("POST","/demo/run",{"scenario":"approved-amendment","request_id":str(uuid.uuid4())},headers=hs)[0]==429
    assert len(state.native.calls)==2


def test_uncertain_call_is_retained_and_blocks_reset_and_new_model_calls(endpoint,state):
    state.native.fail=True;hs=visitor(endpoint)
    _, result, _=endpoint("POST","/demo/run",{"scenario":"quantity-mismatch","request_id":str(uuid.uuid4())},headers=hs)
    assert state.wait(result["job"]["id"])["state"]=="uncertain"
    assert endpoint("POST","/demo/reset",{},headers=hs)[0]==409
    status, value, _=endpoint("POST","/demo/run",{"scenario":"approved-amendment","request_id":str(uuid.uuid4())},headers=hs)
    assert status==409 and "private upstream diagnostic" not in json.dumps(value)
    assert len(state.native.calls)==1


def test_restart_retains_uncertain_reservation(config):
    state=State(config,NativeFixture(),clock=lambda:1000)
    job,_=state.reserve("actor",str(uuid.uuid4()),"ip","quantity-mismatch");state.close()
    recovered=State(config,NativeFixture(),clock=lambda:1000)
    try:
        assert recovered.wait(job["id"])["state"]=="uncertain"
        with pytest.raises(Refused): recovered.reserve("another",str(uuid.uuid4()),"ip2","approved-amendment")
        assert recovered.native.calls==[]
    finally:recovered.close()


def test_closing_window_and_whole_trial_bound(state):
    state.config=replace(state.config,expires_at=1100)
    with pytest.raises(Refused,match="closing"):state.reserve("actor",str(uuid.uuid4()),"ip","quantity-mismatch")
    state.config=replace(state.config,expires_at=20000,max_runs=1)
    job,_=state.reserve("actor",str(uuid.uuid4()),"ip","quantity-mismatch");state.dispatch(job["id"]);state.wait(job["id"])
    with pytest.raises(Refused) as error:state.reserve("another",str(uuid.uuid4()),"ip2","quantity-mismatch")
    assert error.value.code=="TRIAL_LIMIT"


@pytest.mark.parametrize("expiry", [float("inf"), float("nan"), float("-inf")])
def test_expiry_must_be_finite(config, expiry):
    with pytest.raises(ValueError, match="Finite"): replace(config, expires_at=expiry)


def test_extra_scenario_path_components_cannot_dispatch(endpoint, state):
    status, _, _ = endpoint("POST", "/api/scenarios/quantity-mismatch/extra/run", {"run_id":str(uuid.uuid4())}, auth=True)
    assert status == 403
    assert state.native.calls == []
