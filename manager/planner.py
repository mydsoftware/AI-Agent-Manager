from __future__ import annotations

from manager.intention import IntentParser
from manager.task import Task


class Planner:
    """درخواست کاربر را به وظایف قابل اجرا تبدیل می‌کند."""

    def __init__(self, intent_parser: IntentParser | None = None) -> None:
        self.intent_parser = intent_parser or IntentParser()

    def plan(self, request: str, agent: str | None = None) -> list[Task]:
        """درخواست را تحلیل و یک وظیفه با ایجنت مناسب ایجاد می‌کند."""
        intent = self.intent_parser.parse(request)
        selected_agent = agent or intent.agent or "developer"
        return [
            Task(
                id="task-1",
                title="اجرای درخواست کاربر",
                description=intent.goal,
                agent=selected_agent,
            )
        ]
