"""MCP Tool Adapter — converts Tool Registry tools to MCP format."""

from __future__ import annotations

import json
from typing import Any


class MCPToolAdapter:
    """Adapts internal tools to MCP-compatible format.

    Based on the Model Context Protocol standard:
    - Each tool has a name, description, and JSON Schema input
    - Tools return structured JSON results
    - Supports tool discovery and invocation
    """

    @staticmethod
    def tool_to_mcp(tool: Any) -> dict:
        """Convert a Tool Registry tool to MCP tool format."""
        schema = {}
        if hasattr(tool, "input_schema"):
            schema = tool.input_schema
        elif hasattr(tool, "schema"):
            schema = tool.schema

        return {
            "name": getattr(tool, "name", "unknown"),
            "description": getattr(tool, "description", ""),
            "inputSchema": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", []),
            },
        }

    @staticmethod
    def tools_to_mcp_list(tools: list) -> list[dict]:
        """Convert a list of tools to MCP list format."""
        return [MCPToolAdapter.tool_to_mcp(t) for t in tools]

    @staticmethod
    def mcp_result(content: Any, is_error: bool = False) -> dict:
        """Wrap a tool result in MCP response format."""
        if isinstance(content, str):
            text = content
        else:
            text = json.dumps(content, ensure_ascii=False, default=str)

        return {
            "content": [{"type": "text", "text": text}],
            "isError": is_error,
        }

    @staticmethod
    def parse_mcp_call(call: dict) -> tuple[str, dict]:
        """Parse an MCP tool call into (tool_name, arguments)."""
        return call.get("name", ""), call.get("arguments", {})
