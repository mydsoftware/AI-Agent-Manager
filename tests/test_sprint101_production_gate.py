import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

from http_api import APIHandler


def test_production_api_rejects_missing_auth(monkeypatch):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "production-key")
    server = HTTPServer(("127.0.0.1", 0), APIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/execute",
            data=json.dumps({"request": "test"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(request)
            assert False, "unauthorized request must be rejected"
        except urllib.error.HTTPError as error:
            assert error.code == 401
            assert "error" in json.loads(error.read())
    finally:
        server.shutdown()
        thread.join(timeout=2)
