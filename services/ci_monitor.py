"""مانیتور امن GitHub Actions برای چرخه خودکار رفع خطا."""

from __future__ import annotations

from typing import Any

from services.github_integration import GitHubIntegration


class CIMonitor:
    """وضعیت CI را می‌خواند و فقط اطلاعات لازم برای Agent را برمی‌گرداند."""

    def __init__(self, github: GitHubIntegration) -> None:
        self.github = github

    def latest(self, owner: str, repository: str, branch: str) -> dict[str, Any]:
        runs = self.github.workflow_runs(owner, repository, branch, limit=10).get("workflow_runs", [])
        if not runs:
            return {"status": "not_found", "branch": branch}
        run = runs[0]
        conclusion = run.get("conclusion")
        if conclusion == "success":
            return {"status": "passed", "run_id": run.get("id"), "head_sha": run.get("head_sha", "")}
        if conclusion == "failure":
            return {"status": "failed", "failure": self.github.ci_failure_context(owner, repository, int(run["id"]))}
        return {"status": "pending", "run_id": run.get("id"), "workflow_status": run.get("status", "")}
