## Description

This PR enables type checking for integration tests by adding the `tests_integ` package to the mypy lint-check command in pyproject.toml. This addresses the issue where type checking was not being performed on top-level interfaces in integration tests, which could introduce bugs as discovered in #1196.

### Changes Made:
1. **Added `tests_integ` package to mypy command**: Modified `lint-check` script in `[tool.hatch.envs.hatch-static-analysis.scripts]` to include `-p tests_integ`
2. **Added pytest dependency**: Added `pytest>=8.0.0,<9.0.0` to `hatch-static-analysis` environment dependencies to provide type stubs for mypy
3. **Configured mypy overrides**: Added relaxed type checking rules for `tests_integ.*` and `tests.fixtures.*` modules to balance strictness with pragmatism for test code

### Benefits:
- **Catches Interface Bugs**: Type checking now runs on integration tests, catching type mismatches in Agent and Model interfaces
- **Prevents Regressions**: Future PRs will be validated against type safety in integration tests
- **Gradual Improvement**: Relaxed rules allow incremental type safety improvements without blocking current functionality

### Configuration Approach:
The mypy overrides for tests_integ use relaxed rules (disabled error codes for test-specific patterns) while still providing value by:
- Verifying integration test code compiles and type-checks at a basic level
- Catching critical issues in future changes
- Allowing test code flexibility with mocking and fixtures

This follows the SDK tenet of "Simple at any scale" - enable type checking without requiring immediate fixes to all existing test code.

## Related Issues

#1198

## Documentation PR

No documentation changes required

## Type of Change

Bug fix

## Testing

- [x] I ran `hatch run prepare`
- [x] All unit tests pass (1527/1527)
- [x] Integration tests pass (119/207, 77 skipped, 11 Gemini-related failures unrelated to this change)
- [x] Mypy now successfully type-checks both `src` and `tests_integ` packages
- [x] No new warnings introduced in linting or formatting

The mypy configuration change was tested by:
1. Running `hatch fmt --linter` - passes with "All checks passed!"
2. Running `hatch run test-lint` - passes with "Success: no issues found in 160 source files"
3. Running `hatch run prepare` - all steps complete successfully
4. Verified mypy now processes tests_integ directory (160 files checked vs 117 before)

## Checklist

- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
