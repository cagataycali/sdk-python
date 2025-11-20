"""Test script to reproduce issue #1210: Direct tool calls with context=True cause KeyError"""

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


def main():
    """Test direct tool call with context=True"""
    agent = Agent(tools=[add_w_state])
    
    print("Testing direct tool call with context=True...")
    try:
        agent.tool.add_w_state(a=1, b=1)
        print("✓ Direct tool call succeeded!")
        print("\nAgent messages:")
        for msg in agent.messages:
            print(f"  {msg}")
    except Exception as e:
        print(f"✗ Direct tool call failed with error: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
