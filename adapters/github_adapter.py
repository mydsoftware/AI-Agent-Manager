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

    def get_repository(self, repository: str) -> Any: ...
    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any: ...
    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any: ...
    def create_repository(self, owner: str, name: str, description: str = "", private: bool = True, auto_init: bool = True) -> Any: ...
    def repository_dispatch(self, repository: str, event_type: str, client_payload: dict[str, Any]) -> Any: ...
    def create_branch(self, repository: str, branch: str, base: str) -> Any: ...
    def create_pull_request(self, repository: str, head: str, base: str, title: str, body: str = "", draft: bool = True) -> Any: ...
    def workflow_runs(self, repository: str, branch: str | None = None, workflow: str | None = None) -> Any: ...


class GitHubAPIClient:
    """کلاینت سبک GitHub REST API بدون وابستگی خارجی."""

    def __init__(self, token: str | None = None, api_url: str = "https://api.github.com") -> None:
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_PAT")
        self.api_url = api_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict | None = None) -> Any:
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN یا GH_PAT تنظیم نشده است.")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "AI-Agent-Manager",
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(f"{self.api_url}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {"status": response.status}
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API خطای {error.code}: {detail}") from error

    def get_repository(self, repository: str) -> Any:
        return self._request("GET", f"/repos/{repository}")

    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any:
        suffix = f"?ref={ref}" if ref else ""
        return self._request("GET", f"/repos/{repository}/contents/{path}{suffix}")

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        payload = {"message": message, "content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "branch": branch}
        if sha:
            payload["sha"] = sha
        return self._request("PUT", f"/repos/{repository}/contents/{path}", payload)

    def create_repository(self, owner: str, name: str, description: str = "", private: bool = True, auto_init: bool = True) -> Any:
        result = self._request("POST", "/user/repos", {
            "name": name,
            "description": description[:350],
            "private": private,
            "auto_init": auto_init,
            "has_issues": True,
            "has_projects": False,
            "has_wiki": False,
            "has_discussions": False,
        })
        actual_owner = result.get("owner", {}).get("login")
        if owner and actual_owner != owner:
            raise RuntimeError(f"Repository با مالک مورد انتظار ساخته نشد: {result.get('full_name')}")
        return result

    def repository_dispatch(self, repository: str, event_type: str, client_payload: dict[str, Any]) -> Any:
        return self._request("POST", f"/repos/{repository}/dispatches", {"event_type": event_type, "client_payload": client_payload})

    def create_branch(self, repository: str, branch: str, base: str) -> Any:
        base_ref = self._request("GET", f"/repos/{repository}/git/ref/heads/{base}")
        return self._request("POST", f"/repos/{repository}/git/refs", {"ref": f"refs/heads/{branch}", "sha": base_ref["object"]["sha"]})

    def create_pull_request(self, repository: str, head: str, base: str, title: str, body: str = "", draft: bool = True) -> Any:
        return self._request("POST", f"/repos/{repository}/pulls", {"title": title, "head": head, "base": base, "body": body, "draft": draft})

    def workflow_runs(self, repository: str, branch: str | None = None, workflow: str | None = None) -> Any:
        path = f"/repos/{repository}/actions/runs"
        if workflow:
            path = f"/repos/{repository}/actions/workflows/{workflow}/runs"
        query = "?per_page=10"
        if branch:
            query += f"&branch={branch}"
        return self._request("GET", path + query)


@dataclass
class GitHubAdapter:
    """لایه واسط مستقل بین Manager و سرویس GitHub."""

    client: GitHubClient

    def repository(self, repository: str) -> Any:
        return self.client.get_repository(repository)

    def file(self, repository: str, path: str, ref: str | None = None) -> Any:
        return self.client.get_file(repository, path, ref)

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        return self.client.put_file(repository, path, content, message, branch, sha)

    def create_repository(self, owner: str, name: str, description: str = "", private: bool = True, auto_init: bool = True) -> Any:
        return self.client.create_repository(owner, name, description, private, auto_init)

    def repository_dispatch(self, repository: str, event_type: str, client_payload: dict[str, Any]) -> Any:
        return self.client.repository_dispatch(repository, event_type, client_payload)

    def create_branch(self, repository: str, branch: str, base: str) -> Any:
        return self.client.create_branch(repository, branch, base)

    def create_pull_request(self, repository: str, head: str, base: str, title: str, body: str = "", draft: bool = True) -> Any:
        return self.client.create_pull_request(repository, head, base, title, body, draft)

    def workflow_runs(self, repository: str, branch: str | None = None, workflow: str | None = None) -> Any:
        return self.client.workflow_runs(repository, branch, workflow)
