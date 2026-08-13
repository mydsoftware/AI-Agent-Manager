from __future__ import annotations

from manager.memory import Memory
from manager.router import Router
from manager.task import Task


class AgenticLoop:
    """حلقه اجرای وظایف و ثبت نتیجه هر مرحله."""

    def __init__(self, router: Router, memory: Memory | None = None) -> None:
        self.router = router
        self.memory = memory or Memory()

    def run(self, tasks: list[Task]) -> list[str]:
        """وظایف آماده اجرا را به ترتیب اجرا می‌کند."""
        results: list[str] = []
        for task in tasks:
            agent = self.router.route(task)
            self.memory.add("شروع وظیفه", task.id)
            result = agent.run(task)
            self.memory.add("پایان وظیفه", {"id": task.id, "result": result})
            results.append(result)
        return results
