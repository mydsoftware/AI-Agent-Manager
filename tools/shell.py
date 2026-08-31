"""ابزار اجرای کنترل‌شده فرمان‌ها."""

from __future__ import annotations

import os
import re
import subprocess
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class ShellTool(Tool):
    """ابزار اجرای کنترل‌شده فرمان‌ها با Timeout و Secret Protection."""

    name = "shell"
    description = "اجرای کنترل‌شده فرمان‌های سیستم با اعتبارسنجی و محدودیت"
    permissions = [ToolPermission.EXECUTE_COMMAND]
    timeout = 30.0

    # فرمان‌های ممنوع
    BLOCKED_PATTERNS = [
        r"\bsudo\b",
        r"\bdoas\b",
        r"\bpkexec\b",
        r"\brm\s+-rf\s+/\b",
        r"\bgit\s+push\b",
        r"\bgit\s+commit\b",
        r"\bgit\s+rebase\b",
        r"\bnpm\s+install\s+-g\b",
        r"\bpip\s+install\s+--?g\b",
    ]

    # الگوهای Secret در خروجی
    SECRET_PATTERNS = [
        (r"(?:api[_-]?key|token|secret|password)\s*[=:]\s*\S+", "***REDACTED***"),
    ]

    def __init__(self, workspace: str | None = None, allowed_commands: list[str] | None = None) -> None:
        self.workspace = workspace or os.getcwd()
        self.allowed_commands = allowed_commands

    def validate(self, **kwargs: Any) -> bool:
        """اعتبارسنجی فرمان ورودی."""
        command = kwargs.get("command", "")
        if not command or not isinstance(command, str):
            return False
        if len(command) > 4096:
            return False
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        if self.allowed_commands is not None:
            base_cmd = command.split()[0] if command.split() else ""
            if base_cmd not in self.allowed_commands:
                return False
        return True

    def execute(self, **kwargs: Any) -> ToolResult:
        """فرمان را با Timeout و اعتبارسنجی اجرا می‌کند."""
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", self.timeout)

        if not self.validate(command=command):
            return ToolResult(False, error="فرمان مجاز نیست یا اعتبارسنجی ناموفق بود.")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace,
            )
            stdout = self._redact(result.stdout)
            stderr = self._redact(result.stderr)
            success = result.returncode == 0
            return ToolResult(
                success=success,
                output=stdout,
                error=stderr,
                metadata={"exit_code": result.returncode},
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, error=f"فرمان پس از {timeout} ثانیه منقضی شد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در اجرای فرمان: {exc}")

    def _redact(self, text: str) -> str:
        """Secretها را از خروجی حذف می‌کند."""
        for pattern, replacement in self.SECRET_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
