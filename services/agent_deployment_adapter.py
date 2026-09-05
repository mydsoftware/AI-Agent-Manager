"""Adapterهای امن برای اتصال Deployment Loop به Agent Executor و سرویس‌دهنده‌ها."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DeploymentContext:
    project_id: str
    branch: str
    commit_sha: str
    preview_url: str = ""


class AgentDeploymentAdapter:
    """قرارداد اجرایی؛ پیاده‌سازی واقعی می‌تواند از Executor موجود استفاده کند."""

    def __init__(self, executor: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> None:
        self.executor = executor

    def execute_fix(self, context: DeploymentContext, qa_result: dict[str, Any]) -> dict[str, Any]:
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
        return result.get("status") in {"fixed", "committed", "success"}
