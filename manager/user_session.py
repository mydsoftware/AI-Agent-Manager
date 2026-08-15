from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UserSessionResult:
    session_id: str
    request: str
    status: str
    stage: str
    question: str | None
    context: dict[str, Any]
    output: dict[str, Any] | None = None


class UserSessionManager:
    """رابط پایدار بین درخواست کاربر، سؤال شفاف‌سازی و ادامه اجرای Manager."""

    def __init__(self, root: str = "data/sessions") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def start(self, session_id: str, request: str) -> UserSessionResult:
        if not request.strip():
            raise ValueError("درخواست نمی‌تواند خالی باشد.")
        session = {
            "session_id": session_id,
            "request": request,
            "status": "running",
            "stage": "requirements",
            "question": None,
            "context": {},
            "output": None,
        }
        return self._save(session)

    def ask(self, session_id: str, question: str, stage: str = "requirements") -> UserSessionResult:
        session = self._load(session_id)
        session.update({"status": "waiting_for_user", "stage": stage, "question": question})
        return self._save(session)

    def answer(self, session_id: str, answer: str, next_stage: str = "planning") -> UserSessionResult:
        if not answer.strip():
            raise ValueError("پاسخ کاربر نمی‌تواند خالی باشد.")
        session = self._load(session_id)
        if session["status"] != "waiting_for_user":
            raise ValueError("این Session در انتظار پاسخ کاربر نیست.")
        context = dict(session.get("context", {}))
        context.setdefault("user_answers", []).append({"question": session.get("question"), "answer": answer})
        session.update({"status": "running", "stage": next_stage, "question": None, "context": context})
        return self._save(session)

    def complete(self, session_id: str, output: dict[str, Any]) -> UserSessionResult:
        session = self._load(session_id)
        session.update({"status": "completed", "stage": "delivery", "output": output})
        return self._save(session)

    def get(self, session_id: str) -> UserSessionResult:
        return self._result(self._load(session_id))

    def _path(self, session_id: str) -> Path:
        safe = "".join(ch for ch in session_id if ch.isalnum() or ch in "-_")
        if not safe:
            raise ValueError("session_id معتبر نیست.")
        return self.root / f"{safe}.json"

    def _load(self, session_id: str) -> dict[str, Any]:
        path = self._path(session_id)
        if not path.exists():
            raise KeyError(f"Session پیدا نشد: {session_id}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, session: dict[str, Any]) -> UserSessionResult:
        self._path(session["session_id"]).write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
        return self._result(session)

    @staticmethod
    def _result(session: dict[str, Any]) -> UserSessionResult:
        return UserSessionResult(
            session_id=session["session_id"], request=session["request"], status=session["status"],
            stage=session["stage"], question=session.get("question"),
            context=session.get("context", {}), output=session.get("output"),
        )
