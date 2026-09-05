"""لایه کنترل استقرار Vercel برای حلقه توسعه خودکار."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


@dataclass(frozen=True)
class VercelConfig:
    token: str
    api_base_url: str = "https://api.vercel.com"

    @classmethod
    def from_env(cls) -> "VercelConfig":
        return cls(token=os.getenv("VERCEL_TOKEN", "").strip())

    @property
    def configured(self) -> bool:
        return bool(self.token)


class VercelDeploymentService:
    """Facade محدود Vercel؛ Token و مقادیر حساس هرگز در پاسخ برگردانده نمی‌شوند."""

    def __init__(self, config: VercelConfig | None = None) -> None:
        self.config = config or VercelConfig.from_env()

    def status(self) -> dict[str, Any]:
        return {"configured": self.config.configured, "provider": "vercel", "api_base_url": self.config.api_base_url}

    def _headers(self) -> dict[str, str]:
        if not self.config.configured:
            raise RuntimeError("VERCEL_TOKEN تنظیم نشده است.")
        return {"Authorization": f"Bearer {self.config.token}", "Accept": "application/json", "Content-Type": "application/json"}

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not path.startswith("/") or ".." in path:
            raise ValueError("مسیر Vercel نامعتبر است.")
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(self.config.api_base_url + path, data=body, method=method.upper(), headers=self._headers())
        try:
            with urlopen(req, timeout=20) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Vercel API خطا داد ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError("ارتباط با Vercel برقرار نشد.") from error

    def project(self, project_id: str, team_id: str | None = None) -> dict[str, Any]:
        project_id = project_id.strip()
        if not project_id:
            raise ValueError("project_id الزامی است.")
        query = f"?teamId={team_id.strip()}" if team_id and team_id.strip() else ""
        return self.request("GET", f"/v9/projects/{project_id}{query}")

    def deployments(self, project_id: str, team_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        project_id = project_id.strip()
        if not project_id:
            raise ValueError("project_id الزامی است.")
        limit = max(1, min(limit, 100))
        query = f"?projectId={project_id}&limit={limit}"
        if team_id and team_id.strip():
            query += f"&teamId={team_id.strip()}"
        return self.request("GET", f"/v6/deployments{query}")

    def deployment(self, deployment_id: str, team_id: str | None = None) -> dict[str, Any]:
        deployment_id = deployment_id.strip()
        if not deployment_id:
            raise ValueError("deployment_id الزامی است.")
        query = f"?teamId={team_id.strip()}" if team_id and team_id.strip() else ""
        return self.request("GET", f"/v13/deployments/{deployment_id}{query}")
