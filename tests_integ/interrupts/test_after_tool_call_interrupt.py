"""Test interrupts from AfterToolCallEvent.

This test verifies the use case described in issue #1165:
raising an interrupt from an AfterToolCallEvent in response to a failure,
letting an external execution manager analyze the result and potentially
getting a human in the loop to resume at a later time.
"""

import json

import pytest

from strands import Agent, tool
from strands.hooks import AfterToolCallEvent, HookProvider


@pytest.fixture
def after_tool_interrupt_hook():
    """Hook that interrupts after tool calls based on result status."""

    class Hook(HookProvider):
        def register_hooks(self, registry):
            registry.add_callback(AfterToolCallEvent, self.check_result)

        def check_result(self, event: AfterToolCallEvent):
            # Only interrupt on error status
            if event.result.get("status") == "error":
                response = event.interrupt(
                    "tool_failure_review",
                    reason=f"Tool {event.tool_use['name']} failed, human review required",
                )
                # If human approves retry, we could modify the result here
                if response == "RETRY":
                    # Modify result to indicate retry approved
                    event.result["content"] = [{"text": f"Retry approved for {event.tool_use['name']}"}]
                elif response == "SKIP":
                    # Keep the error but mark as reviewed
                    event.result["content"] = [{"text": f"Error acknowledged, skipping {event.tool_use['name']}"}]

    return Hook()


@pytest.fixture
def failing_tool():
    """Tool that always fails."""

    @tool(name="failing_tool")
    def func():
        raise Exception("Tool execution failed")

    return func


@pytest.fixture
def success_tool():
    """Tool that always succeeds."""

    @tool(name="success_tool")
    def func():
        return "success"

    return func


@pytest.fixture
def agent_with_after_interrupt(after_tool_interrupt_hook, failing_tool, success_tool):
    """Agent configured with AfterToolCallEvent interrupt hook."""
    return Agent(hooks=[after_tool_interrupt_hook], tools=[failing_tool, success_tool])


def test_after_tool_call_interrupt_on_failure(agent_with_after_interrupt):
    """Test that interrupt is raised after a tool failure."""
    result = agent_with_after_interrupt("Call the failing_tool")

    # Should stop with interrupt
    assert result.stop_reason == "interrupt"

    # Should have one interrupt for the failure
    assert len(result.interrupts) == 1
    interrupt = result.interrupts[0]

    assert interrupt.name == "tool_failure_review"
    assert "failed" in interrupt.reason.lower()
    assert "human review" in interrupt.reason.lower()


def test_after_tool_call_interrupt_retry_response(agent_with_after_interrupt):
    """Test resuming from interrupt with RETRY response."""
    result = agent_with_after_interrupt("Call the failing_tool")

    assert result.stop_reason == "interrupt"
    interrupt = result.interrupts[0]

    # Resume with RETRY response
    responses = [
        {
            "interruptResponse": {
                "interruptId": interrupt.id,
                "response": "RETRY",
            },
        },
    ]
    result = agent_with_after_interrupt(responses)

    # Should complete after retry approval
    assert result.stop_reason == "end_turn"

    # Check that the tool result was modified to indicate retry
    tool_result_message = agent_with_after_interrupt.messages[-2]
    assert tool_result_message["role"] == "user"
    content = tool_result_message["content"][0]["toolResult"]["content"][0]["text"]
    assert "Retry approved" in content


def test_after_tool_call_interrupt_skip_response(agent_with_after_interrupt):
    """Test resuming from interrupt with SKIP response."""
    result = agent_with_after_interrupt("Call the failing_tool")

    assert result.stop_reason == "interrupt"
    interrupt = result.interrupts[0]

    # Resume with SKIP response
    responses = [
        {
            "interruptResponse": {
                "interruptId": interrupt.id,
                "response": "SKIP",
            },
        },
    ]
    result = agent_with_after_interrupt(responses)

    # Should complete after skip
    assert result.stop_reason == "end_turn"

    # Check that the tool result indicates skip
    tool_result_message = agent_with_after_interrupt.messages[-2]
    assert tool_result_message["role"] == "user"
    content = tool_result_message["content"][0]["toolResult"]["content"][0]["text"]
    assert "Error acknowledged" in content
    assert "skipping" in content


def test_after_tool_call_no_interrupt_on_success(agent_with_after_interrupt):
    """Test that no interrupt is raised for successful tool calls."""
    result = agent_with_after_interrupt("Call the success_tool")

    # Should complete without interrupt
    assert result.stop_reason == "end_turn"
    assert not result.interrupts or len(result.interrupts) == 0

    # Verify success result
    result_message = json.dumps(result.message).lower()
    assert "success" in result_message


def test_after_tool_call_interrupt_multiple_tools(agent_with_after_interrupt):
    """Test interrupts with multiple tool calls."""
    result = agent_with_after_interrupt("Call both failing_tool and success_tool")

    # Should stop on first failure
    assert result.stop_reason == "interrupt"
    assert len(result.interrupts) == 1

    interrupt = result.interrupts[0]

    # Resume with SKIP
    responses = [
        {
            "interruptResponse": {
                "interruptId": interrupt.id,
                "response": "SKIP",
            },
        },
    ]
    result = agent_with_after_interrupt(responses)

    # Should complete after handling the failure
    assert result.stop_reason == "end_turn"

    # Check both tools were called
    tool_result_message = agent_with_after_interrupt.messages[-2]
    assert len(tool_result_message["content"]) == 2  # Two tool results
