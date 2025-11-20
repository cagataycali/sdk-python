#!/usr/bin/env python3
"""Test script to demonstrate LiteLLM cost tracking feature.

This script shows how the cost is automatically calculated and included
in the AgentResult metadata when using LiteLLMModel.
"""

import asyncio
from strands import Agent
from strands.models.litellm import LiteLLMModel


async def main():
    """Test LiteLLM cost tracking with a real model."""
    # Initialize LiteLLM model
    model = LiteLLMModel(
        model_id="anthropic/claude-3-7-sonnet-20250219"
    )

    # Create agent with the model
    agent = Agent(model=model)

    # Run a simple query
    print("Running query...")
    response = agent("What is 2+2?")

    # Display the response
    print(f"\nResponse: {response}")

    # Check if cost is available in metrics
    if hasattr(response, "metrics") and hasattr(response.metrics, "accumulated_metrics"):
        if "cost" in response.metrics.accumulated_metrics:
            cost = response.metrics.accumulated_metrics["cost"]
            print(f"\n✓ Cost tracking is working!")
            print(f"  Cost: ${cost:.10f}")
        else:
            print("\n⚠ Cost not found in metrics")
    else:
        print("\n⚠ Metrics not available")

    # Display full metrics summary
    print("\n" + "=" * 60)
    print("Full Metrics Summary:")
    print("=" * 60)
    print(response.metrics.get_summary())


if __name__ == "__main__":
    asyncio.run(main())
