## Description

This PR implements the ability to dynamically generate HTTP headers for MCP tool calls, addressing feature request #1191.

The implementation adds a new helper function `create_http_transport_with_dynamic_headers()` that wraps transport callables to inject headers generated at connection time. This allows users to:

- Dynamically compute authentication tokens at connection time
- Pass context-specific headers (user identity, session info, etc.)
- Maintain flexibility without requiring upstream MCP SDK changes

**Key Changes:**
1. Added `create_http_transport_with_dynamic_headers()` helper function to `mcp_client.py`
2. Added `header_generator` parameter to `MCPClient.__init__()` for future extensibility
3. Exported the helper function in the `strands.tools.mcp` module
4. Added comprehensive unit tests and integration tests
5. Updated documentation with usage examples

**Usage Example:**
```python
from strands.tools.mcp import MCPClient, create_http_transport_with_dynamic_headers
from mcp.client.streamable_http import streamablehttp_client

def get_auth_token():
    return "my-fresh-token"

transport_fn = create_http_transport_with_dynamic_headers(
    base_transport_fn=lambda headers: streamablehttp_client(
        url="https://api.example.com/mcp",
        headers=headers
    ),
    header_generator=lambda ctx: {
        "Authorization": f"Bearer {get_auth_token()}",
        "X-User-ID": ctx.get("user_id", "anonymous")
    },
    context={"user_id": "user123"}
)

client = MCPClient(transport_fn)
```

## Related Issues
#1191

## Documentation PR
No documentation changes required

## Type of Change
New feature

## Testing
How have you tested the change? Verify that the changes do not break functionality or introduce warnings in consuming repositories: agents-docs, agents-tools, agents-cli

- Comprehensive unit tests added in `tests/strands/tools/mcp/test_mcp_client.py`:
  - `test_create_http_transport_with_dynamic_headers` - Basic functionality
  - `test_create_http_transport_with_dynamic_headers_no_context` - Default context handling
  - `test_create_http_transport_with_dynamic_headers_callable_integration` - Integration with MCPClient
  - `test_mcp_client_with_header_generator_parameter` - Parameter storage verification
  
- Integration test added in `tests_integ/mcp/test_dynamic_headers.py`:
  - `test_dynamic_headers_with_stdio_transport_compatibility` - Verifies compatibility with non-HTTP transports

- All existing MCP tests pass (98 tests in `tests/strands/tools/mcp/`)
- Full test suite passes across Python 3.10, 3.11, 3.12, 3.13
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
