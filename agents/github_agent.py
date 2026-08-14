from __future__ import annotations

import json

from adapters.github_adapter import GitHubAPIClient, GitHubAdapter
from manager.task import Task
from .base_agent import BaseAgent


class GitHubAgent(BaseAgent):
    """ایجنت تخصصی اجرای عملیات واقعی روی GitHub."""

    name = "github"

    def __init__(self, adapter: GitHubAdapter | None = None) -> None:
        self.adapter = adapter or GitHubAdapter(GitHubAPIClient())

    def run(self, task: Task) -> str:
        """عملیات GitHub را از دستور ساختاریافته داخل توضیح وظیفه اجرا می‌کند."""
        try:
            command = json.loads(task.description)
        except json.JSONDecodeError as error:
            raise ValueError("توضیح وظیفه GitHub باید یک JSON معتبر باشد.") from error

        action = command.get("action")
        repository = command.get("repository")
        if not repository:
            raise ValueError("پارامتر repository برای عملیات GitHub الزامی است.")

        if action == "repository":
            result = self.adapter.repository(repository)
            return json.dumps(result, ensure_ascii=False)

        if action == "file":
            path = command.get("path")
            if not path:
                raise ValueError("پارامتر path برای خواندن فایل الزامی است.")
            result = self.adapter.file(repository, path, command.get("ref"))
            return json.dumps(result, ensure_ascii=False)

        if action == "put_file":
            path = command.get("path")
            content = command.get("content")
            branch = command.get("branch")
            message = command.get("message")
            if not all([path, content is not None, branch, message]):
                raise ValueError("پارامترهای path، content، branch و message الزامی هستند.")
            result = self.adapter.put_file(
                repository,
                path,
                content,
                message,
                branch,
                command.get("sha"),
            )
            return json.dumps(result, ensure_ascii=False)

        raise ValueError(f"عملیات GitHub پشتیبانی نمی‌شود: {action}")
