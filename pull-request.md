## Description

This PR implements the `return_direct` feature for Strands tools, similar to Langchain's functionality. When a tool is decorated with `@tool(return_direct=True)`, its result is returned directly to the user, skipping further LLM processing in the agent loop.

**Key Changes:**
- Added `return_direct` parameter to the `@tool` decorator
- Added `_return_direct` attribute and `return_direct` property to `AgentTool` base class
- Modified event loop to check for `return_direct` flag and stop processing when detected
- Returns the tool_result_message directly instead of the assistant's message

**Use Cases:**
- Retrieving large data that doesn't need LLM processing
- Returning structured data that would be corrupted by the LLM
- Reducing latency by skipping unnecessary LLM calls
- Saving costs by avoiding token usage for pass-through operations

## Related Issues

#1204

## Documentation PR

No documentation changes required

## Type of Change

New feature

## Testing

How have you tested the change? Verify that the changes do not break functionality or introduce warnings in consuming repositories: agents-docs, agents-tools, agents-cli

- [x] I ran `hatch run prepare`
- [x] All unit tests pass (1530 passed)
- [x] All Python versions tested (3.10, 3.11, 3.12, 3.13)
- [x] Integration tests pass (Gemini failures unrelated - API permissions)
- [x] Added comprehensive test suite in `tests/strands/tools/test_return_direct.py`
  - Test that `return_direct=True` stops event loop
  - Test that regular tools continue normal behavior
  - Test that `return_direct` property is accessible
  - Test mixed scenarios with multiple tools

## Checklist

- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
