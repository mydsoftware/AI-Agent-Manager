from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class GitHubClient(Protocol):
    """قرارداد موردنیاز برای اتصال به سرویس GitHub."""

    def get_repository(self, repository: str) -> Any:
        """اطلاعات یک مخزن را دریافت می‌کند."""
        ...

    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any:
        """محتوای یک فایل را دریافت می‌کند."""
        ...

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        """یک فایل را ایجاد یا به‌روزرسانی می‌کند."""
        ...


class GitHubAPIClient:
    """کلاینت سبک GitHub REST API بدون وابستگی خارجی."""

    def __init__(self, token: str | None = None, api_url: str = "https://api.github.com") -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_url = api_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict | None = None) -> Any:
        """درخواست احراز هویت‌شده‌ای به GitHub ارسال می‌کند."""
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AI-Agent-Manager",
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(f"{self.api_url}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API خطای {error.code}: {detail}") from error

    def get_repository(self, repository: str) -> Any:
        """اطلاعات مخزن را دریافت می‌کند."""
        return self._request("GET", f"/repos/{repository}")

    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any:
        """محتوای فایل و اطلاعات نسخه آن را دریافت می‌کند."""
        suffix = f"?ref={ref}" if ref else ""
        return self._request("GET", f"/repos/{repository}/contents/{path}{suffix}")

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        """فایل را با رعایت SHA فعلی ایجاد یا به‌روزرسانی می‌کند."""
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        return self._request("PUT", f"/repos/{repository}/contents/{path}", payload)


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

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        """ایجاد یا به‌روزرسانی فایل را به کلاینت واگذار می‌کند."""
        return self.client.put_file(repository, path, content, message, branch, sha)
