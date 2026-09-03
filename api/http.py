from __future__ import annotations

from flask import Flask, jsonify, request

from api.agent_team_api import AgentTeamAPI
from agents.wordpress_connection_http_api import WordPressConnectionHttpApi
from manager.request_router import route_request
from platform.project_store import ProjectStore
from runtime import ManagerRuntime


def create_app(
    team_api: AgentTeamAPI,
    runtime: ManagerRuntime | None = None,
    wordpress_connection_api: WordPressConnectionHttpApi | None = None,
    project_store: ProjectStore | None = None,
) -> Flask:
    """برنامه HTTP مدیریتی و اجرای درخواست‌های Manager را می‌سازد."""
    app = Flask(__name__)
    manager_runtime = runtime or ManagerRuntime()
    connection_api = wordpress_connection_api or WordPressConnectionHttpApi()
    projects = project_store or ProjectStore()

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

    @app.post("/api/route")
    def route_request_api():
        payload = request.get_json(silent=True) or {}
        request_text = str(payload.get("request", "")).strip()
        if not request_text:
            return jsonify({"error": "فیلد request الزامی است."}), 400
        return jsonify(route_request(request_text).__dict__)

    @app.get("/api/projects")
    def list_projects():
        return jsonify(projects.list())

    @app.post("/api/project/create")
    def create_project():
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        project_request = str(payload.get("request", "")).strip()
        if not name or not description or not project_request:
            return jsonify({"error": "name، description و request الزامی هستند."}), 400
        project = projects.create(
            name=name,
            description=description,
            request=project_request,
            project_type=str(payload.get("project_type", "other")),
            is_private=bool(payload.get("private", True)),
        )
        return jsonify(project), 201

    @app.get("/api/project/<project_id>")
    def get_project(project_id: str):
        project = projects.get(project_id)
        if project is None:
            return jsonify({"error": "پروژه پیدا نشد."}), 404
        return jsonify(project)

    @app.post("/api/wordpress/connection/check")
    def wordpress_connection_check():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"message": "بدنه درخواست باید Object باشد."}), 400
        result = connection_api.post_check(payload)
        return jsonify(result.body), result.status

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
