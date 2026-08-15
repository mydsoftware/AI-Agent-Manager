from __future__ import annotations

from manager.context import AgentContext
from manager.loop import AgenticLoop
from manager.task import Task


class TaskScheduler:
    """زمان‌بندی Taskها بر اساس وابستگی و اولویت."""

    def __init__(self, loop: AgenticLoop, context: AgentContext | None = None) -> None:
        self.loop = loop
        self.context = context or AgentContext()

    def run(self, tasks: list[Task]) -> list[str]:
        pending = {task.id: task for task in tasks}
        results: list[str] = []
        while pending:
            ready = [t for t in pending.values() if all(d not in pending for d in t.depends_on)]
            if not ready:
                raise RuntimeError("وابستگی‌های Task قابل حل نیستند")
            ready.sort(key=lambda t: (-getattr(t, "priority", 0), t.id))
            for task in ready:
                result = self.loop.run([task])[0]
                task.result = result
                self.context.set(task.id, result)
                results.append(result)
                del pending[task.id]
        return results
