from __future__ import annotations

from api.app import create_manager_app
from ui.web_app import app as ui_app


def test_manager_route_endpoint():
    client = create_manager_app().test_client()
    response = client.post("/api/route", json={"request": "یک سایت را بررسی کن"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["agent"] == "website-audit"
    assert body["mode"] == "pre_contract"


def test_ui_execute_proxies_to_manager_run(monkeypatch):
    monkeypatch.setattr(
        "ui.web_app.api_call",
        lambda endpoint, method="GET", data=None: {
            "endpoint": endpoint,
            "method": method,
            "data": data,
        },
    )
    client = ui_app.test_client()
    response = client.post("/api/execute", json={"request": "ساخت سایت", "agent": "developer"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["endpoint"] == "/api/run"
    assert body["data"]["request"] == "ساخت سایت"
    assert body["data"]["agent"] == "developer"


def test_ui_rejects_empty_command():
    client = ui_app.test_client()
    response = client.post("/api/execute", json={"request": ""})
    assert response.status_code == 400
