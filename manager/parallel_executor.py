from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from manager.loop import AgenticLoop
from manager.task import Task
from manager.task_status import TaskStatus


class ParallelTaskExecutor:
    """وظایف مستقل را هم‌زمان و وظایف وابسته را مرحله‌ای اجرا می‌کند."""

    def __init__(self, loop: AgenticLoop, max_workers: int = 4) -> None:
        self.loop = loop
        self.max_workers = max_workers

    def run(self, tasks: list[Task]) -> list[str]:
        """گراف وظایف را تا تکمیل همه وظایف اجرا می‌کند."""
        pending = {task.id: task for task in tasks}
        results: list[str] = []

        while pending:
            ready = [
                task for task in pending.values()
                if all(
                    dependency not in pending
                    and next((t for t in tasks if t.id == dependency), None) is not None
                    and next(t for t in tasks if t.id == dependency).status == TaskStatus.SUCCESS
                    for dependency in task.depends_on
                )
            ]

            if not ready:
                for task in pending.values():
                    task.status = TaskStatus.BLOCKED
                raise RuntimeError("گراف وظایف قابل اجرا نیست یا یک وابستگی ناموفق است.")

            for task in ready:
                task.status = TaskStatus.RUNNING

            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(ready))) as pool:
                futures = {pool.submit(self.loop.run, [task]): task for task in ready}
                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        task.result = future.result()[0]
                        task.status = TaskStatus.SUCCESS
                        results.append(task.result)
                    except Exception as error:
                        task.error = str(error)
                        task.status = TaskStatus.FAILED
                        raise
                    finally:
                        pending.pop(task.id, None)

        return results
