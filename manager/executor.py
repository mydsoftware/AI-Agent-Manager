from __future__ import annotations

from manager.loop import AgenticLoop
from manager.task import Task
from manager.task_status import TaskStatus


class TaskExecutor:
    """وظایف را با رعایت وابستگی‌ها و تلاش مجدد اجرا می‌کند."""

    def __init__(self, loop: AgenticLoop) -> None:
        self.loop = loop

    def run(self, tasks: list[Task]) -> list[str]:
        """Task Graph را تا تکمیل، شکست یا انسداد اجرا می‌کند."""
        remaining = {task.id: task for task in tasks}
        known = dict(remaining)
        results: list[str] = []
        if len(known) != len(tasks):
            raise ValueError("شناسه Taskها باید یکتا باشند.")

        while remaining:
            progress = False
            for task_id, task in list(remaining.items()):
                missing = [dep for dep in task.depends_on if dep not in known]
                if missing:
                    task.status = TaskStatus.BLOCKED
                    task.error = f"وابستگی‌های ناشناخته: {', '.join(missing)}"
                    del remaining[task_id]
                    progress = True
                    continue
                dependencies = [known[dep] for dep in task.depends_on]
                if any(dep.status in {TaskStatus.FAILED, TaskStatus.BLOCKED} for dep in dependencies):
                    task.status = TaskStatus.BLOCKED
                    task.error = "یکی از وابستگی‌های این وظیفه با شکست یا انسداد مواجه شده است."
                    del remaining[task_id]
                    progress = True
                    continue
                if any(dep.status != TaskStatus.SUCCESS for dep in dependencies):
                    continue

                attempts = 0
                while attempts <= task.max_attempts:
                    attempts += 1
                    task.attempts = attempts
                    task.start()
                    try:
                        result = self.loop.run([task])[0]
                        task.complete(result)
                        results.append(result)
                        break
                    except Exception as error:
                        task.error = str(error)
                        if attempts <= task.max_attempts:
                            task.status = TaskStatus.RETRYING
                            continue
                        task.fail(str(error))
                del remaining[task_id]
                progress = True

            if not progress:
                for task in remaining.values():
                    task.status = TaskStatus.BLOCKED
                    task.error = "چرخه یا وابستگی حل‌نشده در نمودار وظایف وجود دارد."
                raise RuntimeError("وابستگی وظایف قابل حل نیست.")
        return results
