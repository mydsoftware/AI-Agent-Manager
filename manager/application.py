from __future__ import annotations

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
        """اگر ایجنت صریح تعیین نشده باشد، ایجنت مناسب را خودکار انتخاب و سپس اجرا می‌کند."""
        decision = self.intelligent_router.select(task)
        routed_task = Task(id=task.id, agent=decision.agent, description=task.description)
        return self.executor.run([routed_task])[0]

    def run_many(self, tasks: list[Task]) -> list[str]:
        """چند وظیفه را با انتخاب خودکار ایجنت و رعایت وابستگی‌ها اجرا می‌کند."""
        routed = []
        for task in tasks:
            decision = self.intelligent_router.select(task)
            routed.append(Task(id=task.id, agent=decision.agent, description=task.description))
        return self.executor.run(routed)

    def route(self, task: Task) -> str:
        """بدون اجرا، ایجنت انتخاب‌شده و دلیل انتخاب را برمی‌گرداند."""
        return self.intelligent_router.select(task).agent

    def agents(self) -> list[str]:
        """فهرست ایجنت‌های قابل استفاده Manager را برمی‌گرداند."""
        return self.registry.names()
