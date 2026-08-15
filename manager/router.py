from __future__ import annotations

from agents.registry import SpecialistRegistry
from manager.agent_governance import AgentGovernance
from manager.task import Task


class Router:
    """هر وظیفه را فقط به ایجنت تخصصی ثبت و مجاز مربوط می‌کند."""

    def __init__(self, registry: SpecialistRegistry, governance: AgentGovernance | None = None) -> None:
        self.registry = registry
        self.governance = governance

    def route(self, task: Task):
        """ایجنت مناسب وظیفه را پس از بررسی دسترسی برمی‌گرداند."""
        if self.governance is not None and not self.governance.can_use(task.agent):
            raise PermissionError(f"ایجنت «{task.agent}» غیرفعال یا غیرمجاز است.")
        return self.registry.get(task.agent)
