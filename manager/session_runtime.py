from __future__ import annotations

from typing import Any
from manager.user_session import UserSessionManager, UserSession


class SessionRuntime:
    """User-facing clarification/resume boundary around ManagerRuntime."""

    def __init__(self, sessions: UserSessionManager | None = None, runtime: Any | None = None) -> None:
        self.sessions = sessions or UserSessionManager()
        if runtime is None:
            from runtime import ManagerRuntime
            runtime = ManagerRuntime()
        self.runtime = runtime

    @staticmethod
    def _needs_clarification(request: str) -> bool:
        text = request.strip()
        if len(text) < 8:
            return True
        return text in ("یک سایت بساز", "یه سایت بساز", "برنامه بساز", "اپ بساز", "انجامش بده")

    def start(self, session_id: str, request: str) -> UserSession:
        session = self.sessions.create(session_id, request)
        if self._needs_clarification(request):
            session.status = "waiting_for_user"
            session.question = "لطفاً هدف یا نوع دقیق پروژه را مشخص کنید."
            return self.sessions.update(session)
        return self._execute(session)

    def answer(self, session_id: str, answer: str) -> UserSession:
        session = self.sessions.load(session_id)
        if session.status != "waiting_for_user":
            raise RuntimeError("این Session منتظر پاسخ کاربر نیست.")
        session.answers.append(answer)
        session.request = f"{session.request}\nاطلاعات تکمیلی کاربر: {answer}"
        session.question = None
        return self._execute(session)

    def _execute(self, session: UserSession) -> UserSession:
        session.status = "running"
        session.stage = "planning"
        session = self.sessions.update(session)
        output = self.runtime.run(session.request)
        session.output = output
        session.status = "completed"
        session.stage = "delivery"
        return self.sessions.update(session)
