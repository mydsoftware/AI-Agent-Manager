from __future__ import annotations

from agents.registry import SpecialistRegistry
from manager.task import Task


class Router:
    """هر وظیفه را به ایجنت تخصصی ثبت‌شده مربوط می‌کند."""

    def __init__(self, registry: SpecialistRegistry) -> None:
        self.registry = registry

    def route(self, task: Task):
        """ایجنت مناسب وظیفه را بر اساس نام ثبت‌شده برمی‌گرداند."""
        return self.registry.get(task.agent)
