from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from manager.task import Task
from manager.task_status import TaskStatus


@dataclass
class ManagerReport:
    """گزارش نهایی اجرای مجموعه وظایف."""

    tasks: list[Task]

    @property
    def total(self) -> int:
        """تعداد کل وظایف را برمی‌گرداند."""
        return len(self.tasks)

    @property
    def successful(self) -> int:
        """تعداد وظایف موفق را برمی‌گرداند."""
        return sum(task.status == TaskStatus.SUCCESS for task in self.tasks)

    @property
    def failed(self) -> int:
        """تعداد وظایف ناموفق را برمی‌گرداند."""
        return sum(task.status == TaskStatus.FAILED for task in self.tasks)

    @property
    def blocked(self) -> int:
        """تعداد وظایف مسدود را برمی‌گرداند."""
        return sum(task.status == TaskStatus.BLOCKED for task in self.tasks)

    @property
    def status(self) -> TaskStatus:
        """وضعیت کلی اجرا را تعیین می‌کند."""
        if self.failed:
            return TaskStatus.FAILED
        if self.blocked:
            return TaskStatus.BLOCKED
        if self.total and self.successful == self.total:
            return TaskStatus.SUCCESS
        return TaskStatus.PENDING

    def to_dict(self) -> dict:
        """گزارش را به ساختار قابل استفاده در API تبدیل می‌کند."""
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
                }
                for task in self.tasks
            ],
        }
