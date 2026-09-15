from __future__ import annotations

from flask import Flask

from api.session_api import create_session_blueprint
from manager.auth import APIAuthenticator
from manager.session_runtime import SessionRuntime
from manager.user_session import UserSessionManager


def build_client(tmp_path):
    auth = APIAuthenticator.__new__(APIAuthenticator)
    auth.environment_name = "TEST_KEY"
    auth.api_key = "secret"

    runtime = SessionRuntime(sessions=UserSessionManager(root=str(tmp_path / "sessions")))
    app = Flask(__name__)
    app.register_blueprint(create_session_blueprint(runtime, auth))
    app.config["TESTING"] = True
    return app.test_client()


def test_session_api_accepts_bearer_authentication(tmp_path):
    client = build_client(tmp_path)
    payload = {"session_id": "bearer-test", "request": "یک سایت بساز"}

    assert client.post("/api/session/start", json=payload).status_code == 401
    assert client.post(
        "/api/session/start", json=payload, headers={"Authorization": "Basic secret"}
    ).status_code == 401
    response = client.post(
        "/api/session/start", json=payload, headers={"Authorization": "Bearer secret"}
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "waiting_for_user"


def test_session_api_preserves_api_key_compatibility(tmp_path):
    client = build_client(tmp_path)
    payload = {"session_id": "api-key-test", "request": "یک سایت بساز"}

    response = client.post(
        "/api/session/start", json=payload, headers={"X-API-Key": "secret"}
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "waiting_for_user"
