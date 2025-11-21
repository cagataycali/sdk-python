## Description

Added three convenience methods to the `AgentResult` class to make tool execution information easily accessible without requiring users to navigate the nested metrics structure:

1. **`get_tool_executions()`** - Returns a list of dictionaries containing comprehensive tool execution details including name, tool_use_id, inputs, call counts, success/error counts, and total execution time.

2. **`get_tool_inputs()`** - A simpler alternative that returns just a dictionary mapping tool names to their input parameters.

3. **`get_executed_code()`** - Convenience method specifically for the code_interpreter tool, providing direct access to executed Python code.

These methods address the issue where tool execution content (e.g., executed code) is stored in `result.metrics.tool_metrics` but not easily accessible, requiring users to implement custom extraction logic. The new methods follow the SDK's development tenets: simple at any scale, extensible by design, and making the obvious path the happy path.

## Related Issues

#1156

## Documentation PR

No documentation changes required

## Type of Change

New feature

## Testing

Added comprehensive unit tests for all three new methods covering:
- Normal operation with tool execution data
- Empty metrics (no tools executed)
- Edge cases (malformed data, missing tools)
- Multiple tools with different structures
- All tests pass successfully with mypy type checking

Verified that changes don't break functionality in consuming repositories (agents-docs, agents-tools, agents-cli) by running full test suite.

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
