from __future__ import annotations

from types import SimpleNamespace

from api.agent_team_api import AgentTeamAPI
from api.http import create_app
from manager.auth import APIAuthenticator
from runtime import ManagerRuntime


def build_client(tmp_path, authenticator=None):
    runtime = ManagerRuntime(
        database_path=str(tmp_path / "manager.db"),
        registry_path=str(tmp_path / "agents.json"),
    )
    api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
    app = create_app(api, runtime, authenticator=authenticator)
    app.config["TESTING"] = True
    return app.test_client(), runtime


def test_health(tmp_path):
    client, _ = build_client(tmp_path)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_list_agents(tmp_path):
    client, _ = build_client(tmp_path)
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_disable_and_enable_agent(tmp_path):
    client, runtime = build_client(tmp_path)
    assert runtime.governance.can_use("developer")

    response = client.post("/api/agents/developer/disable")
    assert response.status_code == 200
    assert not runtime.governance.can_use("developer")

    response = client.post("/api/agents/developer/enable")
    assert response.status_code == 200
    assert runtime.governance.can_use("developer")


def test_run_requires_request(tmp_path):
    client, _ = build_client(tmp_path)
    response = client.post("/api/run", json={})
    assert response.status_code == 400


def test_run_without_agent_preserves_automatic_routing(tmp_path):
    client, runtime = build_client(tmp_path)
    calls = []
    runtime.run = lambda request_text, agent=None: (
        calls.append((request_text, agent)) or SimpleNamespace(to_dict=lambda: {"ok": True})
    )

    response = client.post("/api/run", json={"request": "این کد را اصلاح کن"})

    assert response.status_code == 200
    assert calls == [("این کد را اصلاح کن", None)]


def test_run_with_explicit_agent_preserves_agent(tmp_path):
    client, runtime = build_client(tmp_path)
    calls = []
    runtime.run = lambda request_text, agent=None: (
        calls.append((request_text, agent)) or SimpleNamespace(to_dict=lambda: {"ok": True})
    )

    response = client.post("/api/run", json={"request": "تست پروژه", "agent": "qa"})

    assert response.status_code == 200
    assert calls == [("تست پروژه", "qa")]


def test_protected_api_requires_key(tmp_path):
    auth = APIAuthenticator.__new__(APIAuthenticator)
    auth.environment_name = "TEST_KEY"
    auth.api_key = "secret"
    client, _ = build_client(tmp_path, authenticator=auth)

    assert client.get("/api/agents").status_code == 401
    assert client.get("/api/agents", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/api/agents", headers={"X-API-Key": "secret"}).status_code == 200
    assert client.get("/api/health").status_code == 200


def test_run_rejects_oversized_request(tmp_path):
    client, _ = build_client(tmp_path)
    from api import http as http_module
    old = http_module.MAX_REQUEST_LENGTH
    http_module.MAX_REQUEST_LENGTH = 10
    try:
        response = client.post("/api/run", json={"request": "x" * 11})
        assert response.status_code == 413
    finally:
        http_module.MAX_REQUEST_LENGTH = old
