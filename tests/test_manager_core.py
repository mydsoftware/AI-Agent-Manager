from __future__ import annotations

from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.recovery import ErrorRecovery, RecoveryPolicy
from manager.router import Router
from manager.task import Task
from manager.task_status import TaskStatus
from agents.registry import create_default_registry


class Agent آزمایشی:
    """ایجنت ساختگی برای آزمایش حلقه اجرا."""

    name = "developer"


def test_registry_has_required_agents() -> None:
    """Registry پیش‌فرض باید تمام ایجنت‌های اصلی را داشته باشد."""
    names = create_default_registry().names()
    assert {"research", "developer", "qa", "github"}.issubset(names)


def test_retry_policy() -> None:
    """بازیابی باید پس از چند شکست، در اجرای موفق متوقف شود."""
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("خطای آزمایشی")
        return "موفق"

    recovery = ErrorRecovery(RecoveryPolicy(max_retries=3))
    assert recovery.run(operation) == "موفق"
    assert attempts == 3


def test_dependency_order() -> None:
    """وظیفه وابسته باید فقط پس از موفقیت وابستگی اجرا شود."""
    class FakeAgent:
        def run(self, task: Task) -> str:
            return task.id

    class FakeRegistry:
        def get(self, name: str):
            return FakeAgent()

    tasks = [
        Task("a", "اول", "اول", "developer"),
        Task("b", "دوم", "دوم", "developer", depends_on=["a"]),
    ]
    loop = AgenticLoop(Router(FakeRegistry()), Memory())
    results = TaskExecutor(loop).run(tasks)

    assert results == ["a", "b"]
    assert tasks[0].status == TaskStatus.SUCCESS
    assert tasks[1].status == TaskStatus.SUCCESS
