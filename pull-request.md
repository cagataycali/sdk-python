# fix: add SSL/TLS configuration support for self-signed certificates

## Description
This PR adds documentation and tests for SSL/TLS certificate verification configuration in Anthropic and OpenAI model providers. Users working with self-signed certificates or custom CA bundles can now properly configure SSL verification through the `client_args` parameter.

## Related Issues
Fixes #1218

## Type of Change
- [x] Bug fix (non-breaking change which fixes an issue)
- [x] Documentation update
- [x] Test addition

## Changes Made

### Documentation Updates
1. **AnthropicModel**: Updated `client_args` docstring to document SSL verification options:
   - `verify=False` to disable SSL verification (not recommended for production)
   - `verify="/path/to/ca-bundle.crt"` to use a custom CA bundle

2. **OpenAIModel**: Updated `client_args` docstring to document SSL verification via custom httpx.AsyncClient:
   - Example: `client_args={"http_client": httpx.AsyncClient(verify=False)}`

### Test Additions
1. **test_anthropic.py**:
   - `test_init_with_ssl_verification_disabled`: Verifies `verify=False` parameter is passed correctly
   - `test_init_with_custom_ca_bundle`: Verifies custom CA bundle path is passed correctly

2. **test_openai.py**:
   - `test_init_with_ssl_http_client`: Verifies custom httpx.AsyncClient with SSL config is stored
   - `test_init_stores_client_args`: Verifies client_args are properly stored for later use

## Testing

### Unit Tests
```bash
hatch test tests/strands/models/test_anthropic.py tests/strands/models/test_openai.py
```

**Result**: ✅ All 94 tests passed

### Linting & Formatting
```bash
hatch fmt --formatter  # Formatted 2 files
hatch fmt --linter     # All checks passed!
```

## How to Use

### Anthropic with Self-Signed Certificates
```python
from strands.models.anthropic import AnthropicModel

# Disable SSL verification (not recommended for production)
model = AnthropicModel(
    model_id="claude-3-7-sonnet-latest",
    max_tokens=1024,
    client_args={"verify": False}
)

# Use custom CA bundle
model = AnthropicModel(
    model_id="claude-3-7-sonnet-latest",
    max_tokens=1024,
    client_args={"verify": "/path/to/ca-bundle.crt"}
)
```

### OpenAI with Self-Signed Certificates
```python
import httpx
from strands.models.openai import OpenAIModel

# Disable SSL verification (not recommended for production)
custom_client = httpx.AsyncClient(verify=False)
model = OpenAIModel(
    model_id="gpt-4o",
    params={"max_tokens": 1024},
    client_args={"http_client": custom_client}
)

# Use custom CA bundle
custom_client = httpx.AsyncClient(verify="/path/to/ca-bundle.crt")
model = OpenAIModel(
    model_id="gpt-4o",
    params={"max_tokens": 1024},
    client_args={"http_client": custom_client}
)
```

## Breaking Changes
None - this is a documentation and test-only change that clarifies existing functionality.

## Additional Notes
- The underlying SDK clients (Anthropic and OpenAI) already supported SSL configuration through their initialization parameters
- This PR documents that capability and adds tests to verify it works correctly
- The implementation follows the "extensible by design" and "accessible to humans and agents" tenets
- No changes to production code were needed - only documentation and tests

## Checklist
- [x] Code follows the project's style guidelines (hatch fmt passed)
- [x] Self-review of code completed
- [x] Code is commented, particularly in hard-to-understand areas
- [x] Documentation has been updated to reflect changes
- [x] Changes generate no new warnings
- [x] Tests have been added that prove the fix is effective
- [x] New and existing unit tests pass locally
- [x] No breaking changes introduced
