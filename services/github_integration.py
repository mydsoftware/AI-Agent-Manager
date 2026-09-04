"""لایه یکپارچه GitHub برای پروژه‌های هسته مرکزی هوش مصنوعی."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


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
        """درخواست GitHub با خطای قابل‌مدیریت و بدون افشای Token."""
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
