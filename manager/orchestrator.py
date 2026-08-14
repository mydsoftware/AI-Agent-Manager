from __future__ import annotations

from manager.context import AgentContext
from manager.correction_loop import CorrectionLoop
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
        """درخواست را تحلیل، برنامه‌ریزی، اجرا و در صورت نیاز اصلاح می‌کند."""
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
        correction_loop = CorrectionLoop(executor.loop)
        completed_tasks = []

        for task in plan.tasks:
            self.memory.add("شروع Task", {"id": task.id, "agent": task.agent})
            result_task = correction_loop.run(task)
            completed_tasks.append(result_task)
            self.memory.add("پایان Task", {
                "id": result_task.id,
                "status": result_task.status.value,
                "error": result_task.error,
            })
            if result_task.status.value == "failed":
                self.memory.add("توقف زنجیره", result_task.id)
                break

        return ManagerReport(completed_tasks)
