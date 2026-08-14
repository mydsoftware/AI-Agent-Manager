from __future__ import annotations

import json

from manager.task import Task
from .github_agent import GitHubAgent
from .base_agent import BaseAgent


class GitHubProjectAgent(BaseAgent):
    """ایجنت اجرای چرخه مدیریت پروژه روی GitHub."""

    name = "github-project"

    def __init__(self, github: GitHubAgent | None = None) -> None:
        self.github = github or GitHubAgent()

    def run(self, task: Task) -> str:
        """دستورهای پروژه را به عملیات GitHub تبدیل می‌کند."""
        try:
            command = json.loads(task.description)
        except json.JSONDecodeError as error:
            raise ValueError("توضیح پروژه GitHub باید یک JSON معتبر باشد.") from error

        operation = command.get("operation")
        repository = command.get("repository")
        if not repository:
            raise ValueError("پارامتر repository الزامی است.")

        actions = {
            "inspect": {"action": "repository"},
            "read_file": {"action": "file", "path": command.get("path"), "ref": command.get("ref")},
            "write_file": {"action": "put_file", "path": command.get("path"), "content": command.get("content"), "message": command.get("message"), "branch": command.get("branch"), "sha": command.get("sha")},
            "create_branch": {"action": "create_branch", "branch": command.get("branch"), "base": command.get("base")},
            "create_pr": {"action": "create_pr", "head": command.get("head"), "base": command.get("base"), "title": command.get("title"), "body": command.get("body", ""), "draft": command.get("draft", True)},
            "workflow_status": {"action": "workflow_runs", "branch": command.get("branch"), "workflow": command.get("workflow")},
        }
        payload = actions.get(operation)
        if payload is None:
            raise ValueError(f"عملیات پروژه GitHub پشتیبانی نمی‌شود: {operation}")
        payload["repository"] = repository

        if operation == "read_file" and not payload["path"]:
            raise ValueError("پارامتر path الزامی است.")
        if operation == "write_file" and not all([payload["path"], payload["message"], payload["branch"]]):
            raise ValueError("پارامترهای path، message و branch الزامی هستند.")
        if operation == "create_branch" and not all([payload["branch"], payload["base"]]):
            raise ValueError("پارامترهای branch و base الزامی هستند.")
        if operation == "create_pr" and not all([payload["head"], payload["base"], payload["title"]]):
            raise ValueError("پارامترهای head، base و title الزامی هستند.")

        return self.github.run(Task(
            id=f"{task.id}:{operation}",
            title=f"عملیات GitHub: {operation}",
            agent="github",
            description=json.dumps(payload, ensure_ascii=False),
        ))
