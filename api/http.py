from __future__ import annotations

from flask import Flask, jsonify, request

from api.agent_team_api import AgentTeamAPI


def create_app(team_api: AgentTeamAPI) -> Flask:
    """برنامه HTTP مدیریتی را می‌سازد."""
    app = Flask(__name__)

    @app.get("/api/agents")
    def list_agents():
        return jsonify(team_api.list_agents())

    @app.post("/api/agents/<name>/enable")
    def enable_agent(name: str):
        return jsonify(team_api.enable(name))

    @app.post("/api/agents/<name>/disable")
    def disable_agent(name: str):
        return jsonify(team_api.disable(name))

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
