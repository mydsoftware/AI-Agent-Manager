from __future__ import annotations

from flask import Flask, jsonify, request

from services.agent_log_store import AgentLogStore


def register_agent_logs_api(app: Flask, database_path: str = "data/platform.db") -> None:
    """Endpointهای مشاهده لاگ Agentها را ثبت می‌کند."""
    logs = AgentLogStore(database_path)

    @app.get("/api/agent-logs")
    def list_agent_logs():
        try:
            limit = int(request.args.get("limit", 100))
            return jsonify(
                logs.list(
                    project_id=request.args.get("project_id"),
                    task_id=request.args.get("task_id"),
                    agent=request.args.get("agent"),
                    level=request.args.get("level"),
                    limit=limit,
                )
            )
        except (ValueError, TypeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/agent-logs")
    def create_agent_log():
        payload = request.get_json(silent=True) or {}
        try:
            return jsonify(
                logs.add(
                    str(payload.get("agent", "")),
                    str(payload.get("event_type", "")),
                    str(payload.get("message", "")),
                    project_id=str(payload["project_id"]) if payload.get("project_id") is not None else None,
                    workflow_id=str(payload["workflow_id"]) if payload.get("workflow_id") is not None else None,
                    task_id=str(payload["task_id"]) if payload.get("task_id") is not None else None,
                    level=str(payload.get("level", "info")),
                    metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
                )
            ), 201
        except (ValueError, TypeError) as error:
            return jsonify({"error": str(error)}), 400
