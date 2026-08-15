from __future__ import annotations

from flask import Flask, jsonify, request

from api.agent_team_api import AgentTeamAPI
from api.session_api import create_session_blueprint
from manager.user_session_manager import UserSessionManager
from runtime import ManagerRuntime


def create_app(
    team_api: AgentTeamAPI,
    runtime: ManagerRuntime | None = None,
    session_manager: UserSessionManager | None = None,
) -> Flask:
    """برنامه HTTP مدیریتی، اجرای درخواست و Session کاربر را می‌سازد."""
    app = Flask(__name__)
    manager_runtime = runtime or ManagerRuntime()
    app.register_blueprint(create_session_blueprint(session_manager))

    @app.get("/api/agents")
    def list_agents():
        return jsonify(team_api.list_agents())

    @app.post("/api/agents/<name>/enable")
    def enable_agent(name: str):
        return jsonify(team_api.enable(name))

    @app.post("/api/agents/<name>/disable")
    def disable_agent(name: str):
        return jsonify(team_api.disable(name))

    @app.post("/api/run")
    def run_request():
        payload = request.get_json(silent=True) or {}
        request_text = str(payload.get("request", "")).strip()
        agent = str(payload.get("agent", "developer")).strip() or "developer"
        if not request_text:
            return jsonify({"error": "فیلد request الزامی است."}), 400
        report = manager_runtime.run(request_text, agent)
        return jsonify(report.to_dict())

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
