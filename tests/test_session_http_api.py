from __future__ import annotations

from api.http import create_app
from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


class FakeTeamAPI:
    def list_agents(self):
        return []

    def enable(self, name):
        return {"name": name, "enabled": True}

    def disable(self, name):
        return {"name": name, "enabled": False}


class FakeManagerRuntime:
    def __init__(self):
        self.requests = []

    def run(self, request: str):
        from manager.report import ManagerReport
        self.requests.append(request)
        return ManagerReport([])


def test_session_http_flow(tmp_path):
    manager_runtime = FakeManagerRuntime()
    session_runtime = SessionRuntime(
        sessions=UserSessionManager(str(tmp_path)),
        runtime=manager_runtime,
    )
    app = create_app(FakeTeamAPI(), runtime=manager_runtime, session_runtime=session_runtime)
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/api/session/start",
        json={"session_id": "s1", "request": "یک سایت بساز"},
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "waiting_for_user"
    assert response.get_json()["question"]

    response = client.post(
        "/api/session/s1/answer",
        json={"answer": "سایت وردپرسی خدمات ماهواره مرکزی"},
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "completed"
    assert len(manager_runtime.requests) == 1
    assert "خدمات ماهواره مرکزی" in manager_runtime.requests[0]

    response = client.get("/api/session/s1")
    assert response.status_code == 200
    assert response.get_json()["status"] == "completed"
    assert response.get_json()["output"] is not None


def test_session_http_rejects_invalid_payload(tmp_path):
    session_runtime = SessionRuntime(
        sessions=UserSessionManager(str(tmp_path)),
        runtime=FakeManagerRuntime(),
    )
    app = create_app(FakeTeamAPI(), session_runtime=session_runtime)
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post("/api/session/start", json={"session_id": "s1"})
    assert response.status_code == 400

    response = client.post("/api/session/s1/answer", json={"answer": "پاسخ"})
    assert response.status_code in {400, 404}
