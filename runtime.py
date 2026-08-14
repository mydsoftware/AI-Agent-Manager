from __future__ import annotations

from agents.registry import create_default_registry
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.planner import Planner
from manager.report import ManagerReport
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

    def run(self, request: str, agent: str = "developer") -> ManagerReport:
        """درخواست کاربر را برنامه‌ریزی، اجرا و گزارش می‌کند."""
        tasks = self.planner.plan(request, agent)
        try:
            self.executor.run(tasks)
        except Exception:
            pass
        return ManagerReport(tasks)

    def run_tasks(self, tasks: list[Task]) -> ManagerReport:
        """مجموعه‌ای از وظایف آماده را اجرا و گزارش می‌کند."""
        try:
            self.executor.run(tasks)
        except Exception:
            pass
        return ManagerReport(tasks)


if __name__ == "__main__":
    runtime = ManagerRuntime()
    report = runtime.run("بررسی اولیه سیستم مدیریت ایجنت‌ها")
    print(report.to_dict())
