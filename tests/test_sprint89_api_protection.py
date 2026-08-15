from http.server import HTTPServer
import threading
import json
import urllib.request
import urllib.error

from session_api import SessionAPIHandler


def test_session_api_rejects_invalid_api_key(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "sprint89-secret")
    from manager.session_runtime import SessionRuntime
    from manager.user_session import UserSessionManager

    SessionAPIHandler.runtime = SessionRuntime(sessions=UserSessionManager(str(tmp_path)))
    server = HTTPServer(("127.0.0.1", 0), SessionAPIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/session/missing",
            headers={"X-API-Key": "wrong"},
        )
        try:
            urllib.request.urlopen(request)
            assert False, "request should be rejected"
        except urllib.error.HTTPError as error:
            assert error.code == 401
            payload = json.loads(error.read())
            assert "error" in payload
    finally:
        server.shutdown()
        thread.join(timeout=2)
