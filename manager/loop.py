from __future__ import annotations

from manager.memory import Memory
from manager.recovery import ErrorRecovery
from manager.router import Router
from manager.task import Task


class AgenticLoop:
    """حلقه اجرای وظایف، ثبت نتیجه و بازیابی خطا."""

    def __init__(self, router: Router, memory: Memory | None = None, recovery: ErrorRecovery | None = None) -> None:
        self.router = router
        self.memory = memory or Memory()
        self.recovery = recovery or ErrorRecovery()

    def run(self, tasks: list[Task]) -> list[str]:
        """وظایف آماده اجرا را به ترتیب اجرا می‌کند و خطاهای قابل بازیابی را تکرار می‌کند."""
        results: list[str] = []
        for task in tasks:
            agent = self.router.route(task)
            self.memory.add("شروع وظیفه", task.id)
            try:
                result = self.recovery.run(lambda: agent.run(task))
                self.memory.add("پایان موفق وظیفه", {"id": task.id, "result": result})
                results.append(result)
            except Exception as error:
                self.memory.add("شکست وظیفه", {"id": task.id, "error": str(error)})
                raise
        return results
