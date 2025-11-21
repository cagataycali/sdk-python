"""Tests for token estimation utilities."""

from strands.telemetry.token_estimator import _estimate_content_block_chars, estimate_message_tokens


def test_estimate_message_tokens_empty():
    """Test with empty messages list"""
    messages = []
    result = estimate_message_tokens(messages)
    assert result == 0


def test_estimate_message_tokens_simple_text():
    """Test with simple text messages"""
    messages = [
        {"role": "user", "content": [{"text": "Hello world"}]},
        {"role": "assistant", "content": [{"text": "Hi there"}]},
    ]
    result = estimate_message_tokens(messages)
    # Rough estimate: (~11 chars + ~8 chars + overhead) / 4
    assert result > 0


def test_estimate_message_tokens_with_tool_use():
    """Test with tool use content"""
    messages = [
        {
            "role": "user",
            "content": [{"text": "Calculate 2+2"}],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "toolUse": {
                        "name": "calculator",
                        "toolUseId": "tool_123",
                        "input": {"expression": "2+2"},
                    }
                }
            ],
        },
    ]
    result = estimate_message_tokens(messages)
    assert result > 0


def test_estimate_message_tokens_with_tool_result():
    """Test with tool result content"""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": "tool_123",
                        "content": [{"text": "4"}],
                        "status": "success",
                    }
                }
            ],
        }
    ]
    result = estimate_message_tokens(messages)
    assert result > 0


def test_estimate_content_block_chars_text():
    """Test character estimation for text block"""
    block = {"text": "Hello world"}
    result = _estimate_content_block_chars(block)
    # 11 chars for text + 4 for overhead
    assert result == 15


def test_estimate_content_block_chars_image():
    """Test character estimation for image block"""
    block = {
        "image": {
            "format": "png",
            "source": {"bytes": b"fake_image_data"},
        }
    }
    result = _estimate_content_block_chars(block)
    # Fixed overhead for image reference
    assert result == 104


def test_estimate_content_block_chars_tool_use():
    """Test character estimation for toolUse block"""
    block = {
        "toolUse": {
            "name": "calculator",
            "toolUseId": "tool_123",
            "input": {"x": 1, "y": 2},
        }
    }
    result = _estimate_content_block_chars(block)
    assert result > 0


def test_estimate_content_block_chars_tool_result():
    """Test character estimation for toolResult block"""
    block = {
        "toolResult": {
            "toolUseId": "tool_123",
            "content": [{"text": "Result text"}],
            "status": "success",
        }
    }
    result = _estimate_content_block_chars(block)
    assert result > 0


def test_estimate_content_block_chars_document():
    """Test character estimation for document block"""
    block = {
        "document": {
            "format": "pdf",
            "name": "document.pdf",
            "source": {"bytes": b"fake_pdf_data"},
        }
    }
    result = _estimate_content_block_chars(block)
    # format + name + fixed overhead for bytes
    assert result > 0


def test_estimate_content_block_chars_guard_content():
    """Test character estimation for guardContent block"""
    block = {
        "guardContent": {
            "intervention": "Content blocked",
            "reason": "Policy violation",
        }
    }
    result = _estimate_content_block_chars(block)
    assert result > 0


def test_estimate_message_tokens_legacy_string_content():
    """Test with legacy string content format"""
    messages = [
        {"role": "user", "content": "Hello world"},
    ]
    # Should handle string content gracefully
    result = estimate_message_tokens(messages)
    assert result > 0


def test_estimate_message_tokens_multiple_blocks():
    """Test with multiple content blocks in a message"""
    messages = [
        {
            "role": "user",
            "content": [
                {"text": "First block"},
                {"text": "Second block"},
                {"text": "Third block"},
            ],
        }
    ]
    result = estimate_message_tokens(messages)
    assert result > 0


def test_estimate_message_tokens_realistic_conversation():
    """Test with a realistic conversation"""
    messages = [
        {"role": "user", "content": [{"text": "What is the weather like today?"}]},
        {"role": "assistant", "content": [{"text": "I don't have access to real-time weather data."}]},
        {"role": "user", "content": [{"text": "Can you tell me a joke?"}]},
        {
            "role": "assistant",
            "content": [{"text": "Why did the programmer quit his job? Because he didn't get arrays."}],
        },
    ]
    result = estimate_message_tokens(messages)
    # Should be roughly proportional to total character count / 4
    assert result > 20
