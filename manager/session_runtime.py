from __future__ import annotations

from typing import Any

from manager.user_session import UserSessionManager, UserSessionResult
from runtime import ManagerRuntime


class SessionRuntime:
    """اجرای واقعی درخواست کاربر با پشتیبانی از clarification و resume."""

    GENERIC_REQUESTS = {
        "یک سایت بساز", "سایت بساز", "یک برنامه بساز", "برنامه بساز",
        "یه سایت بساز", "یه برنامه بساز", "build a site", "build an app",
    }

    def __init__(self, sessions: UserSessionManager | None = None, runtime: ManagerRuntime | None = None) -> None:
        self.sessions = sessions or UserSessionManager()
        self.runtime = runtime or ManagerRuntime()

    def start(self, session_id: str, request: str) -> UserSessionResult:
        session = self.sessions.start(session_id, request)
        if self._is_ambiguous(request):
            return self.sessions.ask(session_id, "برای انجام دقیق درخواست، موضوع و هدف پروژه را مشخص می‌کنید؟")
        return self._execute(session)

    def answer(self, session_id: str, answer: str) -> UserSessionResult:
        session = self.sessions.answer(session_id, answer)
        return self._execute(session)

    def get(self, session_id: str) -> UserSessionResult:
        return self.sessions.get(session_id)

    def _execute(self, session: UserSessionResult) -> UserSessionResult:
        request = session.context.get("resolved_request", session.context.get("request", None))
        if not request:
            stored = self.sessions.get(session.session_id)
            request = stored.context.get("resolved_request") or getattr(stored, "request", "")
        answers = session.context.get("user_answers", [])
        if answers:
            request = f"{request}\n\nاطلاعات تکمیلی کاربر:\n" + "\n".join(
                f"{item['question']} {item['answer']}" for item in answers
            )
        report = self.runtime.run(request)
        return self.sessions.complete(session.session_id, report.to_dict())

    @classmethod
    def _is_ambiguous(cls, request: str) -> bool:
        text = " ".join(request.strip().lower().split())
        return not text or text in cls.GENERIC_REQUESTS or len(text) < 12
