from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class GitHubClient(Protocol):
    """قرارداد موردنیاز برای اتصال به سرویس GitHub."""

    def get_repository(self, repository: str) -> Any:
        """اطلاعات یک مخزن را دریافت می‌کند."""
        ...

    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any:
        """محتوای یک فایل را دریافت می‌کند."""
        ...


@dataclass
class GitHubAdapter:
    """لایه واسط مستقل بین Manager و سرویس GitHub."""

    client: GitHubClient

    def repository(self, repository: str) -> Any:
        """اطلاعات مخزن را از کلاینت دریافت می‌کند."""
        return self.client.get_repository(repository)

    def file(self, repository: str, path: str, ref: str | None = None) -> Any:
        """محتوای فایل را از کلاینت دریافت می‌کند."""
        return self.client.get_file(repository, path, ref)
