from __future__ import annotations

from manager.decision import DecisionEngine
from manager.intention import IntentParser
from manager.memory import Memory
from manager.multi_plan import MultiAgentPlanner
from manager.report import ManagerReport
from manager.executor import TaskExecutor


class ManagerOrchestrator:
    """تمام اجزای Manager را برای اجرای یک درخواست هماهنگ می‌کند."""

    def __init__(self, memory: Memory | None = None) -> None:
        self.intent_parser = IntentParser()
        self.decision_engine = DecisionEngine()
        self.multi_agent_planner = MultiAgentPlanner()
        self.memory = memory or Memory()

    def execute(self, request: str, executor: TaskExecutor, agent: str | None = None) -> ManagerReport:
        """درخواست را تحلیل، تصمیم‌گیری، چندایجنتی برنامه‌ریزی و اجرا می‌کند."""
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
        plan = self.multi_agent_planner.plan(intent)
        self.memory.add("شروع اجرای درخواست", {"request": request, "tasks": len(plan.tasks)})
        try:
            executor.run(plan.tasks)
        except Exception as error:
            self.memory.add("خطا در اجرای درخواست", str(error))
        self.memory.add("پایان اجرای درخواست", {"tasks": len(plan.tasks)})
        return ManagerReport(plan.tasks)
