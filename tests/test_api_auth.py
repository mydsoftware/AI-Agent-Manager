from __future__ import annotations

import pytest

from api.app import create_manager_app


@pytest.fixture()
def auth_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MANAGER_API_TOKEN", "admin-secret")
    monkeypatch.setenv("MANAGER_OPERATOR_TOKEN", "operator-secret")
    monkeypatch.setenv("MANAGER_VIEWER_TOKEN", "viewer-secret")
    return {
        "admin": {"X-Manager-API-Key": "admin-secret"},
        "operator": {"X-Manager-API-Key": "operator-secret"},
        "viewer": {"X-Manager-API-Key": "viewer-secret"},
    }


def test_api_requires_auth(auth_env):
    app = create_manager_app()
    client = app.test_client()
    assert client.get("/api/projects").status_code == 401


def test_viewer_is_read_only(auth_env):
    app = create_manager_app()
    client = app.test_client()
    response = client.post("/api/project/create", json={"name": "x", "description": "x", "request": "x"}, headers=auth_env["viewer"])
    assert response.status_code == 403


def test_project_creation_binds_authenticated_owner(auth_env):
    app = create_manager_app()
    client = app.test_client()
    response = client.post("/api/project/create", json={"name": "owner-test", "description": "x", "request": "x"}, headers=auth_env["operator"])
    assert response.status_code == 201
    assert response.get_json()["owner_id"] == "manager-operator"


def test_project_isolation_returns_404_for_other_owner(auth_env):
    app = create_manager_app()
    client = app.test_client()
    created = client.post("/api/project/create", json={"name": "scope-test", "description": "x", "request": "x"}, headers=auth_env["operator"])
    assert created.status_code == 201
    project_id = created.get_json()["id"]
    assert client.get(f"/api/project/{project_id}", headers=auth_env["viewer"]).status_code == 404
    assert client.get(f"/api/project/{project_id}", headers=auth_env["admin"]).status_code == 200


def test_route_endpoint_preserves_unauthenticated_contract(auth_env):
    app = create_manager_app()
    client = app.test_client()
    response = client.post("/api/route", json={"request": "ساخت یک سایت فروشگاهی"})
    assert response.status_code == 200
