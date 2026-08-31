"""تست‌های سیستم ابزارها."""

from __future__ import annotations

import os
import tempfile

from tools.base import Tool, ToolPermission, ToolResult
from tools.registry import ToolRegistry, create_default_registry
from tools.filesystem import FilesystemTool
from tools.shell import ShellTool
from tools.test import TestTool


def test_tool_result_success() -> None:
    """ToolResult معتبر ساخته می‌شود."""
    result = ToolResult(success=True, output="ok")
    assert result.success is True
    assert result.output == "ok"


def test_tool_result_failure() -> None:
    """ToolResult خطا معتبر ساخته می‌شود."""
    result = ToolResult(success=False, error="failed")
    assert result.success is False
    assert result.error == "failed"


def test_tool_registry_register_and_get() -> None:
    """ثبت و بازیابی ابزار."""
    registry = ToolRegistry()
    tool = FilesystemTool()
    registry.register(tool)

    assert registry.get("filesystem") is tool
    assert "filesystem" in registry.list_tools()


def test_tool_registry_execute() -> None:
    """اجرای ابزار از طریق Registry."""
    registry = ToolRegistry()
    registry.register(FilesystemTool())

    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FilesystemTool(workspace=tmpdir)
        registry.register(tool)

        result = registry.execute("filesystem", action="write", path="test.txt", content="hello")
        assert result.success is True

        result = registry.execute("filesystem", action="read", path="test.txt")
        assert result.success is True
        assert result.output == "hello"


def test_tool_registry_execute_unknown() -> None:
    """اجرای ابزار ناشناخته."""
    registry = ToolRegistry()
    result = registry.execute("nonexistent")
    assert result.success is False


def test_tool_registry_list_by_permission() -> None:
    """فیلتر ابزارها بر اساس مجوز."""
    registry = ToolRegistry()
    registry.register(FilesystemTool())
    registry.register(ShellTool())

    file_tools = registry.list_by_permission(ToolPermission.READ_FILE)
    assert "filesystem" in file_tools

    exec_tools = registry.list_by_permission(ToolPermission.EXECUTE_COMMAND)
    assert "shell" in exec_tools


def test_filesystem_read_write() -> None:
    """خواندن و نوشتن فایل."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FilesystemTool(workspace=tmpdir)

        result = tool.execute(action="write", path="test.txt", content="سلام دنیا")
        assert result.success is True

        result = tool.execute(action="read", path="test.txt")
        assert result.success is True
        assert result.output == "سلام دنیا"


def test_filesystem_path_traversal_blocked() -> None:
    """جلوگیری از Path Traversal."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FilesystemTool(workspace=tmpdir)
        result = tool.execute(action="read", path="../../../etc/passwd")
        assert result.success is False
        assert "خارج از Workspace" in result.error


def test_filesystem_search() -> None:
    """جستجو در فایل‌ها."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FilesystemTool(workspace=tmpdir)
        tool.execute(action="write", path="a.txt", content="hello world")
        tool.execute(action="write", path="b.txt", content="foo bar")

        result = tool.execute(action="search", pattern="hello")
        assert result.success is True
        assert "hello world" in result.output


def test_shell_validate_blocks_dangerous() -> None:
    """جلوگیری از فرمان‌های خطرناک."""
    tool = ShellTool()
    assert tool.validate(command="sudo rm -rf /") is False
    assert tool.validate(command="git push") is False


def test_shell_execute() -> None:
    """اجرای فرمان ایمن."""
    tool = ShellTool()
    result = tool.execute(command="echo hello")
    assert result.success is True
    assert "hello" in result.output


def test_default_registry_has_tools() -> None:
    """Registry پیش‌فرض ابزارهای استاندارد دارد."""
    registry = create_default_registry()
    tools = registry.list_tools()
    assert "filesystem" in tools
    assert "shell" in tools
    assert "git" in tools
    assert "test" in tools


def test_tool_to_schema() -> None:
    """تبدیل ابزار به Schema."""
    tool = FilesystemTool()
    schema = tool.to_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "filesystem"


def test_tool_registry_schemas() -> None:
    """لیست Schema تمام ابزارها."""
    registry = ToolRegistry()
    registry.register(FilesystemTool())
    registry.register(ShellTool())

    schemas = registry.list_schemas()
    assert len(schemas) == 2
    names = [s["function"]["name"] for s in schemas]
    assert "filesystem" in names
    assert "shell" in names
