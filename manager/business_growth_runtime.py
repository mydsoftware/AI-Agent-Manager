from __future__ import annotations

import json

from manager.business_growth import BusinessGrowthPipeline
from manager.task import Task
from manager.task_status import TaskStatus


class BusinessGrowthRuntime:
    """اجرای ترتیبی Pipeline رشد و انتقال خروجی هر مرحله به مرحله بعد."""

    def __init__(self, executor) -> None:
        self.executor = executor

    def run(self, request: str, target: str | None = None) -> list[dict]:
        tasks = BusinessGrowthPipeline().build(request, target=target)
        history: list[dict] = []
        previous_result = ""

        for task in tasks:
            if previous_result:
                task.description = (
                    f"{task.description}\n\n"
                    "خروجی مرحله قبلی را به‌عنوان context مصرف کن:\n"
                    f"{previous_result}"
                )

            task.status = TaskStatus.PENDING
            result = self.executor.run([task])[0]
            task.result = result
            task.status = TaskStatus.SUCCESS
            previous_result = result
            history.append(
                {
                    "task_id": task.id,
                    "agent": task.agent,
                    "title": task.title,
                    "status": task.status.value,
                    "result": result,
                }
            )

        return history
