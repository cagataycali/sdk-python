"""Model Context Protocol (MCP) integration.

This package provides integration with the Model Context Protocol (MCP), allowing agents to use tools provided by MCP
servers.

- Docs: https://www.anthropic.com/news/model-context-protocol
"""

from .mcp_agent_tool import MCPAgentTool
from .mcp_client import MCPClient, ToolFilters, create_http_transport_with_dynamic_headers
from .mcp_types import MCPTransport

__all__ = ["MCPAgentTool", "MCPClient", "MCPTransport", "ToolFilters", "create_http_transport_with_dynamic_headers"]
