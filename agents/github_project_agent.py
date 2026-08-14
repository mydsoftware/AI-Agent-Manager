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
        command = json.loads(task.description)
        operation = command.get("operation")

        if operation == "inspect":
            return self.github.run(Task(
                id=f"{task.id}:inspect",
                agent="github",
                description=json.dumps({
                    "action": "repository",
                    "repository": command["repository"],
                }, ensure_ascii=False),
            ))

        if operation == "read_file":
            return self.github.run(Task(
                id=f"{task.id}:read",
                agent="github",
                description=json.dumps({
                    "action": "file",
                    "repository": command["repository"],
                    "path": command["path"],
                    "ref": command.get("ref"),
                }, ensure_ascii=False),
            ))

        if operation == "write_file":
            return self.github.run(Task(
                id=f"{task.id}:write",
                agent="github",
                description=json.dumps({
                    "action": "put_file",
                    "repository": command["repository"],
                    "path": command["path"],
                    "content": command["content"],
                    "message": command["message"],
                    "branch": command["branch"],
                    "sha": command.get("sha"),
                }, ensure_ascii=False),
            ))

        raise ValueError(f"عملیات پروژه GitHub پشتیبانی نمی‌شود: {operation}")
