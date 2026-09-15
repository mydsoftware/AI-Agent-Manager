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
        """آخرین SHA commit ایجادشده توسط PUT contents را استخراج می‌کند."""
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

    def _run_engineering_loop(self, task: Task, command: dict) -> str:
        repository = command["repository"]
        branch = command.get("branch")
        base = command.get("base", "main")
        if not branch:
            raise ValueError("پارامتر branch برای چرخه مهندسی الزامی است.")

        expected_sha: str | None = None

        def create_branch():
            return self._github_action(task, "create_branch", repository=repository, branch=branch, base=base)

        def apply_change():
            nonlocal expected_sha
            results = []
            for change in changes:
                results.append(self._github_action(task, "put_file", repository=repository, **change))
            expected_sha = self._last_commit_sha(results)
            return json.dumps({"files_changed": len(results), "results": results}, ensure_ascii=False)

        def check_ci() -> str:
            """GitHub Actions پایان واقعی همان commit را صبر می‌کند.

            قبلاً اولین وضعیت `queued/in_progress` مستقیماً به EngineeringLoop
            برمی‌گشت و چرخه در حالت VERIFY متوقف می‌شد. اکنون تا timeout منتظر
            همان SHA می‌مانیم؛ در timeout وضعیت صریح `timeout` برمی‌گردد تا
            FailureAnalyzer/Repair بتوانند چرخه را ادامه دهند.
            """
            timeout = max(1, int(os.getenv("AI_AGENT_MANAGER_CI_TIMEOUT", "900")))
            interval = max(0.2, float(os.getenv("AI_AGENT_MANAGER_CI_POLL_INTERVAL", "2")))
            deadline = time.monotonic() + timeout

            while True:
                raw = self._github_action(
                    task,
                    "workflow_runs",
                    repository=repository,
                    branch=branch,
                    workflow=command.get("workflow"),
                )
                data = json.loads(raw)
                runs = data.get("workflow_runs", [])

                # Never accept an older successful run from the same branch.
                # The exact commit SHA is authoritative whenever GitHub provides it.
                matching = [run for run in runs if not expected_sha or run.get("head_sha") == expected_sha]
                if not matching:
                    # Test doubles and older adapters may omit head_sha; only use
                    # that compatibility path when every returned run omits it.
                    if runs and not any(run.get("head_sha") for run in runs):
                        matching = runs[:1]

                if matching:
                    latest = matching[0]
                    status = str(latest.get("conclusion") or latest.get("status") or "pending").lower()
                    if status in {"success", "passed", "pass", "failure", "failed", "cancelled", "timed_out", "action_required", "neutral", "skipped"}:
                        return status

                if time.monotonic() >= deadline:
                    return "timeout"
                time.sleep(interval)

        def repair(status: str):
            nonlocal expected_sha
            if not repair_changes:
                raise RuntimeError(f"CI شکست خورد ({status}) و تغییر اصلاحی تعریف نشده است.")
            results = []
            for change in repair_changes:
                results.append(self._github_action(task, "put_file", repository=repository, **change))
            expected_sha = self._last_commit_sha(results) or expected_sha
            return json.dumps({"repair_files": len(results), "results": results}, ensure_ascii=False)

        def create_pr():
            pr = command.get("pr", {})
            return self._github_action(task, "create_pr", repository=repository, head=branch, base=base, title=pr.get("title", f"تغییر خودکار: {task.title}"), body=pr.get("body", ""), draft=pr.get("draft", True))

        changes = command.get("changes") or []
        if not changes and command.get("change"):
            changes = [command["change"]]
        repair_changes = command.get("repair_changes") or []
        if not repair_changes and command.get("repair_change"):
            repair_changes = [command["repair_change"]]

        result = self.engineering_loop.run(create_branch, apply_change, check_ci, repair, create_pr)
        return json.dumps({"state": result.state.value, "attempts": result.attempts, "ci_status": result.ci_status, "error": result.error}, ensure_ascii=False)

    def _github_action(self, task: Task, action: str, **payload) -> str:
        payload["action"] = action
        return self.github.run(Task(id=f"{task.id}:{action}", title=f"عملیات GitHub: {action}", agent="github", description=json.dumps(payload, ensure_ascii=False)))
