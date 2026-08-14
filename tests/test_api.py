from __future__ import annotations

from api.agent_team_api import AgentTeamAPI
from api.http import create_app
from runtime import ManagerRuntime


def build_client(tmp_path):
    runtime = ManagerRuntime(
        database_path=str(tmp_path / "manager.db"),
        registry_path=str(tmp_path / "agents.json"),
    )
    api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
    app = create_app(api, runtime)
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
