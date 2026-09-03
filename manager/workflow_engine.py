"""موتور Workflow برای تبدیل درخواست به Task Graph قابل نمایش و اجرا."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manager.decision import DecisionEngine
from manager.intention import IntentParser
from manager.multi_plan import MultiAgentPlanner
from manager.task import Task


@dataclass(frozen=True)
class WorkflowPlan:
    """برنامه استاندارد قابل مصرف توسط UI و API."""

    name: str
    description: str
    tasks: list[Task]
    selected_agent: str
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "selected_agent": self.selected_agent,
            "confidence": self.confidence,
            "reason": self.reason,
            "tasks": [task.to_dict() for task in self.tasks],
            "edges": [
                {"from": dependency, "to": task.id}
                for task in self.tasks
                for dependency in task.depends_on
            ],
        }


class WorkflowEngine:
    """Facade مرکزی برای Planning و اجرای Workflow از طریق Runtime."""

    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self.intent_parser = IntentParser()
        self.planner = MultiAgentPlanner()
        self.decision_engine = DecisionEngine(runtime.governance)

    def plan(self, request: str, agent: str | None = None) -> WorkflowPlan:
        text = request.strip()
        if not text:
            raise ValueError("درخواست Workflow نمی‌تواند خالی باشد.")

        intent = self.intent_parser.parse(text)
        decision = self.decision_engine.decide(intent)
        selected = agent.strip() if agent and agent.strip() else decision.agent
        if agent:
            if not self.runtime.governance.can_use(selected):
                raise PermissionError(f"ایجنت «{selected}» غیرفعال یا غیرمجاز است.")
            for task in self.planner.plan(intent).tasks:
                task.agent = selected
            tasks = self.planner.plan(intent).tasks
        else:
            tasks = self.planner.plan(intent).tasks

        return WorkflowPlan(
            name="dynamic_request_workflow",
            description="Workflow پویا که از Intent، Decision و Multi-Agent Planner ساخته شده است.",
            tasks=tasks,
            selected_agent=selected,
            confidence=decision.confidence,
            reason=decision.reason,
        )

    def execute(self, request: str, agent: str | None = None) -> dict[str, Any]:
        """Workflow را از مسیر ManagerRuntime واقعی اجرا می‌کند."""
        plan = self.plan(request, agent)
        report = self.runtime.run(request, agent or plan.selected_agent)
        return {"workflow": plan.to_dict(), "report": report.to_dict()}
