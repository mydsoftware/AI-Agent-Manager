"""Model Context Protocol (MCP) adapter for AI-Agent-Manager.

Enables the Tool Registry to expose tools via the MCP standard,
making them usable by any MCP-compatible client (Claude, Cursor, etc.).
"""

from core.mcp.server import MCPServer
from core.mcp.tool_adapter import MCPToolAdapter

__all__ = ["MCPServer", "MCPToolAdapter"]
