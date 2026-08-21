import json

from agents.http_server_adapter import AgentHttpServerAdapter


class FakeConnectionApi:
    def post_check(self, payload):
        return type("Response", (), {
            "status": 200,
            "body": {"reachable": True, "authenticated": True, "writer_endpoint_available": True, "message": "اتصال موفق"},
        })()


def test_adapter_routes_connection_check():
    adapter = AgentHttpServerAdapter(FakeConnectionApi())
    status, headers, body = adapter.handle(
        "POST",
        "/api/wordpress/connection/check",
        json.dumps({"site_url": "https://example.com"}).encode(),
    )
    assert status == 200
    assert headers["Content-Type"].startswith("application/json")
    assert json.loads(body)["authenticated"] is True


def test_adapter_rejects_invalid_json():
    status, _, body = AgentHttpServerAdapter(FakeConnectionApi()).handle(
        "POST", "/api/wordpress/connection/check", b"{invalid"
    )
    assert status == 400
    assert "نامعتبر" in json.loads(body)["message"]
