from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SessionStore:
    """Small JSON-backed persistent store for Manager sessions."""

    def __init__(self, root: str = ".agent_sessions") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        safe = "".join(ch for ch in session_id if ch.isalnum() or ch in "-_ .").strip().replace(" ", "_")
        if not safe:
            raise ValueError("invalid session_id")
        return self.root / f"{safe}.json"

    def create(self, session_id: str, request: str, stage: str) -> dict[str, Any]:
        session = {
            "session_id": session_id,
            "request": request,
            "stage": stage,
            "status": "running",
            "question": None,
            "context": {"request": request},
            "history": [],
        }
        self._save(session)
        return session

    def load(self, session_id: str) -> dict[str, Any]:
        path = self._path(session_id)
        if not path.exists():
            raise KeyError(session_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def ask(self, session_id: str, question: str) -> dict[str, Any]:
        session = self.load(session_id)
        session["status"] = "waiting_for_user"
        session["question"] = question
        session["history"].append({"type": "question", "value": question})
        self._save(session)
        return session

    def answer(self, session_id: str, answer: str, next_stage: str | None = None) -> dict[str, Any]:
        session = self.load(session_id)
        if session.get("status") != "waiting_for_user":
            raise ValueError("no active question")
        session["history"].append({"type": "answer", "value": answer})
        session["context"][f"answer_{len(session['history'])}"] = answer
        session["question"] = None
        session["status"] = "running"
        if next_stage:
            session["stage"] = next_stage
        self._save(session)
        return session

    def _save(self, session: dict[str, Any]) -> None:
        self._path(session["session_id"]).write_text(
            json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8"
        )
