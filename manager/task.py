"""مدل وظیفه قابل اجرا."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from manager.task_status import TaskStatus


@dataclass
class Task:
    """مدل یک وظیفه قابل اجرا توسط ایجنت."""

    id: str = ""
    title: str = ""
    description: str = ""
    agent: str = ""
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    error: str | None = None
    attempts: int = 0
    max_attempts: int = 5
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = f"task-{uuid.uuid4().hex[:8]}"

    def start(self) -> None:
        """وضعیت Task را به در حال اجرا تغییر می‌دهد."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.attempts += 1

    def complete(self, result: str) -> None:
        """Task را با نتیجه موفق تکمیل می‌کند."""
        self.status = TaskStatus.SUCCESS
        self.result = result
        self.error = None
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def fail(self, error: str) -> None:
        """Task را با خطا ناموفق علامت‌گذاری می‌کند."""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def can_retry(self) -> bool:
        """بررسی می‌کند آیا امکان تلاش مجدد وجود دارد."""
        return self.status in {TaskStatus.FAILED, TaskStatus.FIXING} and self.attempts < self.max_attempts

    def to_dict(self) -> dict[str, Any]:
        """Task را به دیکشنری تبدیل می‌کند."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "agent": self.agent,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }
