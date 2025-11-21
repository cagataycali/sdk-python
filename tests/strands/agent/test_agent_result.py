import unittest.mock
from typing import Optional, cast

import pytest
from pydantic import BaseModel

from strands.agent.agent_result import AgentResult
from strands.telemetry.metrics import EventLoopMetrics
from strands.types.content import Message
from strands.types.streaming import StopReason


@pytest.fixture
def mock_metrics():
    return unittest.mock.Mock(spec=EventLoopMetrics)


@pytest.fixture
def simple_message():
    return {"role": "assistant", "content": [{"text": "Hello world!"}]}


@pytest.fixture
def complex_message():
    return {
        "role": "assistant",
        "content": [
            {"text": "First paragraph"},
            {"text": "Second paragraph"},
            {"non_text_content": "This should be ignored"},
            {"text": "Third paragraph"},
        ],
    }


@pytest.fixture
def empty_message():
    return {"role": "assistant", "content": []}


def test__init__(mock_metrics, simple_message: Message):
    """Test that AgentResult can be properly initialized with all required fields."""
    stop_reason: StopReason = "end_turn"
    state = {"key": "value"}

    result = AgentResult(stop_reason=stop_reason, message=simple_message, metrics=mock_metrics, state=state)

    assert result.stop_reason == stop_reason
    assert result.message == simple_message
    assert result.metrics == mock_metrics
    assert result.state == state
    assert result.structured_output is None


def test__str__simple(mock_metrics, simple_message: Message):
    """Test that str() works with a simple message."""
    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=mock_metrics, state={})

    message_string = str(result)
    assert message_string == "Hello world!\n"


def test__str__complex(mock_metrics, complex_message: Message):
    """Test that str() works with a complex message with multiple text blocks."""
    result = AgentResult(stop_reason="end_turn", message=complex_message, metrics=mock_metrics, state={})

    message_string = str(result)
    assert message_string == "First paragraph\nSecond paragraph\nThird paragraph\n"


def test__str__empty(mock_metrics, empty_message: Message):
    """Test that str() works with an empty message."""
    result = AgentResult(stop_reason="end_turn", message=empty_message, metrics=mock_metrics, state={})

    message_string = str(result)
    assert message_string == ""


def test__str__no_content(mock_metrics):
    """Test that str() works with a message that has no content field."""
    message_without_content = cast(Message, {"role": "assistant"})

    result = AgentResult(stop_reason="end_turn", message=message_without_content, metrics=mock_metrics, state={})

    message_string = str(result)
    assert message_string == ""


def test__str__non_dict_content(mock_metrics):
    """Test that str() handles non-dictionary content items gracefully."""
    message_with_non_dict = cast(
        Message,
        {"role": "assistant", "content": [{"text": "Valid text"}, "Not a dictionary", {"text": "More valid text"}]},
    )

    result = AgentResult(stop_reason="end_turn", message=message_with_non_dict, metrics=mock_metrics, state={})

    message_string = str(result)
    assert message_string == "Valid text\nMore valid text\n"


def test_to_dict(mock_metrics, simple_message: Message):
    """Test that to_dict serializes AgentResult correctly."""
    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=mock_metrics, state={"key": "value"})

    data = result.to_dict()

    assert data == {
        "type": "agent_result",
        "message": simple_message,
        "stop_reason": "end_turn",
    }


def test_from_dict():
    """Test that from_dict works with valid data."""
    data = {
        "type": "agent_result",
        "message": {"role": "assistant", "content": [{"text": "Test response"}]},
        "stop_reason": "end_turn",
    }

    result = AgentResult.from_dict(data)

    assert result.message == data["message"]
    assert result.stop_reason == data["stop_reason"]
    assert isinstance(result.metrics, EventLoopMetrics)
    assert result.state == {}


def test_roundtrip_serialization(mock_metrics, complex_message: Message):
    """Test that to_dict() and from_dict() work together correctly."""
    original = AgentResult(
        stop_reason="max_tokens", message=complex_message, metrics=mock_metrics, state={"test": "data"}
    )

    # Serialize and deserialize
    data = original.to_dict()
    restored = AgentResult.from_dict(data)

    assert restored.message == original.message
    assert restored.stop_reason == original.stop_reason
    assert isinstance(restored.metrics, EventLoopMetrics)
    assert restored.state == {}  # State is not serialized


# Tests for structured output functionality
class StructuredOutputModel(BaseModel):
    """Test model for structured output."""

    name: str
    value: int
    optional_field: Optional[str] = None


def test__init__with_structured_output(mock_metrics, simple_message: Message):
    """Test that AgentResult can be initialized with structured_output."""
    stop_reason: StopReason = "end_turn"
    state = {"key": "value"}
    structured_output = StructuredOutputModel(name="test", value=42)

    result = AgentResult(
        stop_reason=stop_reason,
        message=simple_message,
        metrics=mock_metrics,
        state=state,
        structured_output=structured_output,
    )

    assert result.stop_reason == stop_reason
    assert result.message == simple_message
    assert result.metrics == mock_metrics
    assert result.state == state
    assert result.structured_output == structured_output
    assert isinstance(result.structured_output, StructuredOutputModel)
    assert result.structured_output.name == "test"
    assert result.structured_output.value == 42


def test__init__structured_output_defaults_to_none(mock_metrics, simple_message: Message):
    """Test that structured_output defaults to None when not provided."""
    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=mock_metrics, state={})

    assert result.structured_output is None


