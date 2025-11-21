# Strands Agents Examples

This directory contains practical examples demonstrating various patterns and use cases with Strands Agents.

## 📚 Available Examples

### [map_reduce_patterns.py](./map_reduce_patterns.py)
**Dynamic Map-Reduce Workflows**

Learn how to implement dynamic map-reduce patterns in Strands, similar to LangGraph's Send API. This example shows:

- **Dynamic Agent Spawning**: Create 1-N agents at runtime based on data complexity
- **Parallel Processing**: Execute multiple agents/tasks concurrently
- **Two Approaches**: Both Swarm (autonomous) and Workflow (explicit) patterns
- **Multi-Model Support**: Use different models for map vs reduce phases
- **Real Use Case**: Document summarization with "summary of summaries"

```python
# Quick start
from map_reduce_patterns import dynamic_map_reduce_swarm, dynamic_map_reduce_workflow

# Approach 1: Autonomous coordination with Swarm
result = dynamic_map_reduce_swarm(long_document, chunk_size=2000)

# Approach 2: Explicit dependencies with Workflow
result = dynamic_map_reduce_workflow(long_document, chunk_size=2000)
```

**When to use:**
- Document summarization and analysis
- Parallel data processing
- Distributed computation tasks
- Any scenario where you need N workers + 1 aggregator

**Key Features Demonstrated:**
- ✅ Dynamic agent/task creation at runtime
- ✅ Parallel execution with automatic coordination
- ✅ Flexible model selection (per-agent or per-task)
- ✅ Custom tool access control
- ✅ Dependency management
- ✅ Rich monitoring and metrics

## 🎯 Pattern Decision Guide

| Pattern | Best For | Key Features |
|---------|----------|--------------|
| **Swarm** | Autonomous collaboration | Self-organizing, emergent behavior, flexible handoffs |
| **Workflow** | Explicit dependencies | Predictable flow, clear DAG, per-task configuration |

### Swarm vs Workflow for Map-Reduce

**Use Swarm when:**
- You want agents to coordinate autonomously
- Task distribution should emerge naturally
- Agents should decide when to collaborate
- You prefer agent-driven architecture

**Use Workflow when:**
- You need explicit task dependencies (map → reduce)
- Parallel execution timing is critical
- You want predictable execution flow
- Different models/tools for different phases

## 🚀 Getting Started

1. Install Strands with tools support:
```bash
pip install strands-agents[all]
```

2. Run an example:
```bash
python examples/map_reduce_patterns.py
```

3. Customize for your use case:
- Adjust chunk sizes for your data
- Configure different model providers
- Add custom tools for your domain
- Modify system prompts for your tasks

## 📖 Additional Resources

- [Strands Documentation](https://github.com/strands-agents/sdk-python)
- [Multi-Agent Patterns](https://github.com/strands-agents/docs)
- [Tool Development Guide](https://github.com/strands-agents/sdk-python/blob/main/CONTRIBUTING.md)

## 🤝 Contributing

Have a useful pattern or example? Contributions welcome!

1. Add your example file with clear documentation
2. Update this README
3. Follow the [contribution guidelines](../CONTRIBUTING.md)
4. Submit a pull request

## 📝 Example Template

When creating new examples, include:

```python
"""
[Example Title]

[Brief description of the pattern/use case]

[Key concepts demonstrated]
"""

# Clear imports
from strands import Agent

# Well-documented functions
def example_pattern():
    """
    [Function description]
    
    Args:
        [parameters]
    
    Returns:
        [return value]
    """
    pass

# Usage example
if __name__ == "__main__":
    # Demonstrate the pattern
    result = example_pattern()
    print(result)
```

## 💡 Tips

- Start with the simplest pattern for your use case
- Use Swarm for exploration, Workflow for production
- Leverage different models for different task types
- Monitor metrics to optimize performance
- Test with small datasets before scaling
