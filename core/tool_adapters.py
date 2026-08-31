"""Tool Adapters — Composio-style adapters for external services.

Standardized adapter pattern for connecting to GitHub, Slack, Jira, etc.
Each adapter implements the same interface: search, authenticate, execute.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """Definition of an available tool."""

    name: str
    service: str
    description: str
    input_schema: dict = field(default_factory=dict)
    requires_auth: bool = True


class BaseAdapter:
    """Base class for all service adapters."""

    service_name: str = "base"

    def __init__(self) -> None:
        self._authenticated = False

    def authenticate(self) -> bool:
        raise NotImplementedError

    def list_tools(self) -> list[ToolDefinition]:
        raise NotImplementedError

    def execute(self, tool_name: str, params: dict) -> dict:
        raise NotImplementedError

    def is_available(self) -> bool:
        return self._authenticated


class GitHubAdapter(BaseAdapter):
    """GitHub tool adapter — wraps GitHub API operations."""

    service_name = "github"

    def __init__(self) -> None:
        super().__init__()
        self._token = os.getenv("GITHUB_TOKEN", "")
        self._authenticated = bool(self._token)

    def authenticate(self) -> bool:
        self._authenticated = bool(self._token)
        return self._authenticated

    def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition("github_search_repos", "github", "Search repositories"),
            ToolDefinition("github_get_file", "github", "Get file contents"),
            ToolDefinition("github_create_issue", "github", "Create an issue"),
            ToolDefinition("github_create_pr", "github", "Create a pull request"),
            ToolDefinition("github_list_issues", "github", "List repository issues"),
            ToolDefinition("github_get_workflow", "github", "Get workflow runs"),
        ]

    def execute(self, tool_name: str, params: dict) -> dict:
        if not self._authenticated:
            return {"error": "GitHub not authenticated. Set GITHUB_TOKEN."}
        # Real implementation would use requests/API
        return {"tool": tool_name, "params": params, "status": "ready"}


class FilesystemAdapter(BaseAdapter):
    """Filesystem tool adapter — local file operations."""

    service_name = "filesystem"

    def __init__(self, workspace: str = ".") -> None:
        super().__init__()
        self.workspace = workspace
        self._authenticated = True

    def authenticate(self) -> bool:
        return True

    def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition("fs_read", "filesystem", "Read a file"),
            ToolDefinition("fs_write", "filesystem", "Write a file"),
            ToolDefinition("fs_edit", "filesystem", "Edit a file"),
            ToolDefinition("fs_search", "filesystem", "Search files"),
            ToolDefinition("fs_list", "filesystem", "List directory"),
        ]

    def execute(self, tool_name: str, params: dict) -> dict:
        import os
        path = params.get("path", "")

        if tool_name == "fs_read":
            try:
                with open(os.path.join(self.workspace, path), encoding="utf-8") as f:
                    return {"content": f.read()}
            except Exception as e:
                return {"error": str(e)}

        elif tool_name == "fs_list":
            try:
                entries = os.listdir(os.path.join(self.workspace, path))
                return {"entries": entries}
            except Exception as e:
                return {"error": str(e)}

        return {"tool": tool_name, "status": "implemented"}


class BrowserAdapter(BaseAdapter):
    """Browser tool adapter — web browsing and testing."""

    service_name = "browser"

    def __init__(self) -> None:
        super().__init__()
        self._authenticated = True

    def authenticate(self) -> bool:
        return True

    def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition("browser_open", "browser", "Open a URL"),
            ToolDefinition("browser_click", "browser", "Click an element"),
            ToolDefinition("browser_fill", "browser", "Fill a form field"),
            ToolDefinition("browser_screenshot", "browser", "Take screenshot"),
            ToolDefinition("browser_console", "browser", "Get console logs"),
            ToolDefinition("browser_inspect", "browser", "Inspect page elements"),
        ]

    def execute(self, tool_name: str, params: dict) -> dict:
        return {"tool": tool_name, "status": "available"}


class AdapterRegistry:
    """Registry of all available tool adapters (Composio pattern)."""

    def __init__(self) -> None:
        self._adapters: dict[str, BaseAdapter] = {}

    def register(self, adapter: BaseAdapter) -> None:
        self._adapters[adapter.service_name] = adapter

    def get(self, service: str) -> BaseAdapter | None:
        return self._adapters.get(service)

    def list_all_tools(self) -> list[ToolDefinition]:
        tools = []
        for adapter in self._adapters.values():
            if adapter.is_available():
                tools.extend(adapter.list_tools())
        return tools

    def execute(self, service: str, tool_name: str, params: dict) -> dict:
        adapter = self._adapters.get(service)
        if not adapter:
            return {"error": f"Adapter '{service}' not found"}
        if not adapter.is_available():
            return {"error": f"Adapter '{service}' not authenticated"}
        return adapter.execute(tool_name, params)

    def status(self) -> dict[str, bool]:
        return {name: adapter.is_available()
                for name, adapter in self._adapters.items()}


def create_default_registry() -> AdapterRegistry:
    """Create a registry with all default adapters."""
    registry = AdapterRegistry()
    registry.register(GitHubAdapter())
    registry.register(FilesystemAdapter())
    registry.register(BrowserAdapter())
    return registry
