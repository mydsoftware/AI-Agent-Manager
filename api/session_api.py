from __future__ import annotations

from flask import Blueprint, jsonify, request

from manager.user_session_manager import UserSessionManager


def create_session_blueprint(session_manager: UserSessionManager | None = None) -> Blueprint:
    manager = session_manager or UserSessionManager()
    api = Blueprint("session_api", __name__)

    @api.post("/api/session/start")
    def start():
        payload = request.get_json(silent=True) or {}
        session_id = str(payload.get("session_id", "")).strip()
        request_text = str(payload.get("request", "")).strip()
        if not session_id or not request_text:
            return jsonify({"error": "session_id و request الزامی هستند."}), 400
        return jsonify(manager.start(session_id, request_text))

    @api.post("/api/session/<session_id>/question")
    def question(session_id: str):
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("question", "")).strip()
        if not text:
            return jsonify({"error": "question الزامی است."}), 400
        return jsonify(manager.ask(session_id, text))

    @api.post("/api/session/<session_id>/answer")
    def answer(session_id: str):
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("answer", "")).strip()
        if not text:
            return jsonify({"error": "answer الزامی است."}), 400
        return jsonify(manager.answer(session_id, text))

    @api.get("/api/session/<session_id>")
    def status(session_id: str):
        return jsonify(manager.load(session_id))

    return api
