from __future__ import annotations

from manager.task import Task
from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """ایجنت تخصصی تحقیق و جمع‌آوری اطلاعات."""

    name = "research"

    def run(self, task: Task) -> str:
        """در نسخه اولیه، اجرای تحقیق را به محیط میزبان واگذار می‌کند."""
        return f"وظیفه تحقیق دریافت شد: {task.id}"
