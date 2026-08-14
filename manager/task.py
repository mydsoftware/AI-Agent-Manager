from dataclasses import dataclass, field

from manager.task_status import TaskStatus


@dataclass
class Task:
    """مدل یک وظیفه قابل اجرا توسط ایجنت."""

    id: str
    title: str
    description: str
    agent: str
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    error: str | None = None
