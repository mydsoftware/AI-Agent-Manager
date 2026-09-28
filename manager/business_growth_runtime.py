from __future__ import annotations

import json

from manager.business_growth import BusinessGrowthPipeline
from manager.task import Task
from manager.task_status import TaskStatus


class BusinessGrowthRuntime:
    """اجرای Pipeline رشد با عبور context و اجرای planهای مهندسی."""

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

            # Website Builder یک engineering_plan تولید می‌کند؛ آن را همان‌جا اجرا می‌کنیم.
            if task.agent == "website-builder":
                result = self._execute_engineering_plan(task, result)
                task.result = result

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

    def _execute_engineering_plan(self, task: Task, result: str) -> str:
        try:
            data = json.loads(result)
        except (TypeError, json.JSONDecodeError):
            return result

        plan = data.get("engineering_plan")
        if not isinstance(plan, dict) or not plan.get("changes"):
            return result

        command = {
            "operation": "engineering_loop",
            "repository": plan["repository"],
            "base": plan.get("base", "main"),
            "branch": plan["branch"],
            "workflow": plan.get("workflow"),
            "changes": plan["changes"],
            "repair_changes": plan.get("repair_changes", []),
            "pr": plan.get("pr", {}),
        }
        engineering_task = Task(
            id=f"{task.id}:engineering",
            title=f"ساخت سایت: {task.title}",
            description=json.dumps(command, ensure_ascii=False),
            agent="github-project",
        )
        execution = self.executor.run([engineering_task])[0]
        data["engineering_execution"] = json.loads(execution) if isinstance(execution, str) else execution
        return json.dumps(data, ensure_ascii=False)
