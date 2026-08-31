"""MCP Server — exposes Tool Registry tools via Model Context Protocol."""

from __future__ import annotations

import json
from typing import Any, Callable

from core.mcp.tool_adapter import MCPToolAdapter


class MCPServer:
    """Lightweight MCP server that wraps the Tool Registry.

    Usage:
        server = MCPServer(tool_registry)
        # List tools
        tools = server.list_tools()
        # Call a tool
        result = server.call_tool("filesystem", {"action": "read", "path": "foo.py"})
    """

    def __init__(self, tool_registry: Any = None) -> None:
        self._registry = tool_registry
        self._custom_tools: dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable, description: str = "") -> None:
        """Register a custom tool directly with the MCP server."""
        self._custom_tools[name] = {"func": func, "description": description}

    def list_tools(self) -> list[dict]:
        """List all available tools in MCP format."""
        tools = []

        # Tools from registry
        if self._registry and hasattr(self._registry, "list_tools"):
            for tool in self._registry.list_tools():
                tools.append(MCPToolAdapter.tool_to_mcp(tool))

        # Custom tools
        for name, info in self._custom_tools.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "inputSchema": {"type": "object", "properties": {}},
            })

        return tools

    def call_tool(self, name: str, arguments: dict) -> dict:
        """Call a tool by name with arguments. Returns MCP-formatted result."""
        # Try registry first
        if self._registry and hasattr(self._registry, "get_tool"):
            tool = self._registry.get_tool(name)
            if tool and hasattr(tool, "execute"):
                try:
                    result = tool.execute(**arguments)
                    return MCPToolAdapter.mcp_result(result)
                except Exception as e:
                    return MCPToolAdapter.mcp_result(str(e), is_error=True)

        # Try custom tools
        if name in self._custom_tools:
            try:
                result = self._custom_tools[name]["func"](**arguments)
                return MCPToolAdapter.mcp_result(result)
            except Exception as e:
                return MCPToolAdapter.mcp_result(str(e), is_error=True)

        return MCPToolAdapter.mcp_result(f"Tool '{name}' not found", is_error=True)

    def handle_request(self, request: dict) -> dict:
        """Handle an MCP JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "tools/list":
            result = self.list_tools()
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = self.call_tool(tool_name, arguments)
        elif method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "ai-agent-manager", "version": "1.0.0"},
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
            }

        return {"jsonrpc": "2.0", "id": req_id, "result": result}
