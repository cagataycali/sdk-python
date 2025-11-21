## Description
Fixed a bug in the `_normalize_property` function in `src/strands/tools/tools.py` where properties with `anyOf`, `oneOf`, or `allOf` JSON schema constructs were incorrectly having a default `type="string"` set. This caused tool input validation errors when MCP servers describe complex data types like `List[str] | None` using `anyOf`.

The fix checks for the presence of `anyOf`, `oneOf`, or `allOf` before setting the default `type` to `"string"`, allowing these schema constructs to properly define their own types.

## Related Issues
#1190

## Documentation PR
No documentation changes required

## Type of Change
Bug fix

## Testing
How have you tested the change? Verify that the changes do not break functionality or introduce warnings in consuming repositories: agents-docs, agents-tools, agents-cli

- Added 4 comprehensive test cases in `tests/strands/tools/test_tools.py`:
  1. `test_normalize_schema_with_anyof` - Tests that `anyOf` properties don't get default `type="string"`
  2. `test_normalize_schema_with_oneof` - Tests that `oneOf` properties don't get default `type="string"`
  3. `test_normalize_schema_with_allof` - Tests that `allOf` properties don't get default `type="string"`
  4. `test_normalize_schema_with_anyof_list_of_strings` - Tests the exact case from issue #1190 (`List[str] | None`)

All tests verify that when these JSON schema constructs are present, the `type` field is NOT set to `"string"`, which was the root cause of the bug.

- [x] I ran `hatch run prepare`

All tests pass:
- Unit tests: 1531 passed
- Integration tests: Failures are only for Gemini API (environmental - API not enabled in test project)
- Linting: All checks passed
- Formatting: All files formatted correctly
- Type checking: mypy passed with no issues

## Checklist
- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
