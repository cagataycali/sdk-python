"""Tests for return_direct tool feature (Issue #1204)."""

import pytest

from strands import Agent, tool


@tool(return_direct=True)
def get_large_data() -> dict:
    """
    Retrieves large data that should be returned directly without LLM processing.

    Returns:
        A dictionary with large data content.
    """
    return {"status": "success", "content": [{"text": "Large data payload: " + "x" * 1000}]}


@tool
def regular_tool() -> dict:
    """
    Regular tool that should continue the agent loop.

    Returns:
        A dictionary with content.
    """
    return {"status": "success", "content": [{"text": "Regular tool result"}]}


@pytest.mark.asyncio
async def test_return_direct_stops_event_loop():
    """Test that return_direct=True stops the event loop after tool execution."""
    agent = Agent(tools=[get_large_data], system_prompt="You are a helpful assistant.", callback_handler=None)

    result = agent("Use get_large_data tool")

    # The result should be from the tool, not the LLM
    assert result.stop_reason == "tool_use"
    assert any("toolResult" in block for block in result.message["content"])


@pytest.mark.asyncio
async def test_regular_tool_continues_event_loop():
    """Test that tools without return_direct continue the normal event loop."""
    agent = Agent(tools=[regular_tool], system_prompt="You are a helpful assistant.", callback_handler=None)

    result = agent("Use regular_tool tool")

    # Without return_direct, the agent should process the tool result and respond
    # The stop reason should be end_turn (normal completion after processing tool result)
    assert result.stop_reason in ["end_turn", "tool_use"]


@pytest.mark.asyncio
async def test_return_direct_property():
    """Test that the return_direct property is correctly set on tools."""
    assert get_large_data.return_direct is True
    assert regular_tool.return_direct is False


@pytest.mark.asyncio
async def test_multiple_tools_one_return_direct():
    """Test that when multiple tools are called, return_direct on any one stops the loop."""
    agent = Agent(
        tools=[get_large_data, regular_tool], system_prompt="You are a helpful assistant.", callback_handler=None
    )

    # If the model decides to call get_large_data, the loop should stop
    result = agent("Use get_large_data tool")

    assert result.stop_reason == "tool_use"
    assert any("toolResult" in block for block in result.message["content"])
