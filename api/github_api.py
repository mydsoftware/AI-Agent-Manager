"""API اتصال GitHub برای داشبورد پروژه."""

from __future__ import annotations

from flask import Flask, jsonify, request
from services.github_integration import GitHubIntegration


def register_github_api(app: Flask, github: GitHubIntegration | None = None) -> None:
    client = github or GitHubIntegration()

    @app.get("/api/github/status")
    def github_status():
        return jsonify(client.status())

    @app.post("/api/github/repository-url")
    def github_repository_url():
        payload = request.get_json(silent=True) or {}
        try:
            return jsonify({"url": client.repository_url(str(payload.get("owner", "")), str(payload.get("repository", "")))})
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/api/github/repository")
    def github_repository():
        try:
            return jsonify(client.repository(str(request.args.get("owner", "")), str(request.args.get("repository", ""))))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/github/issue")
    def github_issue():
        payload = request.get_json(silent=True) or {}
        try:
            result = client.create_issue(str(payload.get("owner", "")), str(payload.get("repository", "")), str(payload.get("title", "")), str(payload.get("body", "")))
            return jsonify(result), 201
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/github/branch")
    def github_branch():
        payload = request.get_json(silent=True) or {}
        try:
            result = client.create_branch(str(payload.get("owner", "")), str(payload.get("repository", "")), str(payload.get("branch", "")), str(payload.get("source_sha", "")))
            return jsonify(result), 201
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400
