from __future__ import annotations

import json
import os

from manager.business_growth import BusinessGrowthPipeline
from manager.task import Task
from manager.task_status import TaskStatus


class BusinessGrowthRuntime:
    """اجرای end-to-end چرخه رشد با context مشترک و engineering handoff."""

    def __init__(self, executor) -> None:
        self.executor = executor

    def run(self, request: str, target: str | None = None) -> list[dict]:
        max_cycles = max(1, int(os.getenv("BUSINESS_GROWTH_MAX_CYCLES", "1")))
        history: list[dict] = []
        context = request

        for cycle in range(1, max_cycles + 1):
            tasks = BusinessGrowthPipeline().build(context, target=target)
            for task in tasks:
                if history:
                    task.description += (
                        "\n\nContext چرخه/مرحله قبل:\n"
                        + history[-1]["result"]
                    )
                task.status = TaskStatus.PENDING
                result = self.executor.run([task])[0]

                if task.agent == "website-builder":
                    result = self._execute_engineering_plan(task, result)

                task.result = result
                task.status = TaskStatus.SUCCESS
                history.append({
                    "cycle": cycle,
                    "task_id": task.id,
                    "agent": task.agent,
                    "title": task.title,
                    "status": task.status.value,
                    "result": result,
                })

                context = result

            # چرخه بعدی با یافته‌های optimizer آغاز می‌شود؛ تعداد چرخه محدود و قابل تنظیم است.
            if cycle < max_cycles:
                context = history[-1]["result"]

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
        execution = self.executor.run([Task(
            id=f"{task.id}:engineering",
            title=f"ساخت سایت: {task.title}",
            description=json.dumps(command, ensure_ascii=False),
            agent="github-project",
        )])[0]
        data["engineering_execution"] = json.loads(execution) if isinstance(execution, str) else execution
        return json.dumps(data, ensure_ascii=False)
