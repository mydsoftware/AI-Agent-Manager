from __future__ import annotations

from manager.context import AgentContext
from manager.loop import AgenticLoop
from manager.task import Task


class ContextAgentRunner:
    """خروجی Agent قبلی را به صورت زمینه به Agent بعدی منتقل می‌کند."""

    def __init__(self, loop: AgenticLoop, context: AgentContext | None = None) -> None:
        self.loop = loop
        self.context = context or AgentContext()

    def run(self, tasks: list[Task]) -> list[str]:
        """Taskها را بر اساس وابستگی اجرا و خروجی هر Task را ثبت می‌کند."""
        pending = {task.id: task for task in tasks}
        results: list[str] = []
        completed: set[str] = set()

        while pending:
            ready = [
                task for task in pending.values()
                if all(dependency in completed for dependency in task.depends_on)
            ]
            if not ready:
                raise RuntimeError("زنجیره وظایف متوقف شد؛ وابستگی قابل حل نیست.")

            for task in ready:
                inputs = {
                    dependency: self.context.get(dependency)
                    for dependency in task.depends_on
                }
                if inputs:
                    task.description = f"{task.description}\n\nخروجی Agentهای قبلی:\n{inputs}"
                result = self.loop.run([task])[0]
                task.result = result
                task.status = task.status.SUCCESS
                self.context.set(task.id, result)
                completed.add(task.id)
                results.append(result)
                del pending[task.id]

        return results
