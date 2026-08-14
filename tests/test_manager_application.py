from __future__ import annotations

from agents.registry import SpecialistRegistry
from manager.application import ManagerApplication
from manager.task import Task


class FakeAgent:
    name = "fake"

    def run(self, task: Task) -> str:
        return f"انجام شد: {task.id}"


def test_manager_application_routes_to_specialist_agent() -> None:
    registry = SpecialistRegistry()
    registry.register(FakeAgent)
    manager = ManagerApplication(registry=registry)

    result = manager.run(Task("job-1", "کار آزمایشی", "تست", "fake"))

    assert result == "انجام شد: job-1"
    assert manager.agents() == ["fake"]


def test_manager_application_uses_real_default_registry() -> None:
    manager = ManagerApplication()
    assert "github-project" in manager.agents()
