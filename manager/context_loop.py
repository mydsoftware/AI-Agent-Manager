from __future__ import annotations

from manager.context import AgentContext
from manager.loop import AgenticLoop
from manager.task import Task


class ContextAwareExecutor:
    """خروجی هر Agent را در زمینه مشترک ثبت و به مرحله بعد منتقل می‌کند."""

    def __init__(self, loop: AgenticLoop, context: AgentContext | None = None) -> None:
        self.loop = loop
        self.context = context or AgentContext()

    def run(self, tasks: list[Task]) -> list[str]:
        """وظایف را به ترتیب وابستگی اجرا و خروجی هر مرحله را ثبت می‌کند."""
        pending = {task.id: task for task in tasks}
        results: list[str] = []

        while pending:
            ready = [
                task for task in pending.values()
                if all(dependency not in pending for dependency in task.depends_on)
            ]
            if not ready:
                raise RuntimeError("زنجیره وظایف متوقف شد؛ وابستگی قابل حل نیست.")

            for task in ready:
                dependency_outputs = {
                    dependency: self.context.get(dependency)
                    for dependency in task.depends_on
                }
                if dependency_outputs:
                    task.description = (
                        f"{task.description}\n\nخروجی مراحل قبلی:\n{dependency_outputs}"
                    )
                result = self.loop.run([task])[0]
                task.result = result
                self.context.set(task.id, result)
                results.append(result)
                del pending[task.id]

        return results
