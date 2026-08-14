from __future__ import annotations

from manager.decision import DecisionEngine
from manager.intention import IntentParser
from manager.memory import Memory
from manager.report import ManagerReport
from manager.task_factory import TaskFactory
from manager.executor import TaskExecutor


class ManagerOrchestrator:
    """تمام اجزای Manager را برای اجرای یک درخواست هماهنگ می‌کند."""

    def __init__(self, memory: Memory | None = None) -> None:
        self.intent_parser = IntentParser()
        self.decision_engine = DecisionEngine()
        self.task_factory = TaskFactory()
        self.memory = memory or Memory()

    def execute(self, request: str, executor: TaskExecutor, agent: str | None = None) -> ManagerReport:
        """درخواست را تحلیل، تصمیم‌گیری، به وظایف تبدیل و اجرا می‌کند."""
        intent = self.intent_parser.parse(request)
        decision = self.decision_engine.decide(intent)
        if agent:
            decision.agent = agent
            decision.reason = "ایجنت توسط درخواست‌کننده مشخص شده است."
            decision.confidence = 1.0
        intent.agent = decision.agent
        self.memory.add("تصمیم Manager", {
            "agent": decision.agent,
            "reason": decision.reason,
            "confidence": decision.confidence,
        })
        tasks = self.task_factory.create(intent)
        self.memory.add("شروع اجرای درخواست", request)
        try:
            executor.run(tasks)
        except Exception as error:
            self.memory.add("خطا در اجرای درخواست", str(error))
        self.memory.add("پایان اجرای درخواست", {"tasks": len(tasks)})
        return ManagerReport(tasks)
