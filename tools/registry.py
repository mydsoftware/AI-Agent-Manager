"""ثبت و مدیریت ابزارها."""

from __future__ import annotations

from typing import Any

from .base import Tool, ToolPermission, ToolResult


class ToolRegistry:
    """ثبت مرکزی ابزارها برای کشف و مدیریت."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._permissions: dict[ToolPermission, set[str]] = {
            perm: set() for perm in ToolPermission
        }

    def register(self, tool: Tool) -> None:
        """ابزار جدیدی را ثبت می‌کند."""
        self._tools[tool.name] = tool
        for perm in tool.permissions:
            self._permissions[perm].add(tool.name)

    def get(self, name: str) -> Tool | None:
        """ابزار با نام مشخص را برمی‌گرداند."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """نام تمام ابزارهای ثبت‌شده را برمی‌گرداند."""
        return sorted(self._tools.keys())

    def list_by_permission(self, permission: ToolPermission) -> list[str]:
        """ابزارهای دارای مجوز مشخص را برمی‌گرداند."""
        return sorted(self._permissions.get(permission, set()))

    def list_schemas(self) -> list[dict[str, Any]]:
        """Schema تمام ابزارها را برمی‌گرداند."""
        return [tool.to_schema() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs: Any) -> ToolResult:
        """ابزار را با نام و اعتبارسنجی اجرا می‌کند."""
        tool = self.get(name)
        if tool is None:
            return ToolResult(False, error=f"ابزار «{name}» ثبت نشده است.")

        if not tool.validate(**kwargs):
            return ToolResult(False, error=f"ورودی‌های ابزار «{name}» معتبر نیستند.")

        try:
            return tool.execute(**kwargs)
        except Exception as exc:
            return ToolResult(False, error=f"خطا در اجرای ابزار «{name}»: {exc}")

    def has_permission(self, tool_name: str, permission: ToolPermission) -> bool:
        """بررسی می‌کند آیا ابزار مجوز مشخص را دارد."""
        tool = self.get(tool_name)
        if tool is None:
            return False
        return permission in tool.permissions

    def health(self) -> dict[str, bool]:
        """وضعیت ابزارها را برمی‌گرداند."""
        return {name: True for name in self._tools}


def create_default_registry() -> ToolRegistry:
    """Registry پیش‌فرض با تمام ابزارهای استاندارد را می‌سازد."""
    from .filesystem import FilesystemTool
    from .git import GitTool
    from .shell import ShellTool
    from .test import TestTool

    registry = ToolRegistry()
    registry.register(FilesystemTool())
    registry.register(ShellTool())
    registry.register(GitTool())
    registry.register(TestTool())
    return registry
