"""لایه کنترل استقرار Vercel برای حلقه توسعه خودکار."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from services.github_integration import GitHubIntegration


@dataclass(frozen=True)
class VercelConfig:
    """تنظیمات اتصال به Vercel را نگه می‌دارد."""

    token: str
    api_base_url: str = "https://api.vercel.com"

    @classmethod
    def from_env(cls) -> "VercelConfig":
        """تنظیمات را از Environment می‌خواند."""
        return cls(token=os.getenv("VERCEL_TOKEN", "").strip())

    @property
    def configured(self) -> bool:
        """مشخص می‌کند Token در دسترس است یا خیر."""
        return bool(self.token)


class VercelDeploymentService:
    """Facade محدود Vercel؛ Token و مقادیر حساس هرگز در پاسخ برگردانده نمی‌شوند."""

    def __init__(self, config: VercelConfig | None = None) -> None:
        """سرویس را با تنظیمات داده‌شده یا Environment می‌سازد."""
        self.config = config or VercelConfig.from_env()

    def status(self) -> dict[str, Any]:
        """وضعیت پیکربندی Vercel را بدون Secret برمی‌گرداند."""
        return {"configured": self.config.configured, "provider": "vercel", "api_base_url": self.config.api_base_url}

    def _headers(self) -> dict[str, str]:
        """Headerهای احراز هویت Vercel را می‌سازد."""
        if not self.config.configured:
            raise RuntimeError("VERCEL_TOKEN تنظیم نشده است.")
        return {"Authorization": f"Bearer {self.config.token}", "Accept": "application/json", "Content-Type": "application/json"}

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """یک درخواست Vercel را اجرا و خطا را بدون Secret گزارش می‌کند."""
        if not path.startswith("/") or ".." in path:
            raise ValueError("مسیر Vercel نامعتبر است.")
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = Request(self.config.api_base_url + path, data=body, method=method.upper(), headers=self._headers())
        try:
            with urlopen(req, timeout=20) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as error:
            raw_detail = error.read().decode("utf-8", errors="replace")
            detail = GitHubIntegration._sanitize_log(raw_detail, 500).replace(self.config.token, "[REDACTED]")
            raise RuntimeError(f"Vercel API خطا داد ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError("ارتباط با Vercel برقرار نشد.") from error

    def project(self, project_id: str, team_id: str | None = None) -> dict[str, Any]:
        """اطلاعات Project را با Query امن می‌خواند."""
        project_id = project_id.strip()
        if not project_id:
            raise ValueError("project_id الزامی است.")
        params = {"teamId": team_id.strip()} if team_id and team_id.strip() else {}
        query = "?" + urlencode(params) if params else ""
        return self.request("GET", f"/v9/projects/{quote(project_id, safe='')}{query}")

    def deployments(self, project_id: str, team_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        """Deploymentهای Project را با Query امن می‌خواند."""
        project_id = project_id.strip()
        if not project_id:
            raise ValueError("project_id الزامی است.")
        limit = max(1, min(int(limit), 100))
        params: dict[str, str | int] = {"projectId": project_id, "limit": limit}
        if team_id and team_id.strip():
            params["teamId"] = team_id.strip()
        query = "?" + urlencode(params)
        return self.request("GET", f"/v6/deployments{query}")

    def deployment(self, deployment_id: str, team_id: str | None = None) -> dict[str, Any]:
        """اطلاعات یک Deployment را با Query امن می‌خواند."""
        deployment_id = deployment_id.strip()
        if not deployment_id:
            raise ValueError("deployment_id الزامی است.")
        params = {"teamId": team_id.strip()} if team_id and team_id.strip() else {}
        query = "?" + urlencode(params) if params else ""
        return self.request("GET", f"/v13/deployments/{quote(deployment_id, safe='')}{query}")
