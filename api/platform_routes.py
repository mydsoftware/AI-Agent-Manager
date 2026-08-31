"""Flask blueprints for budget, approvals, traces, plugins, and memory search."""

from __future__ import annotations

from flask import Blueprint, jsonify, request


def create_platform_blueprint(services) -> Blueprint:
    bp = Blueprint("platform", __name__, url_prefix="/platform")

    @bp.get("/budget")
    def budget():
        return jsonify(services.budget.snapshot())

    @bp.get("/approvals")
    def approvals():
        services.approvals.expire_stale()
        return jsonify([r.__dict__ for r in services.approvals.pending()])

    @bp.post("/approvals/<request_id>")
    def decide(request_id: str):
        body = request.get_json(silent=True) or {}
        req = services.approvals.decide(
            request_id,
            approved=bool(body.get("approved")),
            comment=str(body.get("comment", "")),
            actor=str(body.get("actor", "human")),
        )
        return jsonify(req.__dict__)

    @bp.get("/traces/<task_id>")
    def traces(task_id: str):
        return jsonify(services.tracer.task_summary(task_id))

    @bp.get("/agents/report")
    def agents_report():
        return jsonify(
            {
                "activity": services.tracer.agent_activity(),
                "tokens": services.tracer.token_report(),
                "errors": services.tracer.error_report(),
            }
        )

    @bp.get("/plugins")
    def plugins():
        return jsonify(services.plugins.status())

    @bp.get("/memory/search")
    def memory_search():
        project_id = request.args.get("project_id", "default")
        query = request.args.get("q", "")
        hits = services.memory.search(project_id, query, limit=10)
        return jsonify(
            [
                {"score": score, "id": rec.id, "kind": rec.kind, "title": rec.title, "content": rec.content[:500]}
                for rec, score in hits
            ]
        )

    return bp
