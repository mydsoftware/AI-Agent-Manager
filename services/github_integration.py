"""لایه یکپارچه GitHub برای پروژه‌های هسته مرکزی هوش مصنوعی."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class GitHubConfig:
    token: str
    api_base_url: str = "https://api.github.com"

    @classmethod
    def from_env(cls) -> "GitHubConfig":
        return cls(token=os.getenv("GITHUB_TOKEN", "").strip())

    @property
    def configured(self) -> bool:
        return bool(self.token)


class GitHubIntegration:
    """Facade امن برای عملیات GitHub؛ Secret هرگز در خروجی قرار نمی‌گیرد."""

    def __init__(self, config: GitHubConfig | None = None) -> None:
        self.config = config or GitHubConfig.from_env()

    def status(self) -> dict[str, Any]:
        return {"configured": self.config.configured, "provider": "github", "api_base_url": self.config.api_base_url}

    def build_headers(self) -> dict[str, str]:
        if not self.config.configured:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")
        return {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.config.token}", "X-GitHub-Api-Version": "2022-11-28"}

    def repository_url(self, owner: str, repository: str) -> str:
        owner, repository = owner.strip(), repository.strip()
        if not owner or not repository:
            raise ValueError("owner و repository الزامی هستند.")
        if any(part in {".", ".."} or "/" in part or "\\" in part for part in (owner, repository)):
            raise ValueError("شناسه Repository نامعتبر است.")
        return f"{self.config.api_base_url}/repos/{owner}/{repository}"

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not path.startswith("/") or ".." in path:
            raise ValueError("مسیر GitHub نامعتبر است.")
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(self.config.api_base_url + path, data=body, method=method.upper(), headers={**self.build_headers(), "Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=20) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"GitHub API خطا داد ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError("ارتباط با GitHub برقرار نشد.") from error

    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        return self.request("GET", f"/repos/{owner.strip()}/{repository.strip()}")

    def create_branch(self, owner: str, repository: str, branch: str, source_sha: str) -> dict[str, Any]:
        branch, source_sha = branch.strip(), source_sha.strip()
        if not branch or not source_sha:
            raise ValueError("branch و source_sha الزامی هستند.")
        return self.request("POST", f"/repos/{owner.strip()}/{repository.strip()}/git/refs", {"ref": f"refs/heads/{branch}", "sha": source_sha})

    def create_issue(self, owner: str, repository: str, title: str, body: str = "") -> dict[str, Any]:
        if not title.strip():
            raise ValueError("title الزامی است.")
        return self.request("POST", f"/repos/{owner.strip()}/{repository.strip()}/issues", {"title": title.strip(), "body": body})

    def workflow_runs(self, owner: str, repository: str, branch: str | None = None, limit: int = 10) -> dict[str, Any]:
        """آخرین اجراهای GitHub Actions را برای Branch می‌خواند."""
        owner, repository = owner.strip(), repository.strip()
        if not owner or not repository:
            raise ValueError("owner و repository الزامی هستند.")
        limit = max(1, min(int(limit), 100))
        query = f"?per_page={limit}"
        if branch and branch.strip():
            query += f"&branch={branch.strip()}"
        return self.request("GET", f"/repos/{owner}/{repository}/actions/runs{query}")

    def workflow_run(self, owner: str, repository: str, run_id: int) -> dict[str, Any]:
        if int(run_id) < 1:
            raise ValueError("run_id نامعتبر است.")
        return self.request("GET", f"/repos/{owner.strip()}/{repository.strip()}/actions/runs/{int(run_id)}")

    def workflow_jobs(self, owner: str, repository: str, run_id: int) -> dict[str, Any]:
        if int(run_id) < 1:
            raise ValueError("run_id نامعتبر است.")
        return self.request("GET", f"/repos/{owner.strip()}/{repository.strip()}/actions/runs/{int(run_id)}/jobs")

    def workflow_job_logs(self, owner: str, repository: str, job_id: int) -> str:
        if int(job_id) < 1:
            raise ValueError("job_id نامعتبر است.")
        path = f"/repos/{owner.strip()}/{repository.strip()}/actions/jobs/{int(job_id)}/logs"
        if not self.config.configured:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")
        req = Request(self.config.api_base_url + path, method="GET", headers=self.build_headers())
        try:
            with urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")[-20000:]
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"GitHub API خطا داد ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError("ارتباط با GitHub برقرار نشد.") from error

    def ci_failure_context(self, owner: str, repository: str, run_id: int) -> dict[str, Any]:
        """اطلاعات محدود و مناسب برای تحویل خطای CI به Agent را می‌سازد."""
        run = self.workflow_run(owner, repository, run_id)
        jobs = self.workflow_jobs(owner, repository, run_id)
        failed_jobs = [
            job for job in jobs.get("jobs", [])
            if job.get("conclusion") == "failure"
        ]
        logs = []
        for job in failed_jobs[:5]:
            logs.append({
                "job_id": job.get("id"),
                "name": job.get("name", ""),
                "conclusion": job.get("conclusion"),
                "log": self.workflow_job_logs(owner, repository, int(job["id"])),
            })
        return {
            "run_id": run.get("id"),
            "workflow": run.get("name", ""),
            "status": run.get("status", ""),
            "conclusion": run.get("conclusion", ""),
            "head_sha": run.get("head_sha", ""),
            "head_branch": run.get("head_branch", ""),
            "failed_jobs": logs,
        }
