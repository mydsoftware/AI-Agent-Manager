from __future__ import annotations

from manager.memory import Memory
from manager.recovery import ErrorRecovery
from manager.router import Router
from manager.task import Task


class AgenticLoop:
    """حلقه اجرای یک Task؛ سیاست Retry در TaskExecutor متمرکز است تا Retry ضرب نشود."""

    def __init__(self, router: Router, memory: Memory | None = None, recovery: ErrorRecovery | None = None) -> None:
        self.router = router
        self.memory = memory or Memory()
        # TaskExecutor مالک چرخه retry است. Recovery داخلی بدون retry جلوی انفجار
        # ترکیبیِ (recovery retries × task retries) را می‌گیرد.
        self.recovery = recovery or ErrorRecovery(policy=None)
        self.recovery.policy.max_retries = 0

    def run(self, tasks: list[Task]) -> list[str]:
        """وظایف آماده اجرا را اجرا می‌کند؛ هر Task فقط یک بار در هر attempt اجرا می‌شود."""
        results: list[str] = []
        for task in tasks:
            agent = self.router.route(task)
            self.memory.add("شروع وظیفه", {"id": task.id, "attempt": task.attempts})
            try:
                result = self.recovery.run(lambda: agent.run(task))
                self.memory.add("پایان موفق وظیفه", {"id": task.id, "result": result, "attempt": task.attempts})
                results.append(result)
            except Exception as error:
                self.memory.add("شکست وظیفه", {"id": task.id, "error": str(error), "attempt": task.attempts})
                raise
        return results
