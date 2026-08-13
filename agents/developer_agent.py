from __future__ import annotations

from manager.task import Task
from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):
    """ایجنت تخصصی توسعه نرم‌افزار."""

    name = "developer"

    def run(self, task: Task) -> str:
        """در نسخه اولیه، اجرای تغییرات کد به محیط میزبان واگذار می‌شود."""
        return f"وظیفه توسعه دریافت شد: {task.id}"
