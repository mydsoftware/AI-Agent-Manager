from __future__ import annotations

import json
import os
import time

from manager.engineering_loop import EngineeringLoop
from manager.task import Task
from .github_agent import GitHubAgent
from .base_agent import BaseAgent


class GitHubProjectAgent(BaseAgent):
    """ایجنت اجرای چرخه کامل توسعه روی GitHub."""

    name = "github-project"

    def __init__(self, github: GitHubAgent | None = None, engineering_loop: EngineeringLoop | None = None) -> None:
        self.github = github or GitHubAgent()
        self.engineering_loop = engineering_loop or EngineeringLoop()

    def run(self, task: Task) -> str:
        try:
            command = json.loads(task.description)
        except json.JSONDecodeError as error:
            raise ValueError("توضیح پروژه GitHub باید JSON معتبر باشد.") from error

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
        return self.github.run(Task(id=f"{task.id}:{operation}", title=f"عملیات GitHub: {operation}", agent="github", description=json.dumps(payload, ensure_ascii=False)))

    @staticmethod
    def _last_commit_sha(results: list[object]) -> str | None:
        for result in reversed(results):
            try:
                data = json.loads(result) if isinstance(result, str) else result
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                commit = data.get("commit")
                if isinstance(commit, dict) and commit.get("sha"):
                    return str(commit["sha"])
        return None

    def _github_command(self, task: Task, action: str, repository: str, **payload) -> dict:
        payload.update({"action": action, "repository": repository})
        raw = self.github.run(Task(id=f"{task.id}:{action}", title=f"عملیات GitHub: {action}", agent="github", description=json.dumps(payload, ensure_ascii=False)))
        return json.loads(raw)

    def _run_engineering_loop(self, task: Task, command: dict) -> str:
        repository = command["repository"]
        branch = command.get("branch")
        base = command.get("base", "main")
        if not branch:
            raise ValueError("پارامتر branch برای چرخه مهندسی الزامی است.")

        expected_sha: str | None = None

        def create_branch():
            return self._github_command(task, "create_branch", repository, branch=branch, base=base)

        def apply_change():
            nonlocal expected_sha
            results = [self._github_command(task, "put_file", repository, **change) for change in changes]
            expected_sha = self._last_commit_sha(results)
            return json.dumps({"files_changed": len(results), "results": results}, ensure_ascii=False)

        def check_ci() -> str:
            timeout = max(1, int(os.getenv("AI_AGENT_MANAGER_CI_TIMEOUT", "900")))
            interval = max(0.2, float(os.getenv("AI_AGENT_MANAGER_CI_POLL_INTERVAL", "2")))
            deadline = time.monotonic() + timeout
            while True:
                data = self._github_command(task, "workflow_runs", repository, branch=branch, workflow=command.get("workflow"))
                runs = data.get("workflow_runs", [])
                matching = [run for run in runs if not expected_sha or run.get("head_sha") == expected_sha]
                if not matching and runs and not any(run.get("head_sha") for run in runs):
                    matching = runs[:1]
                if matching:
                    latest = matching[0]
                    status = str(latest.get("conclusion") or latest.get("status") or "pending").lower()
                    if status in {"success", "passed", "pass", "failure", "failed", "cancelled", "timed_out", "action_required", "neutral", "skipped"}:
                        return status
                if time.monotonic() >= deadline:
                    return "timeout"
                time.sleep(interval)

        def get_ci_log() -> str:
            data = self._github_command(task, "workflow_log", repository, branch=branch, head_sha=expected_sha, workflow=command.get("workflow"))
            return str(data.get("logs") or data.get("message") or data)

        def get_diff() -> str:
            data = self._github_command(task, "compare", repository, base=base, head=branch)
            chunks = [f"diff -- {item.get('filename', '')}\n{item.get('patch') or ''}" for item in data.get("files", [])]
            return "\n\n".join(chunks) or str(data.get("message") or data.get("status") or "")

        def review_change(diff: object):
            return self.engineering_loop.code_review_agent.review(str(diff or ""), tests_passed=True)

        def security_scan(diff: str, dependency_report: str | None):
            return self.engineering_loop.security_agent.scan(diff, dependency_report)

        changes = command.get("changes") or []
        if not changes and command.get("change"):
            changes = [command["change"]]
        repair_changes = command.get("repair_changes") or []
        if not repair_changes and command.get("repair_change"):
            repair_changes = [command["repair_change"]]

        def repair(plan, analysis):
            if not repair_changes:
                raise RuntimeError("CI شکست خورد و تغییر اصلاحی از Developer Plan دریافت نشده است.")
            results = [self._github_command(task, "put_file", repository, **change) for change in repair_changes]
            nonlocal expected_sha
            expected_sha = self._last_commit_sha(results) or expected_sha
            return json.dumps({"repair_files": len(results), "results": results}, ensure_ascii=False)

        def create_pr():
            pr = command.get("pr", {})
            return self._github_command(task, "create_pr", repository, head=branch, base=base, title=pr.get("title", f"تغییر خودکار: {task.title}"), body=pr.get("body", ""), draft=pr.get("draft", True))

        result = self.engineering_loop.run(
            create_branch,
            apply_change,
            check_ci,
            repair,
            create_pr,
            get_ci_log=get_ci_log,
            get_diff=get_diff,
            review_change=review_change,
            security_scan=security_scan,
        )
        return json.dumps({"state": result.state.value, "attempts": result.attempts, "ci_status": result.ci_status, "error": result.error}, ensure_ascii=False)

    def _github_action(self, task: Task, action: str, **payload) -> str:
        payload["action"] = action
        return self.github.run(Task(id=f"{task.id}:{action}", title=f"عملیات GitHub: {action}", agent="github", description=json.dumps(payload, ensure_ascii=False)))
