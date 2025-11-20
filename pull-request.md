# Add LiteLLM Cost Tracking to Agent Results

## Description

This PR implements cost tracking for LiteLLM model invocations by leveraging LiteLLM's `completion_cost()` function and exposing the cost data in the `AgentResult` metadata.

### Changes Made

1. **Extended `Metrics` TypedDict** (`src/strands/types/event_loop.py`):
   - Added optional `cost: float` field to track dollar cost of model invocations

2. **Updated `LiteLLMModel.format_chunk()`** (`src/strands/models/litellm.py`):
   - Modified metadata chunk formatting to calculate cost using `litellm.completion_cost()`
   - Passes the complete response object to enable cost calculation
   - Added error handling for cost calculation failures
   - Used proper logging format (lazy % formatting instead of f-strings)

3. **Updated `LiteLLMModel.stream()`** (`src/strands/models/litellm.py`):
   - Modified to pass the complete response object when yielding metadata chunk
   - Enables cost calculation by providing the necessary context

4. **Updated `EventLoopMetrics.update_metrics()`** (`src/strands/telemetry/metrics.py`):
   - Added logic to accumulate cost across multiple model invocations
   - Properly tracks total cost in `accumulated_metrics`

5. **Updated metrics display** (`src/strands/telemetry/metrics.py`):
   - Added cost display in the metrics summary output
   - Shows cost with 10 decimal precision for accuracy

6. **Added comprehensive test** (`tests/strands/models/test_litellm.py`):
   - Added `test_stream_with_cost_tracking()` to verify cost is calculated and included
   - Mocks `litellm.completion_cost()` to ensure predictable test results
   - Validates the cost appears in metadata event

## Related Issues

Closes #1216

## Type of Change

- [x] New feature (non-breaking change which adds functionality)
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Other (please describe):

## Testing

### Unit Tests
- All existing tests pass (1527 tests)
- New test added: `test_stream_with_cost_tracking` verifies cost calculation
- Linting passes with no warnings or errors
- Formatting applied with `hatch fmt --formatter`

### Manual Testing
Created `test_cost_tracking.py` to demonstrate the feature:
```python
from strands import Agent
from strands.models.litellm import LiteLLMModel

model = LiteLLMModel(model_id="anthropic/claude-3-7-sonnet-20250219")
agent = Agent(model=model)
response = agent("What is 2+2?")

# Access cost from response metadata
cost = response.metrics.accumulated_metrics["cost"]
print(f"Cost: ${cost:.10f}")
```

### Test Results
```bash
# Run unit tests
hatch test tests/strands/models/test_litellm.py
# Result: 28 passed, 12 warnings in 7.24s

# Run all unit tests  
hatch test tests/
# Result: 1527 passed, 114 warnings in 20.31s

# Run linter
hatch fmt --linter
# Result: All checks passed!

# Run formatter
hatch fmt --formatter
# Result: 2 files reformatted, 251 files left unchanged
```

## How It Works

1. When the LiteLLM model streams responses, it collects the final event with usage data
2. The `format_chunk` method receives the complete response object
3. It calls `litellm.completion_cost(completion_response=event)` to calculate the cost
4. The cost is included in the metadata event's metrics
5. The `EventLoopMetrics` class accumulates the cost across multiple invocations
6. Users can access the cost via `response.metrics.accumulated_metrics["cost"]`

## Benefits

- **Automatic Cost Tracking**: No manual calculation needed
- **Accurate Pricing**: Leverages LiteLLM's provider-specific cost data
- **Backward Compatible**: Cost field is optional, doesn't break existing code
- **Composable**: Works seamlessly with existing metrics infrastructure
- **Accessible**: Available via the same `accumulated_metrics` pattern as token usage

## Implementation Notes

- Cost calculation uses LiteLLM's built-in `completion_cost()` function which has provider-specific pricing logic
- The cost is only calculated when available (graceful degradation if cost calculation fails)
- Cost is accumulated across multiple model invocations, just like token usage
- The implementation follows the existing metrics pattern for consistency
- Error handling ensures that cost calculation failures don't break the agent

## Checklist

- [x] My code follows the style guidelines of this project
- [x] I have performed a self-review of my own code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [x] Any dependent changes have been merged and published in downstream modules
- [x] I have checked my code and corrected any misspellings
- [x] I have used conventional commit messages

## Example Usage

```python
from strands import Agent
from strands.models.litellm import LiteLLMModel

# Initialize model
model = LiteLLMModel(
    model_id="anthropic/claude-3-7-sonnet-20250219"
)

# Create agent
agent = Agent(model=model)

# Run query
response = agent("What is 2+2")

# Access cost from response metadata
print(f"Cost: ${response.metrics.accumulated_metrics['cost']:.10f}")

# View full metrics summary (includes cost)
print(response.metrics.get_summary())
```

## Screenshots / Output

Example metrics output with cost tracking:
```
Event Loop Metrics Summary:
├─ Cycles: total=1, avg_time=2.450s, total_time=2.450s
├─ Tokens: in=100, out=50, total=150
├─ Bedrock Latency: 0ms
├─ Cost: $0.0025000000
├─ Tool Usage:
   └─ ...
```
