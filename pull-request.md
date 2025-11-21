## Description

This PR implements support for interrupts from any HookEvent type, addressing issue #1165. Previously, only `BeforeToolCallEvent` supported interrupts through the `_Interruptible` interface. This enhancement extends interrupt capability to all hook events, enabling human-in-the-loop workflows at any point in the agent lifecycle.

**Key Changes:**
1. Extended `_Interruptible` interface to all HookEvent types:
   - `AgentInitializedEvent`
   - `BeforeInvocationEvent`
   - `AfterInvocationEvent`
   - `MessageAddedEvent`
   - `BeforeToolCallEvent` (already supported)
   - `AfterToolCallEvent` (main use case from issue)
   - `BeforeModelCallEvent`
   - `AfterModelCallEvent`

2. Implemented unique `_interrupt_id()` method for each event type to ensure proper interrupt identification

3. Updated tool executor to properly check for interrupts from `AfterToolCallEvent` in all code paths (success, error, cancel, unknown tool)

4. Added comprehensive integration tests demonstrating the new capability, particularly for `AfterToolCallEvent` with error handling scenarios

**Use Case (from issue #1165):**
This enables raising an interrupt from an `AfterToolCallEvent` in response to a tool failure, allowing an external execution manager to analyze the result and potentially get a human in the loop to resume at a later time.

## Related Issues

#1165

## Documentation PR

No documentation changes required

## Type of Change

New feature

## Testing

All tests pass with no new warnings:

**Unit Tests:**
- All 1527 unit tests pass across Python 3.13, 3.12, 3.11, 3.10
- Added 5 new integration tests in `tests_integ/interrupts/test_after_tool_call_interrupt.py`:
  - `test_after_tool_call_interrupt_on_failure`: Verifies interrupt raised on tool failure
  - `test_after_tool_call_interrupt_retry_response`: Tests resuming with RETRY response
  - `test_after_tool_call_interrupt_skip_response`: Tests resuming with SKIP response  
  - `test_after_tool_call_no_interrupt_on_success`: Verifies no interrupt on success
  - `test_after_tool_call_interrupt_multiple_tools`: Tests interrupts with multiple tool calls

**Integration Tests:**
- All existing interrupt tests continue to pass
- New `AfterToolCallEvent` interrupt tests demonstrate the use case from the issue
- No warnings introduced in agents-docs, agents-tools, or agents-cli (verified via `hatch run prepare`)

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
