"""Token estimation utilities for tracking message context size."""

import json
from typing import Any, Dict, List, Union

from ..types.content import ContentBlock, Message


def estimate_message_tokens(messages: List[Message]) -> int:
    """Estimate token count for a list of messages.

    This is a lightweight approximation that doesn't call external APIs.
    Uses character-based estimation as a proxy for tokens.

    Estimation method:
    - Roughly 4 characters per token (based on GPT tokenization averages)
    - Includes overhead for message structure
    - Accounts for role, content blocks, and metadata

    Args:
        messages: List of message dictionaries containing role and content.

    Returns:
        Estimated token count for the messages.
    """
    if not messages:
        return 0

    total_chars = 0

    for message in messages:
        # Role tokens (user/assistant/system)
        role = message.get("role", "")
        total_chars += len(role) + 2  # Role + formatting overhead

        # Content blocks
        content = message.get("content", [])
        if isinstance(content, list):
            for block in content:
                total_chars += _estimate_content_block_chars(block)

        # Message overhead (delimiters, formatting)
        total_chars += 4

    # Convert characters to approximate token count
    # Using 4 chars per token as a common approximation
    estimated_tokens = total_chars // 4

    return estimated_tokens


def _estimate_content_block_chars(block: Union[ContentBlock, Dict[str, Any]]) -> int:
    """Estimate character count for a single content block.

    Args:
        block: Content block dictionary (text, image, toolUse, toolResult, etc.)

    Returns:
        Estimated character count for the block.
    """
    chars = 0

    if "text" in block:
        chars += len(block["text"])

    elif "image" in block:
        # Image blocks are much smaller in token count than actual image data
        # The image itself is not tokenized, only the reference
        chars += 100  # Fixed overhead for image reference

    elif "toolUse" in block:
        tool_use = block["toolUse"]
        # Tool name
        chars += len(tool_use.get("name", ""))
        # Tool input as JSON string
        tool_input: Any = tool_use.get("input", {})
        chars += len(json.dumps(tool_input))
        # ToolUseId
        chars += len(tool_use.get("toolUseId", ""))

    elif "toolResult" in block:
        tool_result = block["toolResult"]
        # ToolUseId
        chars += len(tool_result.get("toolUseId", ""))
        # Result content
        result_content = tool_result.get("content", [])
        if isinstance(result_content, list):
            for result_block in result_content:
                # Cast to dict for recursive call since ToolResultContent has different structure
                chars += _estimate_content_block_chars(result_block)  # type: ignore[arg-type]
        # Status
        chars += len(tool_result.get("status", ""))

    elif "document" in block:
        # Document blocks have format and source metadata
        document = block["document"]
        chars += len(document.get("format", ""))
        chars += len(document.get("name", ""))
        # Source can be bytes or reference
        source = document.get("source", {})
        if "bytes" in source:
            # For document bytes, use a reduced estimate since we don't tokenize the entire document
            chars += 500  # Fixed overhead
        else:
            chars += 100  # Reference overhead

    elif "guardContent" in block:
        # Guardrail content placeholder
        guard_content = block["guardContent"]
        for _key, value in guard_content.items():
            chars += len(json.dumps(value))

    # Block overhead (structure, formatting)
    chars += 4

    return chars
