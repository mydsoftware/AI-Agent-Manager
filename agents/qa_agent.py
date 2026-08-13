from __future__ import annotations

from manager.task import Task
from .base_agent import BaseAgent


class QAAgent(BaseAgent):
    """ایجنت تخصصی کنترل کیفیت و تست."""

    name = "qa"

    def run(self, task: Task) -> str:
        """در نسخه اولیه، اجرای تست به محیط میزبان واگذار می‌شود."""
        return f"وظیفه کنترل کیفیت دریافت شد: {task.id}"
