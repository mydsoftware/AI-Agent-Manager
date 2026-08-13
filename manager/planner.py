from __future__ import annotations

from manager.task import Task


class Planner:
    """درخواست کاربر را به وظایف قابل اجرا تبدیل می‌کند."""

    def plan(self, request: str, agent: str = "developer") -> list[Task]:
        """برای نسخه اولیه یک وظیفه از درخواست کاربر ایجاد می‌کند."""
        return [
            Task(
                id="task-1",
                title="اجرای درخواست کاربر",
                description=request,
                agent=agent,
            )
        ]
