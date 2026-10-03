from __future__ import annotations

import json
import os

from manager.business_growth import BusinessGrowthPipeline
from manager.growth_action_planner import GrowthActionPlanner
from manager.growth_actions import GrowthActionRegistry
from manager.task import Task
from manager.task_status import TaskStatus


class BusinessGrowthRuntime:
    """اجرای end-to-end چرخه رشد با context تجمعی، action execution و engineering handoff امن."""

    def __init__(self, executor, action_registry: GrowthActionRegistry | None = None) -> None:
        self.executor = executor
        self.action_registry = action_registry or GrowthActionRegistry()
        self.action_planner = GrowthActionPlanner()
        self._executed_action_keys: set[str] = set()

    def run(self, request: str, target: str | None = None) -> list[dict]:
        max_cycles = max(1, int(os.getenv("BUSINESS_GROWTH_MAX_CYCLES", "1")))
        max_context_chars = max(4000, int(os.getenv("BUSINESS_GROWTH_MAX_CONTEXT_CHARS", "30000")))
        history: list[dict] = []
        context = request

        for cycle in range(1, max_cycles + 1):
            tasks = BusinessGrowthPipeline().build(context, target=target)
            for task in tasks:
                task.description = self._stage_context(request, target, history, max_context_chars)
                task.status = TaskStatus.PENDING
                result = self.executor.run([task])[0]

                if task.agent == "website-builder":
                    result = self._execute_engineering_plan(task, result)

                result = self._execute_planned_actions(task.agent, result)
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

            if cycle < max_cycles:
                context = history[-1]["result"]

        return history

    def _execute_planned_actions(self, phase: str, result: str) -> str:
        planned = self.action_planner.plan(result, phase)
        if not planned:
            return result

        executions = []
        for item in planned:
            if item.key in self._executed_action_keys:
                executions.append({
                    "status": "skipped",
                    "action": item.action.name,
                    "phase": item.action.phase,
                    "external_execution": False,
                    "data": {"reason": "duplicate_action", "idempotency_key": item.key},
                })
                continue

            execution = self.action_registry.execute(item.action)
            self._executed_action_keys.add(item.key)
            executions.append({
                **execution,
                "data": {
                    **execution.get("data", {}),
                    "idempotency_key": item.key,
                },
            })

        try:
            data = json.loads(result)
        except (TypeError, json.JSONDecodeError):
            data = {"raw_result": result}

        data["action_execution"] = executions
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def _stage_context(
        request: str,
        target: str | None,
        history: list[dict],
        max_chars: int,
    ) -> str:
        header = request
        if target:
            header = f"کسب‌وکار هدف: {target}\nدرخواست اصلی: {request}"

        if not history:
            return header

        previous = "\n\n".join(
            f"مرحله {item['agent']}:\n{item['result']}"
            for item in history[-6:]
        )
        context = (
            f"{header}\n\n"
            "خروجی مرحله قبلی و context تجمعی:\n"
            f"{previous}"
        )
        return context[-max_chars:]

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

        try:
            execution = self.executor.run([Task(
                id=f"{task.id}:engineering",
                title=f"ساخت سایت: {task.title}",
                description=json.dumps(command, ensure_ascii=False),
                agent="github-project",
            )])[0]
            data["engineering_execution"] = (
                json.loads(execution) if isinstance(execution, str) else execution
            )
        except Exception as error:
            if os.getenv("BUSINESS_GROWTH_STRICT_ENGINEERING", "0").lower() in {"1", "true", "yes"}:
                raise
            data["engineering_execution"] = {
                "state": "blocked",
                "external_execution": False,
                "reason": str(error),
                "next_action": (
                    "repository target را ایجاد/متصل کنید یا "
                    "BUSINESS_GROWTH_REPOSITORY را به یک repository موجود تغییر دهید."
                ),
            }

        return json.dumps(data, ensure_ascii=False)
