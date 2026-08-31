"""ابزار مدیریت Git."""

from __future__ import annotations

import subprocess
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class GitTool(Tool):
    """ابزار عملیات Git با بررسی امنی."""

    name = "git"
    description = "عملیات Git: status, diff, log, branch, add, commit"
    permissions = [ToolPermission.GIT]
    timeout = 15.0

    ALLOWED_COMMANDS = {
        "status", "diff", "log", "branch", "add", "commit",
        "checkout", "stash", "show", "remote",
    }

    def __init__(self, workspace: str | None = None) -> None:
        import os
        self.workspace = workspace or os.getcwd()

    def validate(self, **kwargs: Any) -> bool:
        action = kwargs.get("action", "")
        return action in self.ALLOWED_COMMANDS

    def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action", "")
        if action not in self.ALLOWED_COMMANDS:
            return ToolResult(False, error=f"عملیات Git «{action}» پشتیبانی نمی‌شود.")

        args = self._build_args(action, kwargs)
        if args is None:
            return ToolResult(False, error=f"پارامترهای ناقص برای عملیات «{action}».")

        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.workspace,
            )
            success = result.returncode == 0
            return ToolResult(
                success=success,
                output=result.stdout.strip(),
                error=result.stderr.strip() if result.returncode != 0 else "",
                metadata={"action": action, "exit_code": result.returncode},
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, error="عملیات Git منقضی شد.")
        except FileNotFoundError:
            return ToolResult(False, error="Git نصب نشده است.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در عملیات Git: {exc}")

    def _build_args(self, action: str, kwargs: dict[str, Any]) -> list[str] | None:
        """آرگومان‌های Git را بر اساس عملیات می‌سازد."""
        if action == "status":
            return ["status", "--porcelain"]
        elif action == "diff":
            return ["diff", kwargs.get("ref", "HEAD")]
        elif action == "log":
            count = kwargs.get("count", 10)
            return ["log", f"--oneline", f"-{count}"]
        elif action == "branch":
            return ["branch", "-a"]
        elif action == "add":
            paths = kwargs.get("paths", [])
            if not paths:
                return None
            return ["add"] + paths
        elif action == "commit":
            message = kwargs.get("message", "")
            if not message:
                return None
            return ["commit", "-m", message]
        elif action == "checkout":
            branch = kwargs.get("branch", "")
            if not branch:
                return None
            return ["checkout", branch]
        elif action == "stash":
            return ["stash", "list"]
        elif action == "show":
            ref = kwargs.get("ref", "HEAD")
            return ["show", "--stat", ref]
        elif action == "remote":
            return ["remote", "-v"]
        return None
