## Description
This PR adds support for Amazon Bedrock system tools, specifically enabling web grounding capabilities for models like Amazon Nova.

**Changes Made:**
- Added `system_tools` parameter to `BedrockConfig` TypedDict to accept a list of system tool names
- Modified `_format_request` method to include system tools in the `toolConfig` of Bedrock API requests
- System tools are added alongside regular tool specs in the tools array
- Properly handles None values in system_tools configuration using safe iteration

**Implementation Details:**
- System tools follow the Bedrock API format: `{"systemTool": {"name": "toolName"}}`
- Supports multiple system tools (e.g., `["webGrounding", "futureSystemTool"]`)
- System tools can be configured independently or combined with regular tool specs
- The `toolConfig` is created when either `tool_specs` OR `system_tools` is provided

## Related Issues
#1154

## Documentation PR
No documentation changes required

## Type of Change
New feature

## Testing
This change was tested with comprehensive unit tests covering:
- System tools alone
- System tools combined with regular tool specs  
- Multiple system tools
- Proper None handling and empty list cases

All tests pass with no new warnings:
- ✅ Unit tests: `hatch test` (1530 passed across Python 3.10, 3.11, 3.12, 3.13)
- ✅ Linting: `hatch fmt --linter` (ruff + mypy)
- ✅ Formatting: `hatch fmt --formatter`
- ✅ Full preparation: `hatch run prepare`

Verified that the changes do not break functionality in consuming repositories (no imports from agents-docs, agents-tools, agents-cli affected).

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
