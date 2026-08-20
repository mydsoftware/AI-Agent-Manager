import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

import pytest

from http_api import ManagerRequestHandler


def _server(monkeypatch):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "audit-test-key")
    server = HTTPServer(("127.0.0.1", 0), ManagerRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _post(base, path, payload, key="audit-test-key"):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-API-Key": key},
        method="POST",
    )
    return urllib.request.urlopen(request)


def test_website_audit_requires_auth(monkeypatch):
    server, thread = _server(monkeypatch)
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/execute/website-audit",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        assert error.value.code == 401
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_website_audit_validates_required_fields(monkeypatch):
    server, thread = _server(monkeypatch)
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with pytest.raises(urllib.error.HTTPError) as error:
            _post(base, "/execute/website-audit", {"request_id": "x"})
        assert error.value.code == 400
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_pre_contract_cannot_have_access(monkeypatch):
    server, thread = _server(monkeypatch)
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with pytest.raises(urllib.error.HTTPError) as error:
            _post(base, "/execute/website-audit", {
                "request_id": "x",
                "url": "https://example.com",
                "mode": "pre_contract",
                "access": True,
            })
        assert error.value.code == 400
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_website_audit_contract(monkeypatch):
    server, thread = _server(monkeypatch)
    try:
        import http_api
        monkeypatch.setattr(http_api, "execute", lambda request, agent: {
            "status": "completed",
            "report": "گزارش آزمایشی فارسی",
            "limitations": [],
            "required_access": [],
        })
        base = f"http://127.0.0.1:{server.server_port}"
        with _post(base, "/execute/website-audit", {
            "request_id": "audit-1",
            "url": "https://example.com",
            "mode": "pre_contract",
            "access": False,
            "language": "fa",
        }) as response:
            data = json.load(response)
        assert data["status"] == "completed"
        assert data["request_id"] == "audit-1"
        assert data["agent"] == "website-audit"
        assert data["url"] == "https://example.com"
        assert data["mode"] == "pre_contract"
        assert data["report"] == "گزارش آزمایشی فارسی"
    finally:
        server.shutdown()
        thread.join(timeout=2)
