import json
import threading
import urllib.request
from http.server import HTTPServer

from session_api import SessionAPIHandler


def test_session_api_start_answer_and_get(tmp_path, monkeypatch):
    from manager.session_runtime import SessionRuntime
    from manager.user_session import UserSessionManager

    class RuntimeStub:
        def run(self, request: str, agent: str = "developer"):
            return {"status": "success", "artifact": "demo.txt", "agent": agent}

    SessionAPIHandler.runtime = SessionRuntime(
        sessions=UserSessionManager(str(tmp_path)),
        runtime=RuntimeStub(),
    )
    server = HTTPServer(("127.0.0.1", 0), SessionAPIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"

    try:
        def post(path, payload):
            request = urllib.request.Request(
                base + path,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())

        status, state = post("/session/start", {"session_id": "api-1", "request": "یک سایت بساز"})
        assert status == 200
        assert state["status"] == "waiting_for_user"

        status, state = post("/session/answer", {"session_id": "api-1", "answer": "یک سایت فروشگاهی بساز"})
        assert status == 200
        assert state["status"] == "completed"
        assert state["stage"] == "delivery"

        with urllib.request.urlopen(base + "/session/api-1") as response:
            restored = json.loads(response.read())
        assert restored["status"] == "completed"
    finally:
        server.shutdown()
        thread.join(timeout=2)
