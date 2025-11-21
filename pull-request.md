## Description

This PR addresses issue #1173 by adding comprehensive documentation and code examples demonstrating how to implement dynamic map-reduce patterns in Strands Agents, similar to LangGraph's Send API.

**What was added:**
1. **New examples directory** with practical map-reduce implementations
2. **`examples/map_reduce_patterns.py`** - Complete working examples showing:
   - Swarm-based map-reduce (autonomous coordination)
   - Workflow-based map-reduce (explicit dependencies)
   - Multi-model map-reduce (different models for map vs reduce phases)
   - Direct comparison with LangGraph's Send API approach
3. **`examples/README.md`** - Comprehensive guide for discovering and using examples
4. **Updated main README.md** - Added dedicated section on dynamic map-reduce with quick-start examples

**Key features demonstrated:**
- Dynamic agent/task creation at runtime (1-N agents based on data complexity)
- Parallel execution with automatic coordination
- Per-agent/task model and tool configuration
- Real use case: document summarization with "summary of summaries"

## Related Issues

#1173

## Documentation PR

No documentation changes required - this PR adds examples and in-repo documentation

## Type of Change

Documentation update

## Testing

All existing tests pass without modification. The new examples demonstrate existing functionality through practical use cases.

- [x] I ran `hatch run prepare`
- Verified formatting with `hatch fmt --formatter` 
- Verified linting with `hatch fmt --linter` 
- All unit tests pass: `hatch test` (1527 passed across Python 3.10-3.13)
- No new warnings introduced
- Examples provide runnable code for the exact use case described in the issue

## Checklist

- [x] I have read the CONTRIBUTING document
- [x] I have added any necessary tests that prove my fix is effective or my feature works
- [x] I have updated the documentation accordingly
- [x] I have added an appropriate example to the documentation to outline the feature, or no new docs are needed
- [x] My changes generate no new warnings
- [x] Any dependent changes have been merged and published

----

By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of your choice.
