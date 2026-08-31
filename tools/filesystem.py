"""ابزار دسترسی به سیستم فایل با Sandbox."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .base import Tool, ToolPermission, ToolResult


class FilesystemTool(Tool):
    """ابزار خواندن، نوشتن و جستجوی فایل‌ها با محدودیت Workspace."""

    name = "filesystem"
    description = "خواندن، نوشتن، ویرایش، حذف و جستجوی فایل‌ها در Workspace پروژه"
    permissions = [ToolPermission.READ_FILE, ToolPermission.WRITE_FILE, ToolPermission.DELETE_FILE]
    timeout = 15.0

    def __init__(self, workspace: str | None = None) -> None:
        self.workspace = Path(workspace or os.getcwd()).resolve()

    def _safe_path(self, path: str) -> Path | None:
        """مسیر را ایجاد و بررسی می‌کند که در Workspace باشد (جلوگیری از Path Traversal)."""
        try:
            resolved = (self.workspace / path).resolve()
        except (ValueError, OSError):
            return None
        if not str(resolved).startswith(str(self.workspace)):
            return None
        return resolved

    def validate(self, **kwargs: Any) -> bool:
        """اعتبارسنجی ورودی‌ها."""
        action = kwargs.get("action", "")
        if action not in {"read", "write", "edit", "delete", "search"}:
            return False
        if action in {"read", "delete", "edit"} and "path" not in kwargs:
            return False
        if action == "write" and ("path" not in kwargs or "content" not in kwargs):
            return False
        return True

    def execute(self, **kwargs: Any) -> ToolResult:
        """عملیات فایل را اجرا می‌کند."""
        action = kwargs.get("action", "")

        if action == "read":
            return self._read(kwargs["path"])
        elif action == "write":
            return self._write(kwargs["path"], kwargs["content"])
        elif action == "edit":
            return self._edit(kwargs["path"], kwargs.get("old_string", ""), kwargs.get("new_string", ""))
        elif action == "delete":
            return self._delete(kwargs["path"])
        elif action == "search":
            return self._search(kwargs.get("pattern", ""), kwargs.get("path", "."))
        return ToolResult(False, error=f"عملیات ناشناخته: {action}")

    def _read(self, path: str) -> ToolResult:
        safe = self._safe_path(path)
        if safe is None:
            return ToolResult(False, error="مسیر خارج از Workspace است.")
        if not safe.exists():
            return ToolResult(False, error=f"فایل وجود ندارد: {path}")
        try:
            content = safe.read_text(encoding="utf-8")
            return ToolResult(True, output=content, metadata={"size": len(content)})
        except Exception as exc:
            return ToolResult(False, error=f"خطا در خواندن فایل: {exc}")

    def _write(self, path: str, content: str) -> ToolResult:
        safe = self._safe_path(path)
        if safe is None:
            return ToolResult(False, error="مسیر خارج از Workspace است.")
        try:
            safe.parent.mkdir(parents=True, exist_ok=True)
            safe.write_text(content, encoding="utf-8")
            return ToolResult(True, output=f"فایل {path} نوشته شد.", metadata={"size": len(content)})
        except Exception as exc:
            return ToolResult(False, error=f"خطا در نوشتن فایل: {exc}")

    def _edit(self, path: str, old_string: str, new_string: str) -> ToolResult:
        safe = self._safe_path(path)
        if safe is None:
            return ToolResult(False, error="مسیر خارج از Workspace است.")
        if not safe.exists():
            return ToolResult(False, error=f"فایل وجود ندارد: {path}")
        try:
            content = safe.read_text(encoding="utf-8")
            if old_string not in content:
                return ToolResult(False, error="رشته قدیج در فایل یافت نشد.")
            new_content = content.replace(old_string, new_string, 1)
            safe.write_text(new_content, encoding="utf-8")
            return ToolResult(True, output=f"فایل {path} ویرایش شد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در ویرایش فایل: {exc}")

    def _delete(self, path: str) -> ToolResult:
        safe = self._safe_path(path)
        if safe is None:
            return ToolResult(False, error="مسیر خارج از Workspace است.")
        if not safe.exists():
            return ToolResult(False, error=f"فایل وجود ندارد: {path}")
        try:
            safe.unlink()
            return ToolResult(True, output=f"فایل {path} حذف شد.")
        except Exception as exc:
            return ToolResult(False, error=f"خطا در حذف فایل: {exc}")

    def _search(self, pattern: str, search_path: str) -> ToolResult:
        base = self._safe_path(search_path)
        if base is None:
            return ToolResult(False, error="مسیر جستجو خارج از Workspace است.")
        if not base.exists():
            return ToolResult(False, error=f"مسیر وجود ندارد: {search_path}")
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            matches: list[str] = []
            for root, _dirs, files in os.walk(base):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if regex.search(line):
                                    rel = os.path.relpath(fpath, self.workspace)
                                    matches.append(f"{rel}:{i}: {line.strip()}")
                                    if len(matches) >= 50:
                                        return ToolResult(True, output="\n".join(matches))
                    except (OSError, UnicodeDecodeError):
                        continue
            return ToolResult(True, output="\n".join(matches) if matches else "نتیجه‌ای یافت نشد.")
        except re.error as exc:
            return ToolResult(False, error=f"الگوی نامعتبر: {exc}")
