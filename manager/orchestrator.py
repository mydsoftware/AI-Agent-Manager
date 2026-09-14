from __future__ import annotations

import json

from manager.context import AgentContext
from manager.correction_loop import CorrectionLoop
from manager.decision import DecisionEngine
from manager.intent_router import IntentRouter
from manager.intention import IntentParser
from manager.memory import Memory
from manager.multi_plan import MultiAgentPlanner
from manager.replanner import DynamicReplanner
from manager.report import ManagerReport
from manager.executor import TaskExecutor
from manager.supervisor import Supervisor, SupervisorAction
from manager.task import Task


class ManagerOrchestrator:
    """تمام اجزای Manager را برای اجرای خودکار یک درخواست هماهنگ می‌کند."""

    def __init__(self, memory: Memory | None = None) -> None:
        self.intent_parser = IntentParser()
        self.intent_router = IntentRouter()
        self.decision_engine = DecisionEngine()
        self.multi_agent_planner = MultiAgentPlanner()
        self.replanner = DynamicReplanner(self.multi_agent_planner)
        self.memory = memory or Memory()
        self.supervisor = Supervisor()

    def execute(self, request: str, executor: TaskExecutor, agent: str | None = None) -> ManagerReport:
        route = self.intent_router.classify(request)
        intent = self.intent_parser.parse(request)
        decision = self.decision_engine.decide(intent)

        if agent:
            decision.agent = agent
            decision.reason = "ایجنت توسط درخواست‌کننده مشخص شده است."
            decision.confidence = 1.0
        elif route.role != "developer":
            decision.agent = route.role
            decision.reason = f"IntentRouter: {route.intent} / capability={route.capability}"
            decision.confidence = max(decision.confidence, 0.8)

        intent.agent = decision.agent
        self.memory.add("تصمیم Manager", {"agent": decision.agent, "reason": decision.reason, "confidence": decision.confidence, "intent": route.intent, "capability": route.capability})

        context = AgentContext()
        correction_loop = CorrectionLoop(executor.loop, context=context)
        plan = self.multi_agent_planner.plan(intent).tasks
        completed_tasks: list[Task] = []
        replans = 0
        index = 0

        while index < len(plan):
            task = plan[index]
            self.memory.add("شروع Task", {"id": task.id, "agent": task.agent})
            result_task = correction_loop.run(task)
            completed_tasks.append(result_task)
            supervisor_decision = self.supervisor.decide(result_task)
            self.memory.add("تصمیم Supervisor", {"task": result_task.id, "action": supervisor_decision.action.value, "reason": supervisor_decision.reason})
            self.memory.add("پایان Task", {"id": result_task.id, "status": result_task.status.value, "error": result_task.error})

            if result_task.agent == "developer" and result_task.status.value == "success":
                engineering_task = self._engineering_task_from_developer(result_task)
                if engineering_task is not None:
                    engineering_task.depends_on = [result_task.id]
                    plan.insert(index + 1, engineering_task)

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

    @staticmethod
    def _engineering_task_from_developer(task: Task) -> Task | None:
        """خروجی ساختاریافته Developer را مستقیماً وارد چرخه GitHub می‌کند."""
        try:
            plan = json.loads(task.result or "")
        except (TypeError, json.JSONDecodeError):
            return None
        if not isinstance(plan, dict) or plan.get("type") != "development_plan" or not plan.get("engineering_loop"):
            return None
        if not plan.get("repository") or not plan.get("branch") or not plan.get("changes"):
            return None
        command = {
            "operation": "engineering_loop",
            "repository": plan["repository"],
            "branch": plan["branch"],
            "base": plan.get("base", "main"),
            "workflow": plan.get("workflow", "ci.yml"),
            "changes": plan.get("changes", []),
            "repair_changes": plan.get("repair_changes", []),
            "pr": plan.get("pr", {}),
        }
        return Task(id=f"{task.id}:engineering", title=f"اجرای مهندسی: {task.title}", description=json.dumps(command, ensure_ascii=False), agent="github-project", capability="engineering")
