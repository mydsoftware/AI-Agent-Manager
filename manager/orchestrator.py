from __future__ import annotations

from manager.intention import IntentParser
from manager.memory import Memory
from manager.planner import Planner
from manager.report import ManagerReport
from manager.task_factory import TaskFactory
from manager.executor import TaskExecutor


class ManagerOrchestrator:
    """تمام اجزای Manager را برای اجرای یک درخواست هماهنگ می‌کند."""

    def __init__(self, planner: Planner | None = None, memory: Memory | None = None) -> None:
        self.intent_parser = IntentParser()
        self.planner = planner or Planner(self.intent_parser)
        self.task_factory = TaskFactory()
        self.memory = memory or Memory()

    def execute(self, request: str, executor: TaskExecutor, agent: str | None = None) -> ManagerReport:
        """درخواست را تحلیل، به وظایف تبدیل و اجرا می‌کند."""
        intent = self.intent_parser.parse(request)
        if agent:
            intent.agent = agent
        tasks = self.task_factory.create(intent)
        self.memory.add("شروع اجرای درخواست", request)
        try:
            executor.run(tasks)
        except Exception as error:
            self.memory.add("خطا در اجرای درخواست", str(error))
        self.memory.add("پایان اجرای درخواست", {"tasks": len(tasks)})
        return ManagerReport(tasks)
