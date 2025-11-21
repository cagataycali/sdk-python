## Description

This PR implements tracking of agent.messages token size in event logs metrics as requested in issue #1197. The implementation adds a new `context_token_size` field to `EventLoopMetrics` that tracks the current token count of the agent's message context in real-time.

### Key Changes:
1. **Token Estimator Utility** (`src/strands/telemetry/token_estimator.py`):
   - Lightweight character-based estimation (~4 chars per token)
   - Handles all content block types (text, images, tools, documents, etc.)
   - No external API calls - avoids TPM limits and latency issues

2. **Metrics Updates** (`src/strands/telemetry/metrics.py`):
   - Added `context_token_size` field to `EventLoopMetrics`
   - Added `update_context_token_size()` method to update the metric
   - Updated metrics summary to display context token size
   - Added OpenTelemetry histogram for observability

3. **Agent Integration** (`src/strands/agent/agent.py`):
   - Automatically updates context size when messages are added
   - Updates after conversation management operations
   - Updates after context reduction on overflow

4. **Tests**: Comprehensive unit tests for all components

### Benefits:
- **Proactive Context Management**: Track when context is nearing limits
- **Performance**: No external API calls or TPM usage
- **Real-time**: Updates automatically as messages are added/removed
- **Observable**: Exposed via OpenTelemetry metrics

## Related Issues
#1197

## Documentation PR
No documentation changes required

## Type of Change
New feature

## Testing
How have you tested the change? Verify that the changes do not break functionality or introduce warnings in consuming repositories: agents-docs, agents-tools, agents-cli

- [x] I ran `hatch run prepare`
- [x] All unit tests pass (1542 passed)
- [x] Added comprehensive tests for token_estimator module
- [x] Updated existing metrics tests to include context_token_size
- [x] All linting and type checking pass
- [x] No warnings introduced

## Checklist
- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
