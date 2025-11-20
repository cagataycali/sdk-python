## Description
Fixed issue #1200 where Gemini model was generating duplicate `toolUseId` values when the same tool was called multiple times in a single response. The problem was that `toolUseId` was set to the function name instead of a unique identifier, causing tool calls to be indistinguishable from each other.

**Changes made:**
- Added `_tool_use_id_to_name` mapping to track the relationship between unique IDs and function names
- Added `_tool_use_counter` to generate sequential unique IDs (`tooluse_0`, `tooluse_1`, etc.)
- Modified `_format_chunk` to generate unique `toolUseId` values while preserving the function name
- Updated `_format_request_content_part` to look up function names from the mapping when sending tool results back to Gemini
- Reset counter at the start of each stream to ensure fresh IDs per request
- Updated test expectations to reflect unique `toolUseId` format
- Added new test `test_stream_response_multiple_tool_uses_unique_ids` to verify multiple calls get unique IDs

## Related Issues
#1200

## Documentation PR
No documentation changes required

## Type of Change
Bug fix

## Testing
All tests pass successfully:
- Updated existing test `test_stream_response_tool_use` to expect unique `toolUseId` format (`tooluse_0` instead of function name)
- Added new test `test_stream_response_multiple_tool_uses_unique_ids` that specifically verifies two calls to the same tool get different IDs (`tooluse_0` and `tooluse_1`)
- Ran `hatch test -k gemini` - all 25 Gemini tests pass
- Ran `hatch run prepare` - all tests, linting, and formatting checks pass

Verified no warnings introduced in consuming repositories:
- Tests include proper handling of the ID-to-name mapping
- Backward compatibility maintained (fallback to `toolUseId` if not in mapping)
- Counter reset per stream ensures no ID conflicts across requests

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
