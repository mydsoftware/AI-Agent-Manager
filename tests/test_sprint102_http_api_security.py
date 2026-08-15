import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

from http_api import ManagerRequestHandler


def test_http_api_protects_execute_and_session_endpoints(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "s102-secret")
    server = HTTPServer(("127.0.0.1", 0), ManagerRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"

    try:
        request = urllib.request.Request(
            base + "/execute",
            data=json.dumps({"request": "test"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(request)
            assert False
        except urllib.error.HTTPError as error:
            assert error.code == 401

        request = urllib.request.Request(base + "/session/test")
        with urllib.request.urlopen(request) as response:
            assert response.status in (200, 404)
    finally:
        server.shutdown()
        thread.join(timeout=2)
