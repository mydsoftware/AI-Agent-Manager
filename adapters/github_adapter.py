from __future__ import annotations

import base64
import io
import json
import os
import re
import zipfile
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
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

    _SECRET_PATTERNS = (
        re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
        re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
        re.compile(r"(?i)((?:token|password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*)[^\s,;]+"),
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    )

    def __init__(self, token: str | None = None, api_url: str = "https://api.github.com") -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_url = api_url.rstrip("/")

    @staticmethod
    def _repository_path(repository: str) -> str:
        parts = repository.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("repository باید به شکل owner/name باشد.")
        return "/repos/" + "/".join(quote(part, safe="") for part in parts)

    @classmethod
    def _redact_log(cls, text: str, token: str | None = None) -> str:
        redacted = text
        if token:
            redacted = redacted.replace(token, "[REDACTED]")
        for pattern in cls._SECRET_PATTERNS:
            redacted = pattern.sub(
                lambda match: (match.group(1) + "[REDACTED]") if match.lastindex else "[REDACTED]",
                redacted,
            )
        return redacted

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
            raise RuntimeError(f"GitHub API خطای {error.code}: {self._redact_log(detail, self.token)}") from error

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
            raise RuntimeError(f"GitHub API خطای {error.code}: {self._redact_log(detail, self.token)}") from error

    def get_repository(self, repository: str) -> Any:
        return self._request("GET", self._repository_path(repository))

    def get_file(self, repository: str, path: str, ref: str | None = None) -> Any:
        encoded_path = quote(path.lstrip("/"), safe="/")
        suffix = "?" + urlencode({"ref": ref}) if ref else ""
        return self._request("GET", f"{self._repository_path(repository)}/contents/{encoded_path}{suffix}")

    def put_file(self, repository: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> Any:
        payload = {"message": message, "content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "branch": branch}
        if sha:
            payload["sha"] = sha
        encoded_path = quote(path.lstrip("/"), safe="/")
        return self._request("PUT", f"{self._repository_path(repository)}/contents/{encoded_path}", payload)

    def create_branch(self, repository: str, branch: str, base: str) -> Any:
        base_ref = quote(base, safe="")
        base_ref_data = self._request("GET", f"{self._repository_path(repository)}/git/ref/heads/{base_ref}")
        try:
            return self._request(
                "POST",
                f"{self._repository_path(repository)}/git/refs",
                {"ref": f"refs/heads/{branch}", "sha": base_ref_data["object"]["sha"]},
            )
        except RuntimeError as error:
            if "خطای 422" not in str(error):
                raise
            return self._request("GET", f"{self._repository_path(repository)}/git/ref/heads/{quote(branch, safe='')}")

    def create_pull_request(self, repository: str, head: str, base: str, title: str, body: str = "", draft: bool = True) -> Any:
        return self._request("POST", f"{self._repository_path(repository)}/pulls", {"title": title, "head": head, "base": base, "body": body, "draft": draft})

    def workflow_runs(self, repository: str, branch: str | None = None, workflow: str | None = None) -> Any:
        path = f"{self._repository_path(repository)}/actions/runs"
        if workflow:
            path = f"{self._repository_path(repository)}/actions/workflows/{quote(workflow, safe='')}/runs"
        query = {"per_page": 10}
        if branch:
            query["branch"] = branch
        return self._request("GET", path + "?" + urlencode(query))

    def workflow_log(self, repository: str, branch: str, head_sha: str | None = None, workflow: str | None = None) -> Any:
        runs = self.workflow_runs(repository, branch, workflow).get("workflow_runs", [])
        matching = [run for run in runs if not head_sha or run.get("head_sha") == head_sha]
        if not matching and runs and not any(run.get("head_sha") for run in runs):
            matching = runs[:1]
        if not matching:
            return {"available": False, "message": "اجرای CI متناظر پیدا نشد."}
        run = matching[0]
        jobs = self._request("GET", f"{self._repository_path(repository)}/actions/runs/{run['id']}/jobs?per_page=100").get("jobs", [])
        logs: list[str] = []
        for job in jobs:
            if job.get("conclusion") in {"failure", "cancelled", "timed_out", "action_required"}:
                try:
                    raw = self._request_bytes("GET", f"{self._repository_path(repository)}/actions/jobs/{job['id']}/logs")
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        for name in archive.namelist():
                            if not name.endswith("/"):
                                content = archive.read(name).decode("utf-8", errors="replace")
                                logs.append(f"### {job.get('name', job['id'])} / {name}\n{self._redact_log(content, self.token)}")
                except Exception as error:
                    logs.append(f"job {job.get('name')}: دریافت log شکست خورد: {self._redact_log(str(error), self.token)}")
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
        return self._request("GET", f"{self._repository_path(repository)}/compare/{quote(base, safe='')}...{quote(head, safe='')}")

    def dispatch_workflow(self, repository: str, workflow: str, branch: str, inputs: dict | None = None) -> Any:
        self._request(
            "POST",
            f"{self._repository_path(repository)}/actions/workflows/{quote(workflow, safe='')}/dispatches",
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
