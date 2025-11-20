# Pull Request: Document correct cachePoint handling in BedrockModel

## Description

This PR clarifies that **BedrockModel already correctly handles cachePoint content blocks** in messages. The current implementation properly preserves cachePoint blocks as standalone blocks in the content array, which is the correct structure for AWS Bedrock's Converse API.

## Analysis

After investigating issue #1219, I found that:

1. **Current behavior is correct**: `_format_request_message_content` already handles cachePoint blocks and formats them correctly as `{"cachePoint": {"type": "default"}}`.

2. **Bedrock uses standalone blocks**: Unlike Anthropic's API (which merges cache_control into previous blocks), Bedrock expects cachePoint to be a separate content block in the array.

3. **Proposed fix was incorrect**: The issue's suggested fix of merging cachePoint into the previous block would cause boto3 validation errors because Bedrock content blocks use tagged unions (only ONE key allowed per block).

4. **Integration test confirms**: The existing integration test `test_bedrock_cache_point.py` demonstrates the correct usage pattern with cachePoint as a standalone block.

## Changes

- Added unit test `test_format_bedrock_messages_preserves_cache_point_blocks` to verify that cachePoint blocks are correctly preserved as standalone blocks

## Testing

### Unit Tests
```bash
hatch test tests/strands/models/test_bedrock.py::test_format_bedrock_messages_preserves_cache_point_blocks
```

**Result**: ✅ PASSED - Confirms cachePoint blocks are preserved correctly

### Integration Tests
The existing integration test `tests_integ/test_bedrock_cache_point.py` demonstrates the correct usage:
```python
messages: Messages = [
    {
        "role": "user",
        "content": [
            {"text": "Some really long text!" * 1000},
            {"cachePoint": {"type": "default"}},  # Standalone block
        ],
    },
]
```

This structure is already supported by the current implementation.

## Correct Usage Example

```python
from strands import Agent
from strands.models import BedrockModel
from strands.types.content import Messages

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region="us-east-2"
)

# ✅ Correct: cachePoint as standalone block
messages: Messages = [
    {
        "role": "user",
        "content": [
            {"text": "Some long text..." * 1000},
            {"cachePoint": {"type": "default"}},  # This works!
        ],
    },
]

agent = Agent(model=model, messages=messages)
agent("What is the content about?")
```

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation (clarifies existing functionality)
- [x] Test (adds test coverage for existing functionality)

## Related Issues

- Closes #1219

## Conclusion

The issue #1219 appears to be based on a misunderstanding of how Bedrock's cachePoint blocks work compared to Anthropic's cache_control. The current implementation is **correct** and **working as intended**. CachePoint blocks should remain as standalone blocks in the Bedrock content array.

If users are experiencing ValidationException errors, it's likely due to:
1. Incorrect message structure (not following the standalone block pattern)
2. Missing AWS credentials or permissions
3. Using a Bedrock region/model that doesn't support caching
