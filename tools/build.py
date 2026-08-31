"""ابزار اجرای Build."""

from __future__ import annotations

import subprocess
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class BuildTool(Tool):
    """ابزار اجرای فرآیند Build پروژه."""

    name = "build"
    description = "اجرای فرآیند Build پروژه"
    permissions = [ToolPermission.EXECUTE_COMMAND]
    timeout = 180.0

    def __init__(self, workspace: str | None = None) -> None:
        import os
        self.workspace = workspace or os.getcwd()

    def validate(self, **kwargs: Any) -> bool:
        command = kwargs.get("command", "")
        return bool(command and isinstance(command, str))

    def execute(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command", "")
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
                output=output[-5000:] if len(output) > 5000 else output,
                error=result.stderr if not success else "",
                metadata={"command": command, "exit_code": result.returncode},
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, error=f"Build پس از {timeout} ثانیه منقضی شد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در اجرای Build: {exc}")
