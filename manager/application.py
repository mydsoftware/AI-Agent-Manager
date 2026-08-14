from __future__ import annotations

from agents.registry import SpecialistRegistry, create_default_registry
from manager.agent_governance import AgentGovernance
from manager.executor import TaskExecutor
from manager.loop import AgenticLoop
from manager.router import Router
from manager.task import Task


class ManagerApplication:
    """درگاه اجرایی اصلی Manager Agent برای وظایف تخصصی."""

    def __init__(self, registry: SpecialistRegistry | None = None, governance: AgentGovernance | None = None) -> None:
        self.registry = registry or create_default_registry()
        self.router = Router(self.registry, governance)
        self.loop = AgenticLoop(self.router)
        self.executor = TaskExecutor(self.loop)

    def run(self, task: Task) -> str:
        """وظیفه را از مسیری واحد به ایجنت تخصصی مناسب می‌سپارد."""
        return self.executor.run([task])[0]

    def run_many(self, tasks: list[Task]) -> list[str]:
        """چند وظیفه را با رعایت وابستگی‌ها اجرا می‌کند."""
        return self.executor.run(tasks)

    def agents(self) -> list[str]:
        """فهرست ایجنت‌های قابل استفاده Manager را برمی‌گرداند."""
        return self.registry.names()
