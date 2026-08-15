import json
import threading
from http.client import HTTPConnection
from http.server import HTTPServer

from manager.api_guard import APIGuard
from session_api import SessionAPIHandler


class RuntimeStub:
    def __init__(self):
        self.calls = []

    def start(self, session_id, request):
        self.calls.append(("start", session_id, request))
        return type("State", (), {"to_dict": lambda self: {"status": "waiting_for_user", "stage": "clarification", "question": "جزئیات؟"}})()

    def answer(self, session_id, answer):
        self.calls.append(("answer", session_id, answer))
        return type("State", (), {"to_dict": lambda self: {"status": "completed", "stage": "delivery", "output": {"artifact": "demo"}}})()

    def resume(self, session_id):
        self.calls.append(("resume", session_id))
        return type("State", (), {"to_dict": lambda self: {"status": "completed", "stage": "delivery"}})()

    class Sessions:
        def load(self, session_id):
            return type("State", (), {"to_dict": lambda self: {"session_id": session_id, "status": "completed"}})()

    sessions = Sessions()


def test_session_api_endpoints_round_trip(monkeypatch):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "test-key")
    previous_runtime = SessionAPIHandler.runtime
    previous_guard = SessionAPIHandler.guard
    SessionAPIHandler.runtime = RuntimeStub()
    SessionAPIHandler.guard = APIGuard()
    server = HTTPServer(("127.0.0.1", 0), SessionAPIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    headers = {"Content-Type": "application/json", "X-API-Key": "test-key"}
    try:
        conn = HTTPConnection("127.0.0.1", server.server_port)
        body = json.dumps({"session_id": "api-e2e", "request": "یک سایت بساز"}).encode()
        conn.request("POST", "/session/start", body, headers)
        response = conn.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["status"] == "waiting_for_user"

        body = json.dumps({"session_id": "api-e2e", "answer": "فروشگاه"}).encode()
        conn.request("POST", "/session/answer", body, headers)
        response = conn.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["status"] == "completed"

        conn.request("GET", "/session/api-e2e", headers=headers)
        response = conn.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["session_id"] == "api-e2e"
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        SessionAPIHandler.runtime = previous_runtime
        SessionAPIHandler.guard = previous_guard
