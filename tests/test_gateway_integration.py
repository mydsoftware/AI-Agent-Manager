from __future__ import annotations

import json
from unittest.mock import patch

from gateway import server


def test_gateway_route_forwards_request_to_manager():
    captured = {}

    def fake_manager_request(path, body, execution_id=None):
        captured.update(path=path, body=body, execution_id=execution_id)
        return 200, {
            "agent": "website-audit",
            "url": "https://example.com",
            "mode": "pre_contract",
            "access": False,
            "language": "fa",
        }

    with patch.object(server, "manager_request", side_effect=fake_manager_request):
        status, data = server.manager_request("/route", {"request": "AI Agent Manager سایت example.com را بررسی کن"})

    assert status == 200
    assert data["agent"] == "website-audit"


def test_manager_request_uses_gateway_api_key_header(monkeypatch):
    monkeypatch.setattr(server, "GATEWAY_TOKEN", "secret")
    calls = {}

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"status": "ok"}).encode("utf-8")

    def fake_urlopen(request, timeout):
        calls["request"] = request
        calls["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(server.urllib.request, "urlopen", fake_urlopen)
    status, data = server.manager_request("/route", {"request": "تست"})

    assert status == 200
    assert data == {"status": "ok"}
    assert calls["request"].get_header("X-api-key") == "secret"
    assert calls["timeout"] == 30


def test_gateway_website_audit_forwards_execution_id():
    captured = {}

    def fake_manager_request(path, body, execution_id=None):
        captured.update(path=path, body=body, execution_id=execution_id)
        return 202, {"status": "accepted", "execution_id": execution_id}

    with patch.object(server, "manager_request", side_effect=fake_manager_request):
        status, data = server.manager_request(
            "/execute/website-audit",
            {
                "request_id": "req-1",
                "url": "https://example.com",
                "mode": "pre_contract",
                "access": False,
                "language": "fa",
            },
            "exec-1",
        )

    assert status == 202
    assert captured["path"] == "/execute/website-audit"
    assert captured["execution_id"] == "exec-1"
    assert captured["body"]["access"] is False
