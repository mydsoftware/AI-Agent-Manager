from __future__ import annotations

from typing import Callable, Dict, List

from .registry import AgentRegistry
from .task import Task


class Manager:
    """Orchestrates specialist agents through a dependency-aware loop."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.tasks: Dict[str, Task] = {}
        self.handlers: Dict[str, Callable[[Task], str]] = {}

    def add_task(self, task: Task) -> None:
        if task.id in self.tasks:
            raise ValueError(f"Task already exists: {task.id}")
        self.registry.get(task.agent)
        self.tasks[task.id] = task

    def register_handler(self, agent_name: str, handler: Callable[[Task], str]) -> None:
        self.registry.get(agent_name)
        self.handlers[agent_name] = handler

    def ready_tasks(self) -> List[Task]:
        return [
            task for task in self.tasks.values()
            if task.status == "pending"
            and all(dep in self.tasks and self.tasks[dep].status == "done" for dep in task.depends_on)
        ]

    def run_once(self) -> List[Task]:
        processed: List[Task] = []
        for task in self.ready_tasks():
            handler = self.handlers.get(task.agent)
            if handler is None:
                continue
            task.status = "running"
            try:
                task.result = handler(task)
                task.status = "done"
            except Exception as exc:
                task.result = str(exc)
                task.status = "failed"
            processed.append(task)
        return processed

    def run(self, max_cycles: int = 100) -> Dict[str, Task]:
        for _ in range(max_cycles):
            if not self.tasks or all(t.status in {"done", "failed"} for t in self.tasks.values()):
                break
            before = {k: v.status for k, v in self.tasks.items()}
            self.run_once()
            after = {k: v.status for k, v in self.tasks.items()}
            if before == after:
                break
        return dict(self.tasks)
