"""Integration test for dynamic header generation in MCP HTTP transports."""

import threading
import time

import pytest
from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client

from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient, create_http_transport_with_dynamic_headers


def start_mcp_http_server(port=8003):
    """Start a simple MCP HTTP server for testing."""
    from mcp.server import FastMCP

    mcp = FastMCP("Dynamic Headers Test Server", port=port)

    @mcp.tool(description="Echo tool for testing")
    def echo(message: str) -> str:
        return f"Echo: {message}"

    mcp.run(transport="streamable-http")


@pytest.mark.skipif(
    condition=True,
    reason="Manual integration test - requires running HTTP server",
)
def test_dynamic_headers_with_http_transport():
    """Integration test demonstrating dynamic header generation with HTTP transport."""
    # Start test server in background
    server_thread = threading.Thread(
        target=start_mcp_http_server,
        kwargs={"port": 8003},
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)  # Wait for server startup

    # Track token generation
    call_count = [0]

    def get_auth_token():
        """Simulate fetching a token from an auth service."""
        call_count[0] += 1
        return f"token-{call_count[0]}"

    # Create transport with dynamic headers
    def header_generator(context):
        """Generate headers with dynamic auth token."""
        return {
            "Authorization": f"Bearer {get_auth_token()}",
            "X-User-ID": context.get("user_id", "unknown"),
            "X-Request-Type": "mcp-tools",
        }

    transport_fn = create_http_transport_with_dynamic_headers(
        base_transport_fn=lambda headers: streamablehttp_client(
            url="http://127.0.0.1:8003/mcp",
            headers=headers,
        ),
        header_generator=header_generator,
        context={"user_id": "test-user-123"},
    )

    # Use with MCPClient and Agent
    client = MCPClient(transport_fn)
    with client:
        tools = client.list_tools_sync()
        assert len(tools) >= 1
        assert any(tool.tool_name == "echo" for tool in tools)

        # Verify headers were generated
        assert call_count[0] >= 1

        # Use with agent
        agent = Agent(tools=tools)
        result = agent("Echo 'Hello Dynamic Headers!'")

        # Verify the echo tool was called
        assert "Hello Dynamic Headers!" in str(result)


def test_dynamic_headers_with_stdio_transport_compatibility():
    """Verify that create_http_transport_with_dynamic_headers doesn't break stdio transport."""
    # stdio transport doesn't use headers, but we should be able to wrap it
    # This tests that the pattern is flexible

    # Create a simple wrapper that ignores headers (like stdio does)
    def stdio_wrapper(headers=None):
        # Headers are ignored for stdio transport
        return stdio_client(
            StdioServerParameters(
                command="python",
                args=["tests_integ/mcp/echo_server.py"],
            )
        )

    def header_generator(context):
        # This won't be used with stdio, but shouldn't cause errors
        return {"X-Unused-Header": "value"}

    transport_fn = create_http_transport_with_dynamic_headers(
        base_transport_fn=stdio_wrapper,
        header_generator=header_generator,
    )

    # Should work without errors even though headers are ignored
    client = MCPClient(transport_fn)
    with client:
        tools = client.list_tools_sync()
        assert len(tools) >= 1
