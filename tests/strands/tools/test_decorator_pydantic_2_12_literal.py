"""Tests for @tool decorator with Literal types and Pydantic 2.12+ compatibility.

This test module specifically addresses issue #1208 where Pydantic 2.12+ requires forward
references to be resolved when using Literal types with `from __future__ import annotations`.
"""

from __future__ import annotations

from typing import Literal

from strands import tool

# Module-level type aliases (typical usage pattern that triggers the issue)
ClickType = Literal["left", "right", "middle"]


def test_tool_with_literal_type_and_future_annotations():
    """Test that @tool works with Literal types when using __future__ annotations.

    This specifically tests the fix for issue #1208 where Pydantic 2.12+ would fail
    with: "PydanticUserError: `Tool` is not fully defined; you should define `ClickType`"
    """

    @tool
    def click_tool(click_type: ClickType, x: int, y: int) -> dict:
        """
        Click at a specific location.

        Args:
            click_type: Type of click to perform
            x: X coordinate
            y: Y coordinate

        Returns:
            Result of the click operation
        """
        return {
            "status": "success",
            "content": [{"text": f"Clicked {click_type} at ({x}, {y})"}],
        }

    # Verify tool spec is generated correctly
    tool_spec = click_tool.tool_spec
    assert tool_spec["name"] == "click_tool"
    assert "Click at a specific location" in tool_spec["description"]

    # Verify input schema contains Literal enum values
    input_schema = tool_spec["inputSchema"]["json"]
    assert "click_type" in input_schema["properties"]
    click_type_schema = input_schema["properties"]["click_type"]
    assert click_type_schema["type"] == "string"
    assert set(click_type_schema["enum"]) == {"left", "right", "middle"}

    # Verify tool can be called directly
    result = click_tool(click_type="left", x=100, y=200)
    assert result["status"] == "success"
    assert "Clicked left at (100, 200)" in result["content"][0]["text"]
