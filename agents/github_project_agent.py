from __future__ import annotations

import json

from manager.engineering_loop import EngineeringLoop
from manager.task import Task
from .github_agent import GitHubAgent
from .base_agent import BaseAgent


class GitHubProjectAgent(BaseAgent):
    """ایجنت اجرای چرخه مدیریت پروژه روی GitHub."""

    name = "github-project"

    def __init__(self, github: GitHubAgent | None = None, engineering_loop: EngineeringLoop | None = None) -> None:
        self.github = github or GitHubAgent()
        self.engineering_loop = engineering_loop or EngineeringLoop()

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

        if operation == "engineering_loop":
            return self._run_engineering_loop(task, command)

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

    def _run_engineering_loop(self, task: Task, command: dict) -> str:
        """ماشین حالت مهندسی را به عملیات واقعی GitHub متصل می‌کند."""
        repository = command["repository"]
        branch = command.get("branch")
        base = command.get("base", "main")
        if not branch:
            raise ValueError("پارامتر branch برای چرخه مهندسی الزامی است.")

        def create_branch():
            return self._github_action(task, "create_branch", repository=repository, branch=branch, base=base)

        def apply_change():
            change = command.get("change")
            if not change:
                return None
            return self._github_action(task, "put_file", repository=repository, **change)

        def check_ci() -> str:
            raw = self._github_action(task, "workflow_runs", repository=repository, branch=branch, workflow=command.get("workflow"))
            data = json.loads(raw)
            runs = data.get("workflow_runs", [])
            if not runs:
                return "pending"
            latest = runs[0]
            return latest.get("conclusion") or latest.get("status") or "pending"

        def repair(status: str):
            repair_change = command.get("repair_change")
            if not repair_change:
                raise RuntimeError(f"CI شکست خورد ({status}) اما repair_change تعریف نشده است.")
            return self._github_action(task, "put_file", repository=repository, **repair_change)

        def create_pr():
            pr = command.get("pr", {})
            return self._github_action(task, "create_pr", repository=repository, head=branch, base=base, title=pr.get("title", f"تغییر خودکار: {task.title}"), body=pr.get("body", ""), draft=pr.get("draft", True))

        result = self.engineering_loop.run(create_branch, apply_change, check_ci, repair, create_pr)
        return json.dumps({"state": result.state.value, "attempts": result.attempts, "ci_status": result.ci_status, "error": result.error}, ensure_ascii=False)

    def _github_action(self, task: Task, action: str, **payload) -> str:
        payload["action"] = action
        return self.github.run(Task(
            id=f"{task.id}:{action}",
            title=f"عملیات GitHub: {action}",
            agent="github",
            description=json.dumps(payload, ensure_ascii=False),
        ))
