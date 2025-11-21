## Description

This PR implements parallel S3 message retrieval in `S3SessionManager.list_messages()` to significantly improve performance for sessions with many messages. The implementation uses `ThreadPoolExecutor` from the `concurrent.futures` module to fetch multiple S3 objects concurrently instead of sequentially.

**Performance Improvement:**
- Sequential: 100 messages × 50ms latency = ~5 seconds
- Parallel: 100 messages = ~50-200ms
- **10-100x speedup** for large message histories

**Key Changes:**
- Added `concurrent.futures` import (`ThreadPoolExecutor`, `as_completed`)
- Refactored message loading loop to use parallel execution
- Maintained message order by tracking original indices
- Implemented graceful error handling (individual failures don't stop operation)
- Ensured backward compatibility (no API changes)

## Related Issues

#1164

## Documentation PR

No documentation changes required

## Type of Change

New feature

## Testing

### Unit Tests
- Added `test_list_messages_parallel_order_preserved`: Verifies order is maintained with 100 messages
- Added `test_list_messages_parallel_with_pagination`: Verifies pagination works correctly with parallel retrieval
- Added `test_list_messages_empty`: Verifies empty message list handling
- All existing tests pass (1526-1530 passed across Python 3.10, 3.11, 3.12, 3.13)

### Test Execution
```bash
hatch test -k test_s3_session_manager  # All S3 session manager tests pass
hatch run prepare  # All checks pass (formatting, linting, tests)
```

### Verified Changes
- ✅ Message order preserved
- ✅ Pagination works correctly
- ✅ Error handling for individual message failures
- ✅ No warnings introduced
- ✅ Type hints satisfied (mypy passes)
- ✅ Backward compatible

Verified that the changes do not break functionality or introduce warnings in consuming repositories: agents-docs, agents-tools, agents-cli (no code changes to these repos required).

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
