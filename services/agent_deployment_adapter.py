"""Adapterهای امن برای اتصال Deployment Loop به Task Executor واقعی."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from manager.executor import TaskExecutor
from manager.task import Task


@dataclass(frozen=True)
class DeploymentContext:
    project_id: str
    branch: str
    commit_sha: str
    preview_url: str = ""


class AgentDeploymentAdapter:
    """پل بین حلقه استقرار و Executor واقعی پروژه.

    Adapter عمداً فقط یک Task را به Executor می‌دهد؛ خودش هیچ Token یا
    عملیات مستقیم GitHub/Vercel انجام نمی‌دهد.
    """

    def __init__(self, executor: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> None:
        self.executor = executor

    @classmethod
    def from_task_executor(cls, task_executor: TaskExecutor) -> "AgentDeploymentAdapter":
        """یک Adapter متصل به TaskExecutor واقعی Runtime می‌سازد."""
        return cls(executor=cls._build_executor(task_executor))

    @staticmethod
    def _build_executor(task_executor: TaskExecutor) -> Callable[[dict[str, Any]], dict[str, Any]]:
        def execute(request: dict[str, Any]) -> dict[str, Any]:
            task = Task(
                title="رفع خطای Browser QA",
                description=(
                    "نتیجه Browser QA را بررسی کن، مشکل را در Branch پروژه رفع کن "
                    "و در صورت مجاز بودن تغییرات را برای Commit آماده کن."
                ),
                agent="developer",
                metadata={
                    "deployment_action": request.get("action"),
                    "project_id": request.get("project_id"),
                    "branch": request.get("branch"),
                    "commit_sha": request.get("commit_sha"),
                    "preview_url": request.get("preview_url"),
                    "qa": request.get("qa", {}),
                },
                max_attempts=3,
            )

            try:
                results = task_executor.run([task])
            except Exception as error:
                return {
                    "status": "failed",
                    "project_id": request.get("project_id"),
                    "task_id": task.id,
                    "error": str(error),
                }

            if task.status.value == "success":
                return {
                    "status": "success",
                    "project_id": request.get("project_id"),
                    "task_id": task.id,
                    "result": task.result or (results[0] if results else ""),
                }

            return {
                "status": "failed",
                "project_id": request.get("project_id"),
                "task_id": task.id,
                "error": task.error or "Task با موفقیت اجرا نشد.",
            }

        return execute

    def execute_fix(self, context: DeploymentContext, qa_result: dict[str, Any]) -> dict[str, Any]:
        """نتیجه QA را به Executor می‌دهد، بدون عبور دادن اطلاعات محرمانه."""
        if self.executor is None:
            return {"status": "not_configured", "project_id": context.project_id}

        request = {
            "action": "fix_browser_qa_failure",
            "project_id": context.project_id,
            "branch": context.branch,
            "commit_sha": context.commit_sha,
            "preview_url": context.preview_url,
            "qa": qa_result,
        }
        return self.executor(request)

    @staticmethod
    def can_retry(result: dict[str, Any]) -> bool:
        """فقط نتیجه موفق Executor اجازه ورود دوباره به Loop را می‌دهد."""
        return result.get("status") in {"fixed", "committed", "success"}
