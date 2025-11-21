## Description

This PR implements concurrency protection for the Agent class to prevent state corruption when multiple invocations occur simultaneously. The solution adds a threading lock (`_invocation_lock`) that is acquired non-blockingly at the start of each invocation via `stream_async()`, and raises a new `ConcurrencyException` if an invocation is already in progress.

**Key changes:**
- Added `ConcurrencyException` to `src/strands/types/exceptions.py` - a new exception type raised when concurrent invocations are detected
- Modified `src/strands/agent/agent.py` to:
  - Import `threading` module and `ConcurrencyException`
  - Initialize `self._invocation_lock` in `__init__()`
  - Acquire lock non-blockingly in `stream_async()` and raise exception if already held
  - Release lock in `finally` block to ensure cleanup even on exceptions
- Added comprehensive test coverage in `tests/strands/agent/test_agent.py`:
  - `test_agent_concurrent_invocation_raises_exception` - verifies exception is raised for concurrent async calls
  - `test_agent_sequential_invocations_work` - confirms sequential calls work correctly after lock release

This addresses the issue where retry scenarios (e.g., client timeouts triggering retries while previous request still processing) would corrupt the agent's internal state and cause subsequent calls to fail.

## Related Issues
#1176

## Documentation PR
No documentation changes required

## Type of Change
Bug fix

## Testing
How have you tested the change? Verify that the changes do not break functionality or introduce warnings in consuming repositories: agents-docs, agents-tools, agents-cli

- Verified concurrency protection works by simulating concurrent async invocations
- Confirmed that `ConcurrencyException` is raised with appropriate error message
- Ensured sequential invocations continue to work normally
- All existing unit tests pass (1529 passed for Python 3.13, 3.12, 3.11; 1525 passed 4 skipped for Python 3.10)
- No new warnings introduced

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
