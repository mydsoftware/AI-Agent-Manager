from __future__ import annotations

import base64
import io
import json
import os
import zipfile
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class GitHubClient(Protocol):
    def get_repository(self, repository: str) -> Any: ...
    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any: ...
    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any: ...
    def create_branch(self, repository: str, branch: str, base: str) -> Any: ...
    def create_pull_request(self, repository: str, head: str, base: str, title: str, body: str = "", draft: bool = True) -> Any: ...
    def workflow_runs(self, repository: str, branch: str | None = None, workflow: str | None = None) -> Any: ...
    def workflow_log(self, repository: str, branch: str, head_sha: str | None = None, workflow: str | None = None) -> Any: ...
    def compare(self, repository: str, base: str, head: str) -> Any: ...
    def dispatch_workflow(self, repository: str, workflow: str, branch: str, inputs: dict | None = None) -> Any: ...


class GitHubAPIClient:
    """کلاینت سبک GitHub REST API بدون وابستگی خارجی."""

    def __init__(self, token: str | None = None, api_url: str = "https://api.github.com") -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_url = api_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict | None = None) -> Any:
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
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {"accepted": True}
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API خطای {error.code}: {detail}") from error

    def _request_bytes(self, method: str, path: str) -> bytes:
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN تنظیم نشده است.")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AI-Agent-Manager",
        }
        request = Request(f"{self.api_url}{path}", headers=headers, method=method)
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
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

    def create_branch(self, repository: str, branch: str, base: str) -> Any:
        base_ref = self._request("GET", f"/repos/{repository}/git/ref/heads/{base}")
        try:
            return self._request(
                "POST",
                f"/repos/{repository}/git/refs",
                {"ref": f"refs/heads/{branch}", "sha": base_ref["object"]["sha"]},
            )
        except RuntimeError as error:
            if "خطای 422" not in str(error):
                raise
            return self._request("GET", f"/repos/{repository}/git/ref/heads/{branch}")

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

    def workflow_log(self, repository: str, branch: str, head_sha: str | None = None, workflow: str | None = None) -> Any:
        runs = self.workflow_runs(repository, branch, workflow).get("workflow_runs", [])
        matching = [run for run in runs if not head_sha or run.get("head_sha") == head_sha]
        if not matching and runs and not any(run.get("head_sha") for run in runs):
            matching = runs[:1]
        if not matching:
            return {"available": False, "message": "اجرای CI متناظر پیدا نشد."}
        run = matching[0]
        jobs = self._request("GET", f"/repos/{repository}/actions/runs/{run['id']}/jobs?per_page=100").get("jobs", [])
        logs: list[str] = []
        for job in jobs:
            if job.get("conclusion") in {"failure", "cancelled", "timed_out", "action_required"}:
                try:
                    raw = self._request_bytes("GET", f"/repos/{repository}/actions/jobs/{job['id']}/logs")
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        for name in archive.namelist():
                            if not name.endswith("/"):
                                logs.append(f"### {job.get('name', job['id'])} / {name}\n{archive.read(name).decode('utf-8', errors='replace')}")
                except Exception as error:
                    logs.append(f"job {job.get('name')}: دریافت log شکست خورد: {error}")
        return {
            "available": True,
            "run_id": run.get("id"),
            "run_number": run.get("run_number"),
            "head_sha": run.get("head_sha"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "logs": "\n\n".join(logs),
        }

    def compare(self, repository: str, base: str, head: str) -> Any:
        return self._request("GET", f"/repos/{repository}/compare/{base}...{head}")

    def dispatch_workflow(self, repository: str, workflow: str, branch: str, inputs: dict | None = None) -> Any:
        self._request(
            "POST",
            f"/repos/{repository}/actions/workflows/{workflow}/dispatches",
            {"ref": branch, "inputs": inputs or {}},
        )
        return {"accepted": True, "repository": repository, "workflow": workflow, "branch": branch}


@dataclass
class GitHubAdapter:
    client: GitHubClient

    def repository(self, repository: str) -> Any:
        return self.client.get_repository(repository)

    def file(self, repository: str, path: str, ref: str | None = None) -> Any:
        return self.client.get_file(repository, path, ref)

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        return self.client.put_file(repository, path, content, message, branch, sha)

    def create_branch(self, repository: str, branch: str, base: str) -> Any:
        return self.client.create_branch(repository, branch, base)

    def create_pull_request(self, repository: str, head: str, base: str, title: str, body: str = "", draft: bool = True) -> Any:
        return self.client.create_pull_request(repository, head, base, title, body, draft)

    def workflow_runs(self, repository: str, branch: str | None = None, workflow: str | None = None) -> Any:
        return self.client.workflow_runs(repository, branch, workflow)

    def workflow_log(self, repository: str, branch: str, head_sha: str | None = None, workflow: str | None = None) -> Any:
        return self.client.workflow_log(repository, branch, head_sha, workflow)

    def compare(self, repository: str, base: str, head: str) -> Any:
        return self.client.compare(repository, base, head)

    def dispatch_workflow(self, repository: str, workflow: str, branch: str, inputs: dict | None = None) -> Any:
        return self.client.dispatch_workflow(repository, workflow, branch, inputs)
