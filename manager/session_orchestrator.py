from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manager.context import AgentContext
from manager.session_store import SessionStore


@dataclass(frozen=True)
class SessionOrchestrationResult:
    session_id: str
    status: str
    stage: str
    question: str | None = None
    context: dict[str, Any] | None = None


class SessionOrchestrator:
    """Connects persistent sessions to the real Manager input/resume flow."""

    def __init__(self, store: SessionStore | None = None) -> None:
        self.store = store or SessionStore()

    def start(self, session_id: str, request: str, stage: str = "requirements") -> SessionOrchestrationResult:
        session = self.store.create(session_id, request=request, stage=stage)
        return self._result(session)

    def ask(self, session_id: str, question: str) -> SessionOrchestrationResult:
        session = self.store.ask(session_id, question)
        return self._result(session)

    def answer(self, session_id: str, answer: str, next_stage: str | None = None) -> SessionOrchestrationResult:
        session = self.store.answer(session_id, answer, next_stage=next_stage)
        return self._result(session)

    def context(self, session_id: str) -> AgentContext:
        session = self.store.load(session_id)
        context = AgentContext()
        for key, value in session.get("context", {}).items():
            context.set(key, value)
        return context

    @staticmethod
    def _result(session: dict[str, Any]) -> SessionOrchestrationResult:
        return SessionOrchestrationResult(
            session_id=session["session_id"],
            status=session["status"],
            stage=session["stage"],
            question=session.get("question"),
            context=session.get("context", {}),
        )
