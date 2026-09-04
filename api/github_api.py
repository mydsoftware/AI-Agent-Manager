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
