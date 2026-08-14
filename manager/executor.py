from __future__ import annotations

from manager.loop import AgenticLoop
from manager.task import Task
from manager.task_status import TaskStatus


class TaskExecutor:
    """وظایف را با رعایت وابستگی‌ها برای حلقه ایجنت اجرا می‌کند."""

    def __init__(self, loop: AgenticLoop) -> None:
        self.loop = loop

    def run(self, tasks: list[Task]) -> list[str]:
        """وظایف را تا زمانی که وابستگی‌هایشان آماده باشد اجرا می‌کند."""
        remaining = {task.id: task for task in tasks}
        results: list[str] = []

        while remaining:
            progress = False
            for task_id, task in list(remaining.items()):
                if any(
                    dependency in remaining
                    for dependency in task.depends_on
                ):
                    continue

                task.status = TaskStatus.RUNNING
                try:
                    task.result = self.loop.run([task])[0]
                    task.status = TaskStatus.SUCCESS
                    results.append(task.result)
                except Exception as error:
                    task.error = str(error)
                    task.status = TaskStatus.FAILED
                    raise

                del remaining[task_id]
                progress = True

            if not progress:
                for task in remaining.values():
                    task.status = TaskStatus.BLOCKED
                raise RuntimeError("وابستگی وظایف قابل حل نیست.")

        return results
