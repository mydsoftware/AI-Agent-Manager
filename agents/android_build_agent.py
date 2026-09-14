from __future__ import annotations

import json
import time

from adapters.github_adapter import GitHubAPIClient, GitHubAdapter
from manager.task import Task
from .base_agent import BaseAgent


class AndroidBuildAgent(BaseAgent):
    """ایجنت بیلد اندروید با دو موتور اختصاصی پروژه و fallback خودکار."""

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
        timeout = int(command.get("timeout", self.timeout))
        if not repository:
            raise ValueError("repository برای بیلد اندروید الزامی است.")

        workflows = command.get("workflows") or ["android-build-automated.yml", "android-build.yml"]
        attempts: list[dict] = []

        for workflow in workflows:
            dispatch = {"accepted": False, "mode": "monitor"}
            try:
                dispatch = self.adapter.dispatch_workflow(repository, workflow, branch, command.get("inputs", {}))
            except Exception as error:
                # Workflowهای feature branch ممکن است از API dispatch قابل اجرا نباشند؛
                # در این حالت اجرای push-trigger شده را مانیتور می‌کنیم.
                dispatch = {"accepted": False, "mode": "monitor", "error": str(error)}

            run = self._wait_for_completion(repository, workflow, branch, timeout)
            attempts.append({"workflow": workflow, "dispatch": dispatch, "run": run})
            if run and run.get("status") == "completed" and run.get("conclusion") == "success":
                return json.dumps({"type": "android_build", "status": "success", "workflow": workflow, "attempts": attempts}, ensure_ascii=False)
            if run and run.get("status") == "completed":
                continue
            # اگر هیچ اجرای قابل مشاهده‌ای نیست، موتور بعدی را امتحان نکن تا وضعیت مبهم ایجاد نشود.
            break

        return json.dumps({"type": "android_build", "status": "failed", "attempts": attempts}, ensure_ascii=False)

    def _wait_for_completion(self, repository: str, workflow: str, branch: str, timeout: int) -> dict | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            runs = self.adapter.workflow_runs(repository, branch, workflow).get("workflow_runs", [])
            if runs:
                candidate = runs[0]
                if candidate.get("head_branch") == branch:
                    if candidate.get("status") == "completed":
                        return candidate
                    time.sleep(self.poll_interval)
                    continue
            time.sleep(self.poll_interval)
        return {"status": "timeout", "workflow": workflow, "branch": branch}
