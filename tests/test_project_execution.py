from __future__ import annotations

from api.agent_team_api import AgentTeamAPI
from api.http import create_app
from runtime import ManagerRuntime
from services.project_store import ProjectStore


def build_client(tmp_path):
    runtime = ManagerRuntime(
        database_path=str(tmp_path / "manager.db"),
        registry_path=str(tmp_path / "agents.json"),
    )
    api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
    store = ProjectStore(str(tmp_path / "platform.db"))
    app = create_app(api, runtime, project_store=store)
    app.config["TESTING"] = True
    return app.test_client()


def test_create_project_and_update_status(tmp_path):
    client = build_client(tmp_path)
    response = client.post(
        "/api/project/create",
        json={
            "name": "Demo",
            "description": "پروژه آزمایشی",
            "request": "یک صفحه معرفی ساده بساز",
            "project_type": "website",
        },
    )
    assert response.status_code == 201
    project = response.get_json()
    assert project["status"] == "created"

    response = client.post(
        f"/api/project/{project['id']}/status",
        json={"status": "planning"},
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "planning"


def test_project_execution_uses_runtime(tmp_path, monkeypatch):
    client = build_client(tmp_path)
    created = client.post(
        "/api/project/create",
        json={
            "name": "Runtime Demo",
            "description": "اجرای Runtime",
            "request": "درخواست تست",
        },
    ).get_json()

    class FakeReport:
        def to_dict(self):
            return {"status": "completed", "tasks": []}

    from api.http import create_app

    # Replace the runtime call at the application instance level without invoking providers.
    app_runtime = client.application.view_functions["run_project"].__closure__
    runtime_obj = None
    for cell in app_runtime or ():
        value = cell.cell_contents
        if hasattr(value, "run") and hasattr(value, "agent_team"):
            runtime_obj = value
            break
    assert runtime_obj is not None
    monkeypatch.setattr(runtime_obj, "run", lambda request, agent: FakeReport())

    response = client.post(f"/api/project/{created['id']}/run", json={"agent": "developer"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["report"]["status"] == "completed"
    assert payload["project"]["status"] == "completed"
