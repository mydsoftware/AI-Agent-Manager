from __future__ import annotations

from typing import Any
from manager.decision import DecisionEngine
from manager.intention import IntentParser
from manager.user_session import UserSessionManager, UserSession


class SessionRuntime:
    """مرز اجرای درخواست کاربر، شفاف‌سازی و تحویل خروجی نهایی."""

    def __init__(self, sessions: UserSessionManager | None = None, runtime: Any | None = None) -> None:
        self.sessions = sessions or UserSessionManager()
        if runtime is None:
            from runtime import ManagerRuntime
            runtime = ManagerRuntime()
        self.runtime = runtime
        self.intent_parser = IntentParser()
        self.decision_engine = DecisionEngine(getattr(runtime, "governance", None))

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
            session.stage = "clarification"
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

    @staticmethod
    def _serialize_output(output: Any) -> Any:
        if hasattr(output, "to_dict"):
            return output.to_dict()
        if isinstance(output, dict):
            return output
        return {"result": output}

    def _execute(self, session: UserSession) -> UserSession:
        session.status = "running"
        session.stage = "planning"
        session = self.sessions.update(session)

        intent = self.intent_parser.parse(session.request)
        decision = self.decision_engine.decide(intent)
        session.stage = "execution"
        session = self.sessions.update(session)

        try:
            output = self.runtime.run(session.request, agent=decision.agent)
        except TypeError:
            output = self.runtime.run(session.request)

        session.output = {
            "request": session.request,
            "agent": decision.agent,
            "decision": {
                "reason": decision.reason,
                "confidence": decision.confidence,
            },
            "report": self._serialize_output(output),
        }
        session.status = "completed"
        session.stage = "delivery"
        return self.sessions.update(session)
