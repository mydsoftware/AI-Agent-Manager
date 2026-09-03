from __future__ import annotations

from dataclasses import dataclass

from manager.task import Task
from manager.task_status import TaskStatus


@dataclass
class ManagerReport:
    """گزارش نهایی اجرای مجموعه وظایف."""

    tasks: list[Task]

    @property
    def total(self) -> int:
        return len(self.tasks)

    @property
    def successful(self) -> int:
        return sum(task.status == TaskStatus.SUCCESS for task in self.tasks)

    @property
    def failed(self) -> int:
        return sum(task.status == TaskStatus.FAILED for task in self.tasks)

    @property
    def blocked(self) -> int:
        return sum(task.status == TaskStatus.BLOCKED for task in self.tasks)

    @property
    def status(self) -> TaskStatus:
        if self.failed:
            return TaskStatus.FAILED
        if self.blocked:
            return TaskStatus.BLOCKED
        if self.total and self.successful == self.total:
            return TaskStatus.SUCCESS
        return TaskStatus.PENDING

    def to_dict(self) -> dict:
        """گزارش را همراه جزئیات اجرای هر Task به API می‌دهد."""
        return {
            "status": self.status.value,
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "blocked": self.blocked,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "agent": task.agent,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                    "attempts": task.attempts,
                    "max_attempts": task.max_attempts,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                }
                for task in self.tasks
            ],
        }
