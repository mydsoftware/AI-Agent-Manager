from __future__ import annotations

from manager.intention import UserIntent
from manager.task import Task


class TaskFactory:
    """از نیت تحلیل‌شده کاربر، زنجیره وظایف می‌سازد."""

    def create(self, intent: UserIntent) -> list[Task]:
        """برای هر مرحله یک Task مستقل ایجاد می‌کند."""
        if not intent.steps:
            return [
                Task(
                    id="task-1",
                    title="اجرای درخواست کاربر",
                    description=intent.goal,
                    agent=intent.agent or "developer",
                )
            ]

        tasks: list[Task] = []
        previous_id: str | None = None
        for index, step in enumerate(intent.steps, start=1):
            task_id = f"task-{index}"
            tasks.append(
                Task(
                    id=task_id,
                    title=f"مرحله {index}",
                    description=step,
                    agent=intent.agent or "developer",
                    depends_on=[previous_id] if previous_id else [],
                )
            )
            previous_id = task_id
        return tasks
