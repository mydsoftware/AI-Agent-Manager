"""ابزار GitHub."""

from __future__ import annotations

import json
from typing import Any

from adapters.github_adapter import GitHubAPIClient, GitHubAdapter
from .base import Tool, ToolPermission, ToolResult


class GitHubTool(Tool):
    """ابزار عملیات GitHub با استفاده از Adapter."""

    name = "github"
    description = "عملیات GitHub: خواندن/نوشتن فایل، ایجاد Branch/PR، بررسی CI"
    permissions = [ToolPermission.GITHUB]
    timeout = 30.0

    def __init__(self, adapter: GitHubAdapter | None = None) -> None:
        self.adapter = adapter or GitHubAdapter(GitHubAPIClient())

    def validate(self, **kwargs: Any) -> bool:
        action = kwargs.get("action", "")
        repository = kwargs.get("repository", "")
        return bool(action and repository)

    def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action", "")
        repository = kwargs.get("repository", "")

        try:
            if action == "file":
                result = self.adapter.file(repository, kwargs["path"], kwargs.get("ref"))
            elif action == "put_file":
                result = self.adapter.put_file(
                    repository, kwargs["path"], kwargs["content"],
                    kwargs["message"], kwargs["branch"], kwargs.get("sha"),
                )
            elif action == "create_branch":
                result = self.adapter.create_branch(repository, kwargs["branch"], kwargs["base"])
            elif action == "create_pr":
                result = self.adapter.create_pull_request(
                    repository, kwargs["head"], kwargs["base"],
                    kwargs["title"], kwargs.get("body", ""), kwargs.get("draft", True),
                )
            elif action == "workflow_runs":
                result = self.adapter.workflow_runs(repository, kwargs.get("branch"), kwargs.get("workflow"))
            elif action == "repository":
                result = self.adapter.repository(repository)
            else:
                return ToolResult(False, error=f"عملیات GitHub «{action}» پشتیبانی نمی‌شود.")

            return ToolResult(
                success=True,
                output=json.dumps(result, ensure_ascii=False),
                metadata={"action": action, "repository": repository},
            )
        except Exception as exc:
            return ToolResult(False, error=f"خطا در عملیات GitHub: {exc}")
