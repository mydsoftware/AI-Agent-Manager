"""ابزار استقرار (Deploy)."""

from __future__ import annotations

import os
import subprocess
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class DeployTool(Tool):
    """ابزار استقرار پروژه با پشتیبانی از Vercel و Local."""

    name = "deploy"
    description = "استقرار پروژه روی Vercel یا Local"
    permissions = [ToolPermission.DEPLOY]
    timeout = 120.0

    def __init__(self, workspace: str | None = None) -> None:
        self.workspace = workspace or os.getcwd()

    def validate(self, **kwargs: Any) -> bool:
        provider = kwargs.get("provider", "local")
        return provider in {"vercel", "local", "manual"}

    def execute(self, **kwargs: Any) -> ToolResult:
        provider = kwargs.get("provider", "local")
        command = kwargs.get("command", "")

        if provider == "vercel":
            return self._deploy_vercel(command)
        elif provider == "local":
            return self._deploy_local(command)
        else:
            return self._deploy_manual(command)

    def _deploy_vercel(self, command: str) -> ToolResult:
        """استقرار روی Vercel."""
        token = os.getenv("VERCEL_TOKEN", "")
        if not token:
            return ToolResult(False, error="VERCEL_TOKEN تنظیم نشده است.")

        cmd = command or "vercel --yes --prod"
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=self.timeout, cwd=self.workspace,
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else "",
                metadata={"provider": "vercel"},
            )
        except Exception as exc:
            return ToolResult(False, error=f"خطا در استقرار Vercel: {exc}")

    def _deploy_local(self, command: str) -> ToolResult:
        """اجرای محلی."""
        cmd = command or "python -m http.server 8080"
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=30, cwd=self.workspace,
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else "",
                metadata={"provider": "local"},
            )
        except Exception as exc:
            return ToolResult(False, error=f"خطا در اجرای محلی: {exc}")

    def _deploy_manual(self, command: str) -> ToolResult:
        """اجرای دستور استقرار سفارشی."""
        if not command:
            return ToolResult(False, error="دستور استقرار مشخص نشده است.")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=self.timeout, cwd=self.workspace,
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else "",
                metadata={"provider": "manual"},
            )
        except Exception as exc:
            return ToolResult(False, error=f"خطا در استقرار: {exc}")
