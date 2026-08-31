"""ابزار اجرای کد Python."""

from __future__ import annotations

import subprocess
import tempfile
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class PythonTool(Tool):
    """ابزار اجرای ایمن کد Python در Sandbox."""

    name = "python"
    description = "اجرای ایمن کد Python در محیط محدود"
    permissions = [ToolPermission.EXECUTE_COMMAND]
    timeout = 60.0

    def __init__(self, workspace: str | None = None) -> None:
        import os
        self.workspace = workspace or os.getcwd()

    def validate(self, **kwargs: Any) -> bool:
        code = kwargs.get("code", "")
        return bool(code and isinstance(code, str) and len(code) < 50000)

    def execute(self, **kwargs: Any) -> ToolResult:
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", self.timeout)

        if not self.validate(code=code):
            return ToolResult(False, error="کد Python نامعتبر یا بیش از حد طولانی است.")

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace,
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else "",
                metadata={"exit_code": result.returncode},
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, error=f"اجرا پس از {timeout} ثانیه منقضی شد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در اجرای Python: {exc}")
        finally:
            import os
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
