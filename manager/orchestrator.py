from __future__ import annotations

from manager.context import AgentContext
from manager.correction_loop import CorrectionLoop
from manager.decision import DecisionEngine
from manager.intention import IntentParser
from manager.memory import Memory
from manager.multi_plan import MultiAgentPlanner
from manager.replanner import DynamicReplanner
from manager.report import ManagerReport
from manager.executor import TaskExecutor
from manager.supervisor import Supervisor, SupervisorAction


class ManagerOrchestrator:
    """تمام اجزای Manager را برای اجرای یک درخواست هماهنگ می‌کند."""

    def __init__(self, memory: Memory | None = None) -> None:
        self.intent_parser = IntentParser()
        self.decision_engine = DecisionEngine()
        self.multi_agent_planner = MultiAgentPlanner()
        self.replanner = DynamicReplanner(self.multi_agent_planner)
        self.memory = memory or Memory()
        self.supervisor = Supervisor()

    def execute(self, request: str, executor: TaskExecutor, agent: str | None = None) -> ManagerReport:
        """درخواست را تحلیل، برنامه‌ریزی و اجرا می‌کند."""
        intent = self.intent_parser.parse(request)
        decision = self.decision_engine.decide(intent)
        selected_agent = agent or decision.agent
        if agent:
            decision.agent = agent
            decision.reason = "ایجنت توسط درخواست‌کننده مشخص شده است."
            decision.confidence = 1.0
        intent.agent = selected_agent
        self.memory.add("تصمیم Manager", {
            "agent": selected_agent,
            "reason": decision.reason,
            "confidence": decision.confidence,
        })

        context = AgentContext()
        correction_loop = CorrectionLoop(executor.loop, context=context)
        plan = self.multi_agent_planner.plan(intent).tasks
        if agent:
            for task in plan:
                task.agent = selected_agent

        completed_tasks = []
        replans = 0
        index = 0

        while index < len(plan):
            task = plan[index]
            self.memory.add("شروع Task", {"id": task.id, "agent": task.agent})
            result_task = correction_loop.run(task)
            completed_tasks.append(result_task)
            supervisor_decision = self.supervisor.decide(result_task)
            self.memory.add("تصمیم Supervisor", {
                "task": result_task.id,
                "action": supervisor_decision.action.value,
                "reason": supervisor_decision.reason,
            })
            self.memory.add("پایان Task", {
                "id": result_task.id,
                "status": result_task.status.value,
                "error": result_task.error,
            })

            if supervisor_decision.action == SupervisorAction.STOP:
                break
            if supervisor_decision.action in (SupervisorAction.RETRY, SupervisorAction.SKIP):
                if replans >= 2:
                    break
                replanned = self.replanner.replan(intent, completed_tasks, supervisor_decision)
                replans += 1
                self.memory.add("بازطراحی برنامه", replanned.reason)
                plan = completed_tasks + replanned.tasks
                index = len(completed_tasks)
                continue
            index += 1

        return ManagerReport(completed_tasks)
