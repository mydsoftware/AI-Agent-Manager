from __future__ import annotations

from manager.task import Task


class DependencyGraph:
    """اعتبارسنجی و مرتب‌سازی وابستگی‌های Task."""

    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = {task.id: task for task in tasks}
        self._validate()

    def _validate(self) -> None:
        for task in self.tasks.values():
            missing = [d for d in task.depends_on if d not in self.tasks]
            if missing:
                raise ValueError(f"وابستگی‌های تعریف‌نشده برای {task.id}: {', '.join(missing)}")
        self._check_cycles()

    def _check_cycles(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError("چرخه در وابستگی Taskها شناسایی شد")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in self.tasks[task_id].depends_on:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in self.tasks:
            visit(task_id)

    def ready(self, pending: set[str]) -> list[Task]:
        return [
            task for task_id, task in self.tasks.items()
            if task_id in pending and all(dep not in pending for dep in task.depends_on)
        ]
