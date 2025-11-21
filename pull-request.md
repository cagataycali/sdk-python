## Description

Fixed a ValidationException that occurred when using SummarizingConversationManager with structured_output_model during context window overflow. The issue was caused by structured output tool use blocks being included in user messages, which violates AWS Bedrock's Converse API rules.

**Root Cause:**
When an agent with `structured_output_model` configured triggers summarization due to context window overflow, the assistant's response includes a `toolUse` block for the structured output. The `_generate_summary` method was converting this response (including the toolUse) directly to a user message, violating the Bedrock rule that user messages cannot contain toolUse blocks.

**Solution:**
1. Temporarily disable `_default_structured_output_model` when using the parent agent for summarization
2. Filter out all `toolUse` blocks from the summary message content before converting to a user message
3. Use `getattr` with defaults to handle both real agents and mock agents safely
4. Restore the original structured output configuration after summarization

**Changes:**
- Modified `SummarizingConversationManager._generate_summary()` to:
  - Save and restore the agent's `_default_structured_output_model` attribute
  - Temporarily set it to `None` when summarizing (only when using parent agent)
  - Filter out toolUse blocks from the summary message content
  - Provide a fallback text message if all content is filtered out

## Related Issues

#1160

## Documentation PR

No documentation changes required

## Type of Change

Bug fix

## Testing

**Testing Approach:**
1. Added two comprehensive unit tests that specifically verify the fix:
   - `test_generate_summary_filters_structured_output_tool_use`: Tests that toolUse blocks from structured output are filtered out
   - `test_generate_summary_filters_all_tool_use_blocks`: Tests the fallback behavior when all content is toolUse blocks

2. Verified all existing tests still pass - no regressions introduced

3. Ran complete test suite:
   ```bash
   # Unit tests
   hatch test tests/strands/agent/test_summarizing_conversation_manager.py
   # Result: 32 passed, 12 warnings

   # Full test suite
   hatch run prepare
   # Result: All checks passed (1529 tests passed across Python 3.10, 3.11, 3.12, 3.13)
   ```

**Test Coverage:**
- Tests verify that structured output tools are properly filtered from summary messages
- Tests verify fallback behavior for edge cases
- Tests verify compatibility with mock agents (no regression in existing tests)
- All Python versions tested (3.10, 3.11, 3.12, 3.13)

**No warnings introduced** in consuming repositories (verified by running full test suite).

- [x] I ran `hatch run prepare`

## Checklist
- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
