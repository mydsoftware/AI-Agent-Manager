from __future__ import annotations

from flask import Blueprint, jsonify, request

from manager.session_runtime import SessionRuntime


def create_session_blueprint(session_runtime: SessionRuntime | None = None) -> Blueprint:
    runtime = session_runtime or SessionRuntime()
    api = Blueprint("session_api", __name__)

    @api.post("/api/session/start")
    def start():
        payload = request.get_json(silent=True) or {}
        session_id = str(payload.get("session_id", "")).strip()
        request_text = str(payload.get("request", "")).strip()
        if not session_id or not request_text:
            return jsonify({"error": "session_id و request الزامی هستند."}), 400
        return jsonify(runtime.start(session_id, request_text).__dict__)

    @api.post("/api/session/<session_id>/answer")
    def answer(session_id: str):
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("answer", "")).strip()
        if not text:
            return jsonify({"error": "answer الزامی است."}), 400
        return jsonify(runtime.answer(session_id, text).__dict__)

    @api.get("/api/session/<session_id>")
    def status(session_id: str):
        return jsonify(runtime.get(session_id).__dict__)

    return api
