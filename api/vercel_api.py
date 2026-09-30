"""API استقرار Vercel و QA مرورگر برای داشبورد."""

from __future__ import annotations

import hmac
import os

from flask import Flask, jsonify, request
from services.browser_qa import BrowserQA
from services.vercel_deployment import VercelDeploymentService


def _authorized_request() -> bool:
    """درخواست را با کلید API سرور و مقایسه constant-time احراز می‌کند."""
    expected = os.getenv("MANAGER_API_TOKEN", "").strip()
    supplied = request.headers.get("X-Manager-API-Key", "").strip()
    return bool(expected) and hmac.compare_digest(supplied, expected)


def _require_auth():
    """در صورت نبود احراز هویت، پاسخ 401 مناسب API را برمی‌گرداند."""
    if _authorized_request():
        return None
    return jsonify({"error": "احراز هویت برای این Endpoint الزامی است."}), 401


def register_vercel_api(app: Flask, vercel: VercelDeploymentService | None = None, browser_qa: BrowserQA | None = None) -> None:
    """Routeهای Vercel و Browser QA را با لایه احراز هویت ثبت می‌کند."""
    client = vercel or VercelDeploymentService()
    qa = browser_qa or BrowserQA()

    @app.get("/api/vercel/status")
    def vercel_status():
        denied = _require_auth()
        if denied:
            return denied
        return jsonify(client.status())

    @app.get("/api/vercel/project")
    def vercel_project():
        denied = _require_auth()
        if denied:
            return denied
        try:
            return jsonify(client.project(str(request.args.get("project_id", "")), request.args.get("team_id")))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/api/vercel/deployments")
    def vercel_deployments():
        denied = _require_auth()
        if denied:
            return denied
        try:
            limit = int(request.args.get("limit", "20"))
            return jsonify(client.deployments(str(request.args.get("project_id", "")), request.args.get("team_id"), limit))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/api/vercel/deployment")
    def vercel_deployment():
        denied = _require_auth()
        if denied:
            return denied
        try:
            return jsonify(client.deployment(str(request.args.get("deployment_id", "")), request.args.get("team_id")))
        except (ValueError, RuntimeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/browser-qa/smoke")
    def browser_qa_smoke():
        denied = _require_auth()
        if denied:
            return denied
        payload = request.get_json(silent=True) or {}
        try:
            return jsonify(qa.run_smoke(str(payload.get("url", ""))))
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
