from pathlib import Path

from api.http import create_app


class FakeTeamAPI:
    def list_agents(self):
        return []

    def enable(self, name):
        return {"name": name, "enabled": True}

    def disable(self, name):
        return {"name": name, "enabled": False}


class FakeSessionManager:
    def __init__(self):
        self.sessions = {}

    def start(self, session_id, request):
        value = {"session_id": session_id, "request": request, "status": "running"}
        self.sessions[session_id] = value
        return value

    def ask(self, session_id, question):
        self.sessions[session_id]["status"] = "waiting_for_user"
        self.sessions[session_id]["question"] = question
        return self.sessions[session_id]

    def answer(self, session_id, answer):
        self.sessions[session_id]["status"] = "running"
        self.sessions[session_id]["answer"] = answer
        return self.sessions[session_id]

    def load(self, session_id):
        return self.sessions[session_id]


def test_session_http_flow():
    app = create_app(FakeTeamAPI(), session_manager=FakeSessionManager())
    client = app.test_client()

    response = client.post("/api/session/start", json={"session_id": "s1", "request": "build a site"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "running"

    response = client.post("/api/session/s1/question", json={"question": "What is the site topic?"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "waiting_for_user"

    response = client.post("/api/session/s1/answer", json={"answer": "Satellite services"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "running"

    response = client.get("/api/session/s1")
    assert response.status_code == 200
    assert response.get_json()["answer"] == "Satellite services"
