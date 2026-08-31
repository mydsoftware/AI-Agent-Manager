"""ابزار مشاهده و جستجوی لاگ‌ها."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class LogsTool(Tool):
    """ابزار مشاهده و جستجوی لاگ‌ها."""

    name = "logs"
    description = "مشاهده و جستجوی لاگ‌ها و فایل‌های خروجی"
    permissions = [ToolPermission.READ_FILE]
    timeout = 10.0

    def __init__(self, workspace: str | None = None) -> None:
        self.workspace = Path(workspace or os.getcwd())

    def validate(self, **kwargs: Any) -> bool:
        action = kwargs.get("action", "read")
        return action in {"read", "search", "tail", "list"}

    def execute(self, **kwargs: Any) -> ToolResult:
        action = kwargs.get("action", "read")
        path = kwargs.get("path", "")
        pattern = kwargs.get("pattern", "")
        lines = kwargs.get("lines", 100)

        if action == "list":
            return self._list_logs()
        elif action == "read":
            return self._read_log(path, lines)
        elif action == "search":
            return self._search_log(path, pattern)
        elif action == "tail":
            return self._tail_log(path, lines)
        return ToolResult(False, error=f"عملیات ناشناخته: {action}")

    def _list_logs(self) -> ToolResult:
        log_dirs = ["logs", "log", "data", "."]
        files: list[str] = []
        for d in log_dirs:
            log_path = self.workspace / d
            if log_path.exists():
                for f in log_path.iterdir():
                    if f.is_file() and (f.suffix in {".log", ".txt"} or "log" in f.name.lower()):
                        files.append(str(f.relative_to(self.workspace)))
        return ToolResult(True, output="\n".join(sorted(files)) if files else "فایل لاگی یافت نشد.")

    def _read_log(self, path: str, lines: int) -> ToolResult:
        if not path:
            return ToolResult(False, error="مسیر فایل لاگ مشخص نشده.")
        target = self.workspace / path
        if not target.exists():
            return ToolResult(False, error=f"فایل لاگ وجود ندارد: {path}")
        try:
            content = target.read_text(encoding="utf-8", errors="replace")
            all_lines = content.splitlines()
            tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return ToolResult(True, output="\n".join(tail))
        except Exception as exc:
            return ToolResult(False, error=f"خطا در خواندن لاگ: {exc}")

    def _search_log(self, path: str, pattern: str) -> ToolResult:
        if not path or not pattern:
            return ToolResult(False, error="مسیر و الگوی جستجو الزامی است.")
        target = self.workspace / path
        if not target.exists():
            return ToolResult(False, error=f"فایل لاگ وجود ندارد: {path}")
        try:
            import re
            regex = re.compile(pattern, re.IGNORECASE)
            content = target.read_text(encoding="utf-8", errors="replace")
            matches = [line for line in content.splitlines() if regex.search(line)]
            return ToolResult(True, output="\n".join(matches[-50:]) if matches else "نتیجه‌ای یافت نشد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در جستجوی لاگ: {exc}")

    def _tail_log(self, path: str, lines: int) -> ToolResult:
        return self._read_log(path, lines)
