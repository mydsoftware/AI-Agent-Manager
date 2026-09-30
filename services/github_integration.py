"""لایه یکپارچه GitHub برای پروژه‌های هسته مرکزی هوش مصنوعی."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class GitHubConfig:
    """تنظیمات اتصال به GitHub را نگه می‌دارد."""

    token: str
    api_base_url: str = "https://api.github.com"

    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """تنظیمات را از متغیرهای محیطی می‌خواند."""
        return cls(token=os.getenv("GITHUB_TOKEN", "").strip())

    @property
    def configured(self) -> bool:
        """مشخص می‌کند Token در دسترس است یا خیر."""
        return bool(self.token)


class GitHubIntegration:
    """Facade امن برای عملیات GitHub؛ Secret هرگز در خروجی قرار نمی‌گیرد."""

    MAX_AGENT_LOG_CHARS = 4000
    _SECRET_PATTERNS = (
        re.compile(r"(?i)(authorization\s*:\s*)[^\r\n]+"),
        re.compile(r"(?i)(\b(?:token|password|passwd|secret|api[_-]?key)\s*[=:]\s*)[^\s,;]+"),
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]+\b"),
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]+\b"),
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    )

    def __init__(self, config: GitHubConfig | None = None) -> None:
        """Facade را با تنظیمات داده‌شده یا Environment می‌سازد."""
        self.config = config or GitHubConfig.from_env()

    def status(self) -> dict[str, Any]:
        """وضعیت پیکربندی اتصال را بدون افشای Token برمی‌گرداند."""
        return {"configured": self.config.configured, "provider": "github", "api_base_url": self.config.api_base_url}

    def build_headers(self) -> dict[str, str]:
        """Headerهای احراز هویت GitHub را می‌سازد."""
        if not self.config.configured:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")
        return {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.config.token}", "X-GitHub-Api-Version": "2022-11-28"}

    def repository_url(self, owner: str, repository: str) -> str:
        """URL امن Repository را می‌سازد."""
        owner, repository = owner.strip(), repository.strip()
        if not owner or not repository:
            raise ValueError("owner و repository الزامی هستند.")
        if any(part in {".", ".."} or "/" in part or "\\" in part for part in (owner, repository)):
            raise ValueError("شناسه Repository نامعتبر است.")
        return f"{self.config.api_base_url}/repos/{owner}/{repository}"

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """یک درخواست GitHub را با خطای محدود و بدون Secret اجرا می‌کند."""
        if not path.startswith("/") or ".." in path:
            raise ValueError("مسیر GitHub نامعتبر است.")
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(self.config.api_base_url + path, data=body, method=method.upper(), headers={**self.build_headers(), "Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=20) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as error:
            detail = self._sanitize_log(error.read().decode("utf-8", errors="replace"), 500)
            raise RuntimeError(f"GitHub API خطا داد ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError("ارتباط با GitHub برقرار نشد.") from error

    @classmethod
    def _sanitize_log(cls, text: str, limit: int | None = None) -> str:
        """Secretهای متداول را حذف و Diagnostic را به طول محدود تبدیل می‌کند."""
        sanitized = text
        for pattern in cls._SECRET_PATTERNS:
            sanitized = pattern.sub(lambda match: (match.group(1) + "[REDACTED]") if match.lastindex else "[REDACTED]", sanitized)
        max_chars = limit or cls.MAX_AGENT_LOG_CHARS
        return sanitized[-max_chars:]

    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        """اطلاعات Repository را می‌خواند."""
        return self.request("GET", f"/repos/{owner.strip()}/{repository.strip()}")

    def create_branch(self, owner: str, repository: str, branch: str, source_sha: str) -> dict[str, Any]:
        """یک Branch جدید از SHA مشخص ایجاد می‌کند."""
        branch, source_sha = branch.strip(), source_sha.strip()
        if not branch or not source_sha:
            raise ValueError("branch و source_sha الزامی هستند.")
        return self.request("POST", f"/repos/{owner.strip()}/{repository.strip()}/git/refs", {"ref": f"refs/heads/{branch}", "sha": source_sha})

    def create_issue(self, owner: str, repository: str, title: str, body: str = "") -> dict[str, Any]:
        """Issue جدید را ایجاد می‌کند."""
        if not title.strip():
            raise ValueError("title الزامی است.")
        return self.request("POST", f"/repos/{owner.strip()}/{repository.strip()}/issues", {"title": title.strip(), "body": body})

    def workflow_runs(self, owner: str, repository: str, branch: str | None = None, limit: int = 10) -> dict[str, Any]:
        """آخرین اجراهای GitHub Actions را برای Branch می‌خواند."""
        owner, repository = owner.strip(), repository.strip()
        if not owner or not repository:
            raise ValueError("owner و repository الزامی هستند.")
        limit = max(1, min(int(limit), 100))
        params: dict[str, str | int] = {"per_page": limit}
        if branch and branch.strip():
            params["branch"] = branch.strip()
        query = "?" + urlencode(params)
        return self.request("GET", f"/repos/{owner}/{repository}/actions/runs{query}")

    def workflow_run(self, owner: str, repository: str, run_id: int) -> dict[str, Any]:
        """اطلاعات یک Workflow Run را می‌خواند."""
        if int(run_id) < 1:
            raise ValueError("run_id نامعتبر است.")
        return self.request("GET", f"/repos/{owner.strip()}/{repository.strip()}/actions/runs/{int(run_id)}")

    def workflow_jobs(self, owner: str, repository: str, run_id: int) -> dict[str, Any]:
        """Jobهای یک Workflow Run را می‌خواند."""
        if int(run_id) < 1:
            raise ValueError("run_id نامعتبر است.")
        return self.request("GET", f"/repos/{owner.strip()}/{repository.strip()}/actions/runs/{int(run_id)}/jobs")

    def workflow_job_logs(self, owner: str, repository: str, job_id: int) -> str:
        """فقط یک excerpt محدود و sanitized از لاگ Job برمی‌گرداند."""
        if int(job_id) < 1:
            raise ValueError("job_id نامعتبر است.")
        path = f"/repos/{owner.strip()}/{repository.strip()}/actions/jobs/{int(job_id)}/logs"
        if not self.config.configured:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")
        req = Request(self.config.api_base_url + path, method="GET", headers=self.build_headers())
        try:
            with urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return self._sanitize_log(raw)
        except HTTPError as error:
            detail = self._sanitize_log(error.read().decode("utf-8", errors="replace"), 500)
            raise RuntimeError(f"GitHub API خطا داد ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError("ارتباط با GitHub برقرار نشد.") from error

    def ci_failure_context(self, owner: str, repository: str, run_id: int) -> dict[str, Any]:
        """اطلاعات محدود و sanitized مناسب برای تحویل خطای CI به Agent را می‌سازد."""
        run = self.workflow_run(owner, repository, run_id)
        jobs = self.workflow_jobs(owner, repository, run_id)
        failed_jobs = [job for job in jobs.get("jobs", []) if job.get("conclusion") == "failure"]
        diagnostics = []
        for job in failed_jobs[:5]:
            job_id = job.get("id")
            diagnostic = {
                "job_id": job_id,
                "name": str(job.get("name", ""))[:200],
                "conclusion": job.get("conclusion"),
            }
            if isinstance(job_id, int) and job_id > 0:
                try:
                    diagnostic["log_excerpt"] = self.workflow_job_logs(owner, repository, job_id)
                except (RuntimeError, ValueError):
                    diagnostic["log_excerpt"] = "[LOG_UNAVAILABLE]"
            else:
                diagnostic["log_excerpt"] = "[LOG_UNAVAILABLE]"
            diagnostics.append(diagnostic)
        return {
            "run_id": run.get("id"),
            "workflow": str(run.get("name", ""))[:200],
            "status": run.get("status", ""),
            "conclusion": run.get("conclusion", ""),
            "head_sha": run.get("head_sha", ""),
            "head_branch": str(run.get("head_branch", ""))[:200],
            "failed_jobs": diagnostics,
        }
