"""ابزار اجرای تست."""

from __future__ import annotations

import subprocess
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class TestTool(Tool):
    """ابزار اجرای تست‌ها و بررسی نتیجه."""

    name = "test"
    description = "اجرای تست‌های pytest و بررسی نتیجه"
    permissions = [ToolPermission.EXECUTE_COMMAND]
    timeout = 120.0

    def __init__(self, workspace: str | None = None) -> None:
        import os
        self.workspace = workspace or os.getcwd()

    def validate(self, **kwargs: Any) -> bool:
        command = kwargs.get("command", "pytest -q")
        return bool(command and isinstance(command, str))

    def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "pytest -q")
        timeout = kwargs.get("timeout", self.timeout)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace,
            )
            output = result.stdout + result.stderr
            success = result.returncode == 0
            return ToolResult(
                success=success,
                output=output,
                error=result.stderr if not success else "",
                metadata={"command": command, "exit_code": result.returncode},
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, error=f"تست پس از {timeout} ثانیه منقضی شد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در اجرای تست: {exc}")
