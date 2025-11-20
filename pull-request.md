# Pull Request: Support for Bedrock Service Tiers

## Description

This PR adds support for Amazon Bedrock Service Tiers, allowing users to optimize cost and performance for their AI workloads.

**What changed:**
- Added `service_tier` parameter to `BedrockModel.BedrockConfig` with three supported values: `"priority"`, `"standard"`, and `"flex"`
- Updated `_format_request` method to include `performanceConfig` when service tier is specified
- Implemented graceful error handling that automatically retries without service tier when model doesn't support it
- Added comprehensive tests covering all three service tiers and error handling scenarios

**Why this matters:**
Service Tiers enable users to:
- Use `"flex"` for cost-optimized long-running workflows that are not time-sensitive
- Use `"standard"` for balanced performance and cost (default behavior when not specified)
- Use `"priority"` for time-critical workloads requiring lowest latency

**Implementation details:**
- Service tier is optional - existing code continues to work without changes
- When a model doesn't support service tiers, a warning is logged and the request automatically retries without the service tier parameter
- The configuration persists after retry, allowing future calls to attempt using the service tier again
- Follows AWS Bedrock API structure: `performanceConfig: {"latency": "priority|standard|flex"}`

## Related Issues

Closes #1206

## Type of Change

- [x] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Other (please describe):

## Testing

### Unit Tests Added:
1. `test_format_request_with_service_tier_priority` - Verifies priority tier is correctly included in request
2. `test_format_request_with_service_tier_standard` - Verifies standard tier is correctly included in request
3. `test_format_request_with_service_tier_flex` - Verifies flex tier is correctly included in request
4. `test_format_request_without_service_tier` - Ensures backward compatibility when tier is not specified
5. `test_stream_with_unsupported_service_tier_retries_without_it` - Tests graceful handling with warning and retry
6. `test_stream_with_supported_service_tier_works` - Tests successful execution with service tier
7. `test_service_tier_config_persists_after_retry` - Ensures configuration is preserved after retry

### Test Results:
```
tests/strands/models/test_bedrock.py::test_format_request_with_service_tier_priority PASSED
tests/strands/models/test_bedrock.py::test_format_request_with_service_tier_standard PASSED
tests/strands/models/test_bedrock.py::test_format_request_with_service_tier_flex PASSED
tests/strands/models/test_bedrock.py::test_format_request_without_service_tier PASSED
tests/strands/models/test_bedrock.py::test_stream_with_unsupported_service_tier_retries_without_it PASSED
tests/strands/models/test_bedrock.py::test_stream_with_supported_service_tier_works PASSED
tests/strands/models/test_bedrock.py::test_service_tier_config_persists_after_retry PASSED

======================== 99 passed, 5 warnings in 0.38s ========================
```

### Manual Testing:
Tested with the following scenarios:
1. Creating an agent with `service_tier="flex"` for cost-optimized workloads
2. Creating an agent with `service_tier="priority"` for time-critical tasks
3. Creating an agent without specifying service_tier (backward compatibility)
4. Attempting to use service tier with a model that doesn't support it (graceful fallback)

### Example Usage:
```python
from strands import Agent
from strands.models import BedrockModel

# Cost-optimized for long-running workflows
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    service_tier="flex"
)
agent = Agent(model=model, tools=[...])

# Time-critical workloads
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    service_tier="priority"
)
agent = Agent(model=model, tools=[...])

# Default behavior (no service tier)
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"
)
agent = Agent(model=model, tools=[...])
```

## Checklist

- [x] I have read the [CONTRIBUTING](CONTRIBUTING.md) document
- [x] My code follows the code style of this project (ruff formatting and linting)
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] All new and existing tests pass locally
- [x] I have added type hints to all function signatures
- [x] My changes generate no new warnings
- [x] I have made corresponding changes to the documentation (inline docstrings)
- [x] My commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification

## Additional Context

This feature implements the AWS Bedrock Service Tiers as announced in the [AWS blog post](https://aws.amazon.com/blogs/aws/new-amazon-bedrock-service-tiers-help-you-match-ai-workload-performance-with-cost/).

The implementation follows the SDK's development tenets:
- **Simple at any scale**: Single optional parameter, clear semantics
- **Extensible by design**: Easy to add new tier types in the future
- **Composability**: Works with all existing BedrockModel features
- **The obvious path is the happy path**: Intuitive API, automatic fallback for unsupported models
- **Accessible to humans and agents**: Clear parameter names and behavior
- **Embrace common standards**: Follows AWS Bedrock API conventions

## Screenshots/Logs

When service tier is not supported by the model, the following warning is logged:

```
WARNING:strands.models.bedrock:Service tier 'flex' is not supported for model 'model-id'. Retrying without service tier.
```

The request then automatically succeeds without the service tier parameter, ensuring non-blocking behavior as requested in the issue.
