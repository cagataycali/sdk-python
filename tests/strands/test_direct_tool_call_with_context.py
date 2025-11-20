"""Test for direct tool calls with context=True (issue #1210)."""

from strands import Agent, ToolContext, tool


@tool(context=True)
def add_w_state(a: int, b: int, tool_context: ToolContext) -> int:
    """Add two numbers and store result in agent state.

    Args:
        a: First number
        b: Second number
        tool_context: The tool context with agent access

    Returns:
        The sum of a and b
    """
    result = a + b
    tool_context.agent.state.set("last_add_result", result)
    return result


def test_direct_tool_call_with_context():
    """Test that direct tool calls work with context=True tools."""
    agent = Agent(tools=[add_w_state])

    # Call the tool directly
    tool_result = agent.tool.add_w_state(a=5, b=3)

    # Verify the tool result is successful
    assert tool_result["status"] == "success"
    assert tool_result["content"][0]["text"] == "8"

    # Verify the state was updated
    assert agent.state.get("last_add_result") == 8


def test_direct_tool_call_with_context_custom_name():
    """Test that direct tool calls work with context=True and custom context parameter name."""

    @tool(context="my_ctx")
    def multiply_w_state(x: int, y: int, my_ctx: ToolContext) -> int:
        """Multiply two numbers and store in state.

        Args:
            x: First number
            y: Second number
            my_ctx: Custom context parameter

        Returns:
            Product of x and y
        """
        result = x * y
        my_ctx.agent.state.set("last_multiply_result", result)
        return result

    agent = Agent(tools=[multiply_w_state])

    # Call the tool directly
    tool_result = agent.tool.multiply_w_state(x=4, y=7)

    # Verify the tool result is successful
    assert tool_result["status"] == "success"
    assert tool_result["content"][0]["text"] == "28"

    # Verify the state was updated
    assert agent.state.get("last_multiply_result") == 28
