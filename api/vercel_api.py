"""API استقرار Vercel و QA مرورگر برای داشبورد."""

from __future__ import annotations

from flask import Flask, jsonify, request
from services.browser_qa import BrowserQA
from services.vercel_deployment import VercelDeploymentService


def register_vercel_api(app: Flask, vercel: VercelDeploymentService | None = None, browser_qa: BrowserQA | None = None) -> None:
    client = vercel or VercelDeploymentService()
    qa = browser_qa or BrowserQA()

    @app.get("/api/vercel/status")
    def vercel_status():
        return jsonify(client.status())

    @app.get("/api/vercel/project")
    def vercel_project():
        try:
            return jsonify(client.project(str(request.args.get("project_id", "")), request.args.get("team_id")))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/api/vercel/deployments")
    def vercel_deployments():
        try:
            limit = int(request.args.get("limit", "20"))
            return jsonify(client.deployments(str(request.args.get("project_id", "")), request.args.get("team_id"), limit))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/api/vercel/deployment")
    def vercel_deployment():
        try:
            return jsonify(client.deployment(str(request.args.get("deployment_id", "")), request.args.get("team_id")))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/browser-qa/smoke")
    def browser_qa_smoke():
        payload = request.get_json(silent=True) or {}
        try:
            return jsonify(qa.run_smoke(str(payload.get("url", ""))))
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
