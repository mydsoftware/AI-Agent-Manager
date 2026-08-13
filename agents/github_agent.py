from __future__ import annotations

from manager.task import Task
from adapters.github_adapter import GitHubAdapter
from .base_agent import BaseAgent


class GitHubAgent(BaseAgent):
    """ایجنت تخصصی مدیریت عملیات GitHub."""

    name = "github"

    def __init__(self, adapter: GitHubAdapter | None = None) -> None:
        self.adapter = adapter

    def run(self, task: Task) -> str:
        """وظیفه GitHub را دریافت می‌کند و اجرای واقعی را به Adapter می‌سپارد."""
        if self.adapter is None:
            return f"وظیفه GitHub دریافت شد اما رابط GitHub تزریق نشده است: {task.id}"
        return f"وظیفه GitHub آماده اجرا است: {task.id}"
