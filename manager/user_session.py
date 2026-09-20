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
    answers: list[str] | None = None


class UserSessionManager:
    """رابط پایدار بین درخواست کاربر، سؤال شفاف‌سازی و ادامه اجرای Manager."""

    def __init__(self, root: str = "data/sessions", max_session_id_length: int = 128) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_session_id_length = max(1, max_session_id_length)

    def create(self, session_id: str, request: str) -> UserSession:
        self.start(session_id, request)
        return self.load(session_id)

    def load(self, session_id: str) -> UserSession:
        data = self._load(session_id)
        return UserSession(session_id=data["session_id"], request=data["request"], status=data["status"], stage=data["stage"], question=data.get("question"), answers=[x.get("answer", "") for x in data.get("context", {}).get("user_answers", [])], output=data.get("output"))

    def start(self, session_id: str, request: str) -> UserSessionResult:
        if not request.strip():
            raise ValueError("درخواست نمی‌تواند خالی باشد.")
        self._path(session_id)
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
        session.update({"status": "waiting_for_user", "stage": "clarification" if stage == "requirements" else stage, "question": question})
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
        session.update({"status": "completed", "stage": "delivery", "question": None, "output": {"report": output} if "report" not in output else output})
        return self._save(session)

    def fail(self, session_id: str, error: str, stage: str = "execution") -> UserSessionResult:
        session = self._load(session_id)
        session.update({"status": "failed", "stage": stage, "question": None, "output": {"error": error}})
        return self._save(session)

    def get(self, session_id: str) -> UserSessionResult:
        return self._result(self._load(session_id))

    def _path(self, session_id: str) -> Path:
        raw = str(session_id).strip()
        if not raw or len(raw) > self.max_session_id_length:
            raise ValueError("session_id معتبر نیست.")
        if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in raw):
            raise ValueError("session_id فقط می‌تواند شامل حروف، اعداد، - و _ باشد.")
        return self.root / f"{raw}.json"

    def _load(self, session_id: str) -> dict[str, Any]:
        path = self._path(session_id)
        if not path.exists():
            raise KeyError(f"Session پیدا نشد: {session_id}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError("اطلاعات Session قابل خواندن نیست.") from error

    def _save(self, session: dict[str, Any]) -> UserSessionResult:
        path = self._path(session["session_id"])
        temporary = path.with_suffix(f".json.{id(session)}.tmp")
        try:
            temporary.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(path)
        except OSError as error:
            raise RuntimeError("ذخیره Session انجام نشد.") from error
        finally:
            temporary.unlink(missing_ok=True)
        return self._result(session)

    @staticmethod
    def _result(session: dict[str, Any]) -> UserSessionResult:
        return UserSessionResult(
            session_id=session["session_id"], request=session["request"], status=session["status"],
            stage=session["stage"], question=session.get("question"),
            context=session.get("context", {}), output=session.get("output"),
            answers=[item.get("answer", "") for item in session.get("context", {}).get("user_answers", [])],
        )
