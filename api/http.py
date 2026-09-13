from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from api.agent_team_api import AgentTeamAPI
from api.session_api import create_session_blueprint
from manager.auth import APIAuthenticator
from manager.session_runtime import SessionRuntime
from runtime import ManagerRuntime


DASHBOARD_ROOT = Path(__file__).resolve().parent.parent / "dashboard"
MAX_REQUEST_LENGTH = int(os.getenv("AI_AGENT_MANAGER_MAX_REQUEST_LENGTH", "12000"))


def create_app(
    team_api: AgentTeamAPI | None = None,
    runtime: ManagerRuntime | None = None,
    session_runtime: SessionRuntime | None = None,
    authenticator: APIAuthenticator | None = None,
) -> Flask:
    """برنامه HTTP مدیریتی را با داشبورد و APIهای واقعی می‌سازد."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("AI_AGENT_MANAGER_MAX_BODY_BYTES", "1048576"))
    manager_runtime = runtime or ManagerRuntime()
    manager_team_api = team_api or AgentTeamAPI(manager_runtime.agent_team, manager_runtime.registry_manager)
    user_runtime = session_runtime or SessionRuntime(runtime=manager_runtime)
    api_auth = authenticator or APIAuthenticator()
    app.register_blueprint(create_session_blueprint(user_runtime, authenticator=api_auth))

    @app.before_request
    def authenticate_api_requests():
        if not api_auth.enabled or request.path.startswith("/dashboard") or request.path == "/":
            return None
        if request.path == "/api/health":
            return None
        if request.path.startswith("/api/") and not api_auth.validate(request.headers.get("X-API-Key")):
            return jsonify({"error": "کلید دسترسی معتبر نیست."}), 401
        return None

    @app.get("/")
    def dashboard_root():
        return send_from_directory(DASHBOARD_ROOT, "index.html")

    @app.get("/dashboard")
    def dashboard():
        return send_from_directory(DASHBOARD_ROOT, "index.html")

    @app.get("/dashboard/<path:filename>")
    def dashboard_files(filename: str):
        return send_from_directory(DASHBOARD_ROOT, filename)

    @app.get("/api/agents")
    def list_agents():
        return jsonify(manager_team_api.list_agents())

    @app.post("/api/agents/<name>/enable")
    def enable_agent(name: str):
        try:
            return jsonify(manager_team_api.enable(name))
        except (KeyError, ValueError) as error:
            return jsonify({"error": str(error)}), 404

    @app.post("/api/agents/<name>/disable")
    def disable_agent(name: str):
        try:
            return jsonify(manager_team_api.disable(name))
        except (KeyError, ValueError) as error:
            return jsonify({"error": str(error)}), 404

    @app.post("/api/run")
    def run_request():
        payload = request.get_json(silent=True) or {}
        request_text = str(payload.get("request", "")).strip()
        agent_value = payload.get("agent")
        agent = str(agent_value).strip() if agent_value is not None else None
        if not request_text:
            return jsonify({"error": "فیلد request الزامی است."}), 400
        if len(request_text) > MAX_REQUEST_LENGTH:
            return jsonify({"error": f"طول درخواست نباید بیشتر از {MAX_REQUEST_LENGTH} نویسه باشد."}), 413
        report = manager_runtime.run(request_text, agent)
        return jsonify(report.to_dict())

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


def create_default_app() -> Flask:
    """نمونه آماده اجرا برای استفاده مستقیم توسط WSGI یا توسعه محلی."""
    return create_app()
