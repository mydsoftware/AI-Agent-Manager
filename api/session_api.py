from __future__ import annotations

from flask import Blueprint, jsonify, request

from manager.auth import APIAuthenticator
from manager.session_runtime import SessionRuntime


def create_session_blueprint(
    session_runtime: SessionRuntime | None = None,
    authenticator: APIAuthenticator | None = None,
) -> Blueprint:
    runtime = session_runtime or SessionRuntime()
    api_auth = authenticator or APIAuthenticator()
    api = Blueprint("session_api", __name__)

    def require_key():
        if api_auth.enabled and not api_auth.validate(request.headers.get("X-API-Key")):
            return jsonify({"error": "کلید دسترسی معتبر نیست."}), 401
        return None

    @api.post("/api/session/start")
    def start():
        unauthorized = require_key()
        if unauthorized:
            return unauthorized
        payload = request.get_json(silent=True) or {}
        session_id = str(payload.get("session_id", "")).strip()
        request_text = str(payload.get("request", "")).strip()
        if not session_id or not request_text:
            return jsonify({"error": "session_id و request الزامی هستند."}), 400
        try:
            return jsonify(runtime.start(session_id, request_text).__dict__)
        except (ValueError, KeyError) as error:
            return jsonify({"error": str(error)}), 400

    @api.post("/api/session/<session_id>/answer")
    def answer(session_id: str):
        unauthorized = require_key()
        if unauthorized:
            return unauthorized
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("answer", "")).strip()
        if not text:
            return jsonify({"error": "answer الزامی است."}), 400
        try:
            return jsonify(runtime.answer(session_id, text).__dict__)
        except KeyError:
            return jsonify({"error": "Session پیدا نشد."}), 404
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    @api.get("/api/session/<session_id>")
    def status(session_id: str):
        unauthorized = require_key()
        if unauthorized:
            return unauthorized
        try:
            return jsonify(runtime.get(session_id).__dict__)
        except KeyError:
            return jsonify({"error": "Session پیدا نشد."}), 404

    return api
