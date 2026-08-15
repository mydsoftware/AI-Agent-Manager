import json
import threading
import urllib.request
from http.server import HTTPServer

from http_api import ManagerRequestHandler


def test_health_endpoint_is_available_without_api_key():
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
