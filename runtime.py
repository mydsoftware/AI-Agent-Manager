from __future__ import annotations

from agents.registry import create_default_registry
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.memory import Memory
from manager.orchestrator import ManagerOrchestrator
from manager.persistent_memory import PersistentMemory
from manager.report import ManagerReport
from manager.router import Router
from manager.task import Task


class ManagerRuntime:
    """محیط اجرای اصلی مدیر چندایجنتی."""

    def __init__(self, database_path: str = "data/manager.db") -> None:
        self.registry = create_default_registry()
        self.router = Router(self.registry)
        self.memory = Memory()
        self.persistent_memory = PersistentMemory(database_path)
        self.loop = AgenticLoop(self.router, self.memory)
        self.executor = TaskExecutor(self.loop)
        self.orchestrator = ManagerOrchestrator(memory=self.memory)

    def run(self, request: str, agent: str = "developer") -> ManagerReport:
        """درخواست کاربر را از تحلیل نیت تا گزارش نهایی اجرا می‌کند."""
        self.persistent_memory.add("شروع درخواست", {"request": request, "agent": agent})
        report = self.orchestrator.execute(request, self.executor, agent)
        self.persistent_memory.add("پایان درخواست", report.to_dict())
        return report

    def run_tasks(self, tasks: list[Task]) -> ManagerReport:
        """مجموعه‌ای از وظایف آماده را اجرا، ثبت و گزارش می‌کند."""
        try:
            self.executor.run(tasks)
        except Exception as error:
            self.persistent_memory.add("خطای اجرای وظایف", str(error))
        report = ManagerReport(tasks)
        self.persistent_memory.add("پایان اجرای وظایف", report.to_dict())
        return report


if __name__ == "__main__":
    runtime = ManagerRuntime()
    report = runtime.run("بررسی اولیه سیستم مدیریت ایجنت‌ها")
    print(report.to_dict())
