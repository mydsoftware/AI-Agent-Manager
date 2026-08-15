import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

from http_api import ManagerRequestHandler


def test_get_session_requires_api_key(monkeypatch):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "s104-secret")
    from manager.api_guard import APIGuard
    ManagerRequestHandler.guard = APIGuard()
    server = HTTPServer(("127.0.0.1", 0), ManagerRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(f"http://127.0.0.1:{server.server_port}/session/test")
        try:
            urllib.request.urlopen(request)
            assert False, "unauthorized session GET must fail"
        except urllib.error.HTTPError as error:
            assert error.code == 401
            assert json.loads(error.read())["error"]
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_health_remains_public(monkeypatch):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "s104-secret")
    from manager.api_guard import APIGuard
    ManagerRequestHandler.guard = APIGuard()
    server = HTTPServer(("127.0.0.1", 0), ManagerRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/health") as response:
            assert response.status == 200
            assert json.loads(response.read())["status"] == "فعال"
    finally:
        server.shutdown()
        thread.join(timeout=2)
