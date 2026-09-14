from __future__ import annotations

import json
import time

from adapters.github_adapter import GitHubAPIClient, GitHubAdapter
from manager.task import Task
from .base_agent import BaseAgent


class AndroidBuildAgent(BaseAgent):
    """ایجنت بیلد اندروید؛ از دو مسیر Gradle و Build Android App استفاده می‌کند."""

    name = "android-build"

    def __init__(self, adapter: GitHubAdapter | None = None, poll_interval: int = 8, timeout: int = 900) -> None:
        self.adapter = adapter or GitHubAdapter(GitHubAPIClient())
        self.poll_interval = poll_interval
        self.timeout = timeout

    def run(self, task: Task) -> str:
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("وظیفه android-build باید JSON معتبر باشد.") from error

        repository = command.get("repository")
        branch = command.get("branch", "feature/manager-core")
        workflow = command.get("workflow", "android-build-automated.yml")
        if not repository:
            raise ValueError("repository برای بیلد اندروید الزامی است.")

        dispatch = self.adapter.dispatch_workflow(repository, workflow, branch, command.get("inputs", {}))
        if not dispatch.get("accepted", False):
            raise RuntimeError("GitHub نتوانست Workflow بیلد اندروید را اجرا کند.")

        deadline = time.monotonic() + int(command.get("timeout", self.timeout))
        run = None
        while time.monotonic() < deadline:
            runs = self.adapter.workflow_runs(repository, branch, workflow).get("workflow_runs", [])
            if runs:
                candidate = runs[0]
                if candidate.get("head_branch") == branch and candidate.get("status") in {"queued", "in_progress", "completed"}:
                    run = candidate
                    if candidate.get("status") == "completed":
                        return json.dumps({"type": "android_build", "workflow": workflow, "run": candidate}, ensure_ascii=False)
            time.sleep(self.poll_interval)

        return json.dumps({"type": "android_build", "workflow": workflow, "status": "timeout", "run": run, "dispatch": dispatch}, ensure_ascii=False)
