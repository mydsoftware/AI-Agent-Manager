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
        """وظیفه را تحلیل، مسیریابی و با آماده‌سازی لازم اجرا می‌کند."""
        decision = self.intelligent_router.select(task)
        routed_task = self._prepare_task(task, decision.agent, decision.engineering)
        return self.executor.run([routed_task])[0]

    def run_many(self, tasks: list[Task]) -> list[str]:
        """چند وظیفه را با انتخاب خودکار ایجنت و رعایت وابستگی‌ها اجرا می‌کند."""
        routed = []
        for task in tasks:
            decision = self.intelligent_router.select(task)
            routed.append(self._prepare_task(task, decision.agent, decision.engineering))
        return self.executor.run(routed)

    def route(self, task: Task) -> str:
        """بدون اجرا، ایجنت انتخاب‌شده را برمی‌گرداند."""
        return self.intelligent_router.select(task).agent

    def agents(self) -> list[str]:
        """فهرست ایجنت‌های قابل استفاده Manager را برمی‌گرداند."""
        return self.registry.names()

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
