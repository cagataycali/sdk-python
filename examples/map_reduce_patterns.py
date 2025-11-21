#!/usr/bin/env python3
"""
Dynamic Map-Reduce Patterns in Strands Agents

This example demonstrates how to implement dynamic map-reduce workflows
in Strands, similar to LangGraph's Send API, where you can spawn 1-N agents
at runtime based on query complexity.

Two approaches are shown:
1. Swarm-based map-reduce (autonomous coordination)
2. Workflow-based map-reduce (explicit dependency management)

Use Case: Document summarization where each agent processes a chunk
and a final agent creates a "summary of summaries".
"""

from strands_tools import swarm, workflow

from strands import Agent

# ============================================================================
# APPROACH 1: Swarm-Based Dynamic Map-Reduce
# ============================================================================
# Best for: Autonomous collaboration, self-organizing teams
# Features: Agents decide when to hand off, shared context, emergent behavior
# ============================================================================


def dynamic_map_reduce_swarm(document: str, chunk_size: int = 1000):
    """
    Dynamic map-reduce using Swarm pattern.

    - Splits document into chunks at runtime
    - Creates 1-N "mapper" agents dynamically based on document size
    - Adds 1 "reducer" agent for final summary
    - Agents coordinate autonomously through handoffs

    Args:
        document: The document to summarize
        chunk_size: Approximate size of each chunk in characters

    Returns:
        Final summary result from the swarm
    """
    # Create agent with swarm tool
    agent = Agent(tools=[swarm])

    # Split document into chunks dynamically (1-5 agents based on size)
    chunks = [document[i : i + chunk_size] for i in range(0, len(document), chunk_size)]
    num_chunks = min(len(chunks), 5)  # Cap at 5 agents
    chunks = chunks[:num_chunks]

    print(f"📄 Document size: {len(document)} chars")
    print(f"🤖 Spawning {num_chunks} mapper agents + 1 reducer agent")

    # Dynamically create mapper agents (1-5 based on document complexity)
    mapper_agents = []
    for i in range(num_chunks):
        mapper_agents.append(
            {
                "name": f"mapper_{i + 1}",
                "system_prompt": f"""You are a document analysis specialist (Mapper {i + 1}).
            
Your task:
1. Analyze the document chunk assigned to you
2. Extract key points, themes, and important information
3. Create a concise summary of your chunk (2-3 paragraphs)
4. When done, hand off to the reducer agent for final consolidation

Document Chunk {i + 1}:
{chunks[i]}
""",
                "tools": ["file_write"],  # Can save intermediate results
            }
        )

    # Add reducer agent
    mapper_agents.append(
        {
            "name": "reducer",
            "system_prompt": """You are a master synthesizer (Reducer).

Your task:
1. Review summaries from all mapper agents
2. Identify common themes and key insights across chunks
3. Create a comprehensive "summary of summaries" 
4. Ensure no important information is lost
5. Complete the swarm task when done

Use the complete_swarm_task tool when your final summary is ready.
""",
            "tools": ["file_write"],
        }
    )

    # Execute swarm with dynamic agent team
    result = agent.tool.swarm(
        task="Analyze and summarize this document using map-reduce pattern",
        agents=mapper_agents,
        max_handoffs=20,  # Allow multiple rounds of collaboration
        execution_timeout=900,
    )

    return result


# ============================================================================
# APPROACH 2: Workflow-Based Dynamic Map-Reduce
# ============================================================================
# Best for: Explicit control, parallel execution, complex dependencies
# Features: Clear task dependencies, per-task model selection, predictable flow
# ============================================================================


def dynamic_map_reduce_workflow(document: str, chunk_size: int = 1000):
    """
    Dynamic map-reduce using Workflow pattern.

    - Splits document into chunks at runtime
    - Creates 1-N parallel "map" tasks dynamically
    - Creates 1 "reduce" task that depends on all map tasks
    - Explicit parallel execution with dependency management

    Args:
        document: The document to summarize
        chunk_size: Approximate size of each chunk in characters

    Returns:
        Final summary result from the workflow
    """
    # Create agent with workflow tool
    agent = Agent(tools=[workflow])

    # Split document into chunks dynamically
    chunks = [document[i : i + chunk_size] for i in range(0, len(document), chunk_size)]
    num_chunks = min(len(chunks), 5)  # Cap at 5 agents
    chunks = chunks[:num_chunks]

    print(f"📄 Document size: {len(document)} chars")
    print(f"🤖 Creating {num_chunks} parallel map tasks + 1 reduce task")

    # Dynamically create map tasks (1-5 based on document complexity)
    tasks = []
    map_task_ids = []

    for i in range(num_chunks):
        task_id = f"map_chunk_{i + 1}"
        map_task_ids.append(task_id)

        tasks.append(
            {
                "task_id": task_id,
                "description": f"""Analyze and summarize this document chunk.

Document Chunk {i + 1}:
{chunks[i]}

Create a concise summary extracting:
- Key points and main themes
- Important details and insights
- Critical information

Output: 2-3 paragraph summary of this chunk.""",
                "tools": ["file_write", "calculator"],
                "priority": 5,  # High priority - these run in parallel
                "timeout": 300,
            }
        )

    # Create reduce task that depends on ALL map tasks
    tasks.append(
        {
            "task_id": "reduce_summaries",
            "description": """Review all chunk summaries and create a comprehensive final summary.

Tasks:
1. Read all previous summaries from the map phase
2. Identify common themes and patterns across chunks
3. Create a cohesive "summary of summaries"
4. Ensure key information from all chunks is represented
5. Output a well-structured final summary

Your final summary should:
- Be comprehensive yet concise
- Highlight the most important points
- Maintain logical flow
- Represent the entire document""",
            "dependencies": map_task_ids,  # Depends on ALL map tasks
            "tools": ["file_write", "file_read"],
            "priority": 3,  # Lower priority - runs after map phase completes
            "timeout": 600,
        }
    )

    # Create workflow
    workflow_id = "dynamic_mapreduce"
    agent.tool.workflow(
        action="create",
        workflow_id=workflow_id,
        tasks=tasks,
    )

    # Start execution (map tasks run in parallel)
    agent.tool.workflow(
        action="start",
        workflow_id=workflow_id,
    )

    # Get final results
    status = agent.tool.workflow(
        action="status",
        workflow_id=workflow_id,
    )

    return status


