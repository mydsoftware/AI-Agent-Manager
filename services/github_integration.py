"""لایه یکپارچه GitHub برای پروژه‌های هسته مرکزی هوش مصنوعی."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


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
    """Facade امن برای عملیات GitHub؛ هیچ Secretای در خروجی برگردانده نمی‌شود."""

    def __init__(self, config: GitHubConfig | None = None) -> None:
        self.config = config or GitHubConfig.from_env()

    def status(self) -> dict[str, Any]:
        return {
            "configured": self.config.configured,
            "provider": "github",
            "api_base_url": self.config.api_base_url,
        }

    def build_headers(self) -> dict[str, str]:
        if not self.config.configured:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.config.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def repository_url(self, owner: str, repository: str) -> str:
        owner = owner.strip()
        repository = repository.strip()
        if not owner or not repository:
            raise ValueError("owner و repository الزامی هستند.")
        if any(part in {".", ".."} or "/" in part or "\\" in part for part in (owner, repository)):
            raise ValueError("شناسه Repository نامعتبر است.")
        return f"{self.config.api_base_url}/repos/{owner}/{repository}"
