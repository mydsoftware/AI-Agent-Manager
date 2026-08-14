from __future__ import annotations

from agents.registry import create_default_registry
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.planner import Planner
from manager.router import Router
from manager.task import Task


class ManagerRuntime:
    """محیط اجرای اصلی مدیر چندایجنتی."""

    def __init__(self) -> None:
        self.registry = create_default_registry()
        self.router = Router(self.registry)
        self.memory = Memory()
        self.loop = AgenticLoop(self.router, self.memory)
        self.executor = TaskExecutor(self.loop)
        self.planner = Planner()

    def run(self, request: str, agent: str = "developer") -> list[str]:
        """درخواست کاربر را برنامه‌ریزی و با رعایت وابستگی‌ها اجرا می‌کند."""
        tasks = self.planner.plan(request, agent)
        return self.executor.run(tasks)

    def run_tasks(self, tasks: list[Task]) -> list[str]:
        """مجموعه‌ای از وظایف آماده را با Executor اجرا می‌کند."""
        return self.executor.run(tasks)


if __name__ == "__main__":
    runtime = ManagerRuntime()
    for result in runtime.run("بررسی اولیه سیستم مدیریت ایجنت‌ها"):
        print(result)