# ============================================================================
# ADVANCED: Multi-Model Map-Reduce
# ============================================================================
# Use different models for map vs reduce phases
# Example: Fast model for mapping, powerful model for reducing
# ============================================================================


def multi_model_map_reduce(document: str, chunk_size: int = 1000):
    """
    Map-reduce with different models for map and reduce phases.

    - Fast/cheap models for parallel map tasks
    - Powerful model for final reduce task
    - Optimal cost/performance balance
    """
    agent = Agent(tools=[workflow])

    chunks = [document[i : i + chunk_size] for i in range(0, len(document), chunk_size)]
    num_chunks = min(len(chunks), 5)
    chunks = chunks[:num_chunks]

    tasks = []
    map_task_ids = []

    # Map tasks with fast model (e.g., Ollama for local speed)
    for i in range(num_chunks):
        task_id = f"map_chunk_{i + 1}"
        map_task_ids.append(task_id)

        tasks.append(
            {
                "task_id": task_id,
                "description": f"Summarize document chunk {i + 1}:\n\n{chunks[i]}",
                "model_provider": "ollama",  # Fast local model
                "model_settings": {"model_id": "qwen3:8b", "params": {"temperature": 0.3}},
                "tools": ["file_write"],
                "priority": 5,
            }
        )

    # Reduce task with powerful model (e.g., Claude Sonnet)
    tasks.append(
        {
            "task_id": "reduce_summaries",
            "description": "Create comprehensive summary from all chunk summaries",
            "dependencies": map_task_ids,
            "model_provider": "bedrock",  # Powerful cloud model
            "model_settings": {
                "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "params": {"temperature": 0.5, "max_tokens": 4000},
            },
            "system_prompt": "You are an expert at synthesizing information from multiple sources.",
            "tools": ["file_write", "file_read"],
            "priority": 3,
            "timeout": 600,
        }
    )

    # Execute
    workflow_id = "multi_model_mapreduce"
    agent.tool.workflow(action="create", workflow_id=workflow_id, tasks=tasks)
    result = agent.tool.workflow(action="start", workflow_id=workflow_id)

    return result


# ============================================================================
# USAGE EXAMPLES
# ============================================================================


if __name__ == "__main__":
    # Sample document
    long_document = (
        """
    [Your long document content here - can be 10,000+ characters]
    This would be split into chunks automatically...
    """
        * 100
    )  # Simulate a long document

    print("=" * 80)
    print("Example 1: Swarm-Based Map-Reduce")
    print("=" * 80)
    result1 = dynamic_map_reduce_swarm(long_document, chunk_size=2000)
    print(f"\nResult: {result1}")

    print("\n" + "=" * 80)
    print("Example 2: Workflow-Based Map-Reduce")
    print("=" * 80)
    result2 = dynamic_map_reduce_workflow(long_document, chunk_size=2000)
    print(f"\nResult: {result2}")

    print("\n" + "=" * 80)
    print("Example 3: Multi-Model Map-Reduce")
    print("=" * 80)
    result3 = multi_model_map_reduce(long_document, chunk_size=2000)
    print(f"\nResult: {result3}")


# ============================================================================
# KEY DIFFERENCES FROM LANGGRAPH'S SEND API
# ============================================================================

"""
LangGraph Send API:
-------------------
graph.add_conditional_edges(
    "split_document",
    continue_to_summarize,
    ["summarize_chunk"],
)

Strands Equivalents:
-------------------

1. Swarm Approach (Recommended for dynamic scenarios):
   - Agents spawned dynamically based on runtime decisions
   - Autonomous coordination through handoff_to_agent
   - Self-organizing, emergent behavior
   - Similar to LangGraph's Send but with more autonomy

2. Workflow Approach (Recommended for explicit control):
   - Tasks created dynamically in code before execution
   - Clear dependency DAG
   - Parallel execution with dependency resolution
   - More predictable than Send API

Key Advantages in Strands:
--------------------------
✅ No graph compilation needed - pure Python
✅ Rich model provider support (Bedrock, Anthropic, Ollama, etc.)
✅ Per-agent/task tool configuration
✅ Built-in monitoring and metrics
✅ File-based persistence
✅ Flexible agent configuration (system prompts, models, tools)

Usage Decision Guide:
--------------------
Use Swarm when:
- You want agents to coordinate autonomously
- Task distribution should be emergent
- Agents should decide collaboration patterns

Use Workflow when:
- You need explicit task dependencies
- Parallel execution is critical
- You want predictable execution flow
- Different models for different tasks
"""
