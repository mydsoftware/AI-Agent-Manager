from __future__ import annotations

import json

from agents.registry import SpecialistRegistry, create_default_registry
from manager.agent_governance import AgentGovernance
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.router import Router
from manager.task import Task
from manager.task_router import IntelligentTaskRouter


class ManagerApplication:
    """درگاه اجرایی اصلی Manager Agent برای وظایف تخصصی."""

    def __init__(self, registry: SpecialistRegistry | None = None, governance: AgentGovernance | None = None) -> None:
        self.registry = registry or create_default_registry()
        self.governance = governance
        self.router = Router(self.registry, governance)
        self.intelligent_router = IntelligentTaskRouter(self.registry, governance)
        self.loop = AgenticLoop(self.router)
        self.executor = TaskExecutor(self.loop)

    def run(self, task: Task) -> str:
        """وظیفه را تحلیل، مسیریابی و در صورت نیاز وارد چرخه مهندسی می‌کند."""
        decision = self.intelligent_router.select(task)
        if decision.agent == "developer":
            return self._run_developer_pipeline(task)
        routed_task = self._prepare_task(task, decision.agent, decision.engineering)
        return self.executor.run([routed_task])[0]

    def run_many(self, tasks: list[Task]) -> list[str]:
        """چند وظیفه را با انتخاب خودکار ایجنت و رعایت وابستگی‌ها اجرا می‌کند."""
        return [self.run(task) for task in tasks]

    def route(self, task: Task) -> str:
        """بدون اجرا، ایجنت انتخاب‌شده را برمی‌گرداند."""
        return self.intelligent_router.select(task).agent

    def agents(self) -> list[str]:
        """فهرست ایجنت‌های قابل استفاده Manager را برمی‌گرداند."""
        return self.registry.names()

    def _run_developer_pipeline(self, task: Task) -> str:
        """خروجی Developer را به چرخه اجرایی GitHub تحویل می‌دهد."""
        developer_task = Task(
            id=f"{task.id}:developer",
            title=task.title,
            description=task.description,
            agent="developer",
            depends_on=task.depends_on,
        )
        plan_raw = self.executor.run([developer_task])[0]
        try:
            plan = json.loads(plan_raw)
        except (TypeError, json.JSONDecodeError):
            return plan_raw

        if plan.get("type") != "development_plan" or not plan.get("engineering_loop"):
            return plan_raw

        command = {
            "operation": "engineering_loop",
            "repository": plan["repository"],
            "branch": plan["branch"],
            "change": plan.get("change"),
            "base": plan.get("base", "main"),
            "workflow": plan.get("workflow"),
            "repair_change": plan.get("repair_change"),
            "pr": plan.get("pr", {}),
        }
        engineering_task = Task(
            id=f"{task.id}:engineering",
            title=f"اجرای مهندسی: {task.title}",
            description=json.dumps(command, ensure_ascii=False),
            agent="github-project",
        )
        return self.executor.run([engineering_task])[0]

    def _prepare_task(self, task: Task, agent: str, engineering: bool) -> Task:
        """برای کارهای GitHub، چرخه مهندسی را در صورت وجود اطلاعات کافی فعال می‌کند."""
        description = task.description
        if engineering and agent == "github-project":
            try:
                command = json.loads(description)
            except (TypeError, json.JSONDecodeError):
                command = None
            if isinstance(command, dict) and command.get("repository") and command.get("change") and command.get("branch"):
                command.setdefault("operation", "engineering_loop")
                description = json.dumps(command, ensure_ascii=False)

        return Task(
            id=task.id,
            title=task.title,
            description=description,
            agent=agent,
            depends_on=task.depends_on,
        )
