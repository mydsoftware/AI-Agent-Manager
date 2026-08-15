from __future__ import annotations

from manager.context import AgentContext
from manager.context_loop import ContextAwareExecutor
from manager.loop import AgenticLoop
from manager.task import Task


class AgentOrchestrator:
    """هماهنگ‌کننده اجرای زنجیره‌ای Agentها با Context مشترک."""

    def __init__(self, loop: AgenticLoop, context: AgentContext | None = None) -> None:
        self.context = context or AgentContext()
        self.executor = ContextAwareExecutor(loop, self.context)

    def run(self, tasks: list[Task]) -> list[str]:
        return self.executor.run(tasks) if tasks else []
