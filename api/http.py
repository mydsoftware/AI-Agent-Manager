from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from api.agent_team_api import AgentTeamAPI
from api.session_api import create_session_blueprint
from manager.session_runtime import SessionRuntime
from runtime import ManagerRuntime


DASHBOARD_ROOT = Path(__file__).resolve().parent.parent / "dashboard"


def create_app(
    team_api: AgentTeamAPI,
    runtime: ManagerRuntime | None = None,
    session_runtime: SessionRuntime | None = None,
) -> Flask:
    """برنامه HTTP مدیریتی، Session و داشبورد کاربر را می‌سازد."""
    app = Flask(__name__)
    manager_runtime = runtime or ManagerRuntime()
    user_runtime = session_runtime or SessionRuntime(runtime=manager_runtime)
    app.register_blueprint(create_session_blueprint(user_runtime))

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
        agent_value = payload.get("agent")
        agent = str(agent_value).strip() if agent_value is not None else None
        if not request_text:
            return jsonify({"error": "فیلد request الزامی است."}), 400
        report = manager_runtime.run(request_text, agent)
        return jsonify(report.to_dict())

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
