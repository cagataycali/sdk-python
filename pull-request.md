## Description

This PR enhances the S3SessionManager to address performance and flexibility issues by:

1. **S3 Client Injection**: Added an optional `s3_client` parameter to the constructor. When provided, the manager uses the pre-configured client instead of creating a new one, reducing latency and allowing better resource management.

2. **Session ID Management**: Added a `set_session_id()` method that allows updating the active session ID dynamically. This enables using a single S3SessionManager instance as a singleton across multiple sessions, eliminating the need to repeatedly create new boto3 clients.

These changes follow the SDK design tenets:
- **Simple at any scale**: Optional parameters maintain backward compatibility
- **Extensible by design**: New functionality doesn't break existing code
- **Composability**: Works seamlessly with existing session management patterns
- **The obvious path is the happy path**: Clear method names and behavior

## Related Issues

#1163

## Documentation PR

No documentation changes required

## Type of Change

Bug fix

## Testing

**New Tests Added:**
- `test_init_with_custom_s3_client`: Verifies custom S3 client can be passed in
- `test_init_with_custom_s3_client_ignores_other_params`: Confirms that when s3_client is provided, boto params are ignored
- `test_set_session_id`: Tests basic session ID updating
- `test_set_session_id_singleton_pattern`: Demonstrates singleton usage across multiple sessions
- `test_set_session_id_invalid`: Validates that path separators in session IDs are rejected

**Test Results:**
- All 44 S3SessionManager tests pass
- Full test suite: 1535 passed (Python 3.10-3.13)
- No new warnings introduced

**Verified compatibility with consuming repos:**
- No breaking changes to public API
- All existing functionality preserved
- Backward compatible additions only

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