def test__str__with_structured_output(mock_metrics, simple_message: Message):
    """Test that str() is not affected by structured_output."""
    structured_output = StructuredOutputModel(name="test", value=42)

    result = AgentResult(
        stop_reason="end_turn",
        message=simple_message,
        metrics=mock_metrics,
        state={},
        structured_output=structured_output,
    )

    # The string representation should only include the message text, not structured output
    message_string = str(result)
    assert message_string == "Hello world!\n"
    assert "test" not in message_string
    assert "42" not in message_string


# Tests for tool execution helper methods
def test_get_tool_executions_with_tools(simple_message: Message):
    """Test that get_tool_executions() returns tool execution details."""
    from strands.telemetry.metrics import EventLoopMetrics, ToolMetrics

    metrics = EventLoopMetrics()
    # Add mock tool metrics
    metrics.tool_metrics["calculator"] = ToolMetrics(
        tool={
            "toolUseId": "tool_123",
            "name": "calculator",
            "input": {"expression": "5 + 3"},
        },
        call_count=1,
        success_count=1,
        error_count=0,
        total_time=0.5,
    )
    metrics.tool_metrics["code_interpreter"] = ToolMetrics(
        tool={
            "toolUseId": "tool_456",
            "name": "code_interpreter",
            "input": {
                "code_interpreter_input": {
                    "action": {
                        "type": "executeCode",
                        "language": "python",
                        "code": "print('hello')",
                    }
                }
            },
        },
        call_count=2,
        success_count=2,
        error_count=0,
        total_time=1.2,
    )

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    executions = result.get_tool_executions()

    assert len(executions) == 2

    # Check calculator execution
    calc_execution = next(e for e in executions if e["name"] == "calculator")
    assert calc_execution["tool_use_id"] == "tool_123"
    assert calc_execution["input"] == {"expression": "5 + 3"}
    assert calc_execution["call_count"] == 1
    assert calc_execution["success_count"] == 1
    assert calc_execution["error_count"] == 0
    assert calc_execution["total_time"] == 0.5

    # Check code_interpreter execution
    ci_execution = next(e for e in executions if e["name"] == "code_interpreter")
    assert ci_execution["tool_use_id"] == "tool_456"
    assert "code_interpreter_input" in ci_execution["input"]
    assert ci_execution["call_count"] == 2
    assert ci_execution["success_count"] == 2


def test_get_tool_executions_empty(simple_message: Message):
    """Test that get_tool_executions() returns empty list when no tools used."""
    metrics = EventLoopMetrics()

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    executions = result.get_tool_executions()

    assert executions == []


def test_get_tool_inputs_with_tools(simple_message: Message):
    """Test that get_tool_inputs() returns tool input parameters."""
    from strands.telemetry.metrics import EventLoopMetrics, ToolMetrics

    metrics = EventLoopMetrics()
    metrics.tool_metrics["calculator"] = ToolMetrics(
        tool={
            "toolUseId": "tool_123",
            "name": "calculator",
            "input": {"expression": "10 * 20"},
        }
    )

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    inputs = result.get_tool_inputs()

    assert len(inputs) == 1
    assert "calculator" in inputs
    assert inputs["calculator"] == {"expression": "10 * 20"}


def test_get_tool_inputs_empty(simple_message: Message):
    """Test that get_tool_inputs() returns empty dict when no tools used."""
    metrics = EventLoopMetrics()

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    inputs = result.get_tool_inputs()

    assert inputs == {}


def test_get_executed_code_with_code(simple_message: Message):
    """Test that get_executed_code() extracts code from code_interpreter tool."""
    from strands.telemetry.metrics import EventLoopMetrics, ToolMetrics

    metrics = EventLoopMetrics()
    test_code = "import numpy as np\nresult = np.mean([1, 2, 3, 4, 5])"
    metrics.tool_metrics["code_interpreter"] = ToolMetrics(
        tool={
            "toolUseId": "tool_789",
            "name": "code_interpreter",
            "input": {
                "code_interpreter_input": {
                    "action": {
                        "type": "executeCode",
                        "language": "python",
                        "code": test_code,
                    }
                }
            },
        }
    )

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    code = result.get_executed_code()

    assert code == test_code


def test_get_executed_code_no_code_interpreter(simple_message: Message):
    """Test that get_executed_code() returns None when code_interpreter not used."""
    from strands.telemetry.metrics import EventLoopMetrics, ToolMetrics

    metrics = EventLoopMetrics()
    # Add different tool, not code_interpreter
    metrics.tool_metrics["calculator"] = ToolMetrics(
        tool={
            "toolUseId": "tool_123",
            "name": "calculator",
            "input": {"expression": "5 + 3"},
        }
    )

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    code = result.get_executed_code()

    assert code is None


def test_get_executed_code_empty_metrics(simple_message: Message):
    """Test that get_executed_code() returns None when no tools used."""
    metrics = EventLoopMetrics()

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    code = result.get_executed_code()

    assert code is None


def test_get_executed_code_malformed_input(simple_message: Message):
    """Test that get_executed_code() handles malformed input gracefully."""
    from strands.telemetry.metrics import EventLoopMetrics, ToolMetrics

    metrics = EventLoopMetrics()
    # Create code_interpreter with malformed input structure
    metrics.tool_metrics["code_interpreter"] = ToolMetrics(
        tool={
            "toolUseId": "tool_999",
            "name": "code_interpreter",
            "input": {"malformed": "structure"},  # Missing expected nested structure
        }
    )

    result = AgentResult(stop_reason="end_turn", message=simple_message, metrics=metrics, state={})

    code = result.get_executed_code()

    # Should return None rather than raising an exception
    assert code is None
