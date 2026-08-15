from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from manager.context import AgentContext
from manager.loop import AgenticLoop
from manager.task import Task


class ParallelAgentOrchestrator:
    """اجرای موازی Taskهای مستقل و حفظ ترتیب منطقی وابستگی‌ها."""

    def __init__(self, loop: AgenticLoop, context: AgentContext | None = None, max_workers: int = 4) -> None:
        self.loop = loop
        self.context = context or AgentContext()
        self.max_workers = max(1, max_workers)

    def run(self, tasks: list[Task]) -> list[str]:
        pending = {task.id: task for task in tasks}
        results: list[str] = []

        while pending:
            ready = [
                task for task in pending.values()
                if all(dependency not in pending for dependency in task.depends_on)
            ]
            if not ready:
                raise RuntimeError("زنجیره وظایف متوقف شد؛ وابستگی قابل حل نیست.")

            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(ready))) as pool:
                futures = {pool.submit(self.loop.run, [task]): task for task in ready}
                completed = []
                for future in as_completed(futures):
                    task = futures[future]
                    result = future.result()[0]
                    task.result = result
                    self.context.set(task.id, result)
                    completed.append((task.id, result))

            for task_id, result in sorted(completed):
                results.append(result)
                del pending[task_id]

        return results
