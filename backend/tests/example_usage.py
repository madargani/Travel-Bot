"""Example usage of unified travel agent."""

import asyncio
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_agent import travel_agent
from agent_dependencies import TravelDependencies


async def example_usage():
    """Example of how to use unified travel agent."""
    deps = TravelDependencies.from_env()

    print("🌍 Travel Agent Example - Planning Trip to Paris")
    print("=" * 60)

    # Example conversation flow
    conversation_steps = [
        "I want to plan a trip from San Francisco to Paris for December 15-22, 2025.",
        "Let's go with the first flight option for $850.",
        "I need a hotel in Paris for those dates, 2 adults, budget around $200/night.",
        "The boutique hotel looks good, let's book that one.",
        "Now I'd like to find some restaurants near my hotel.",
        "What events are happening in Paris during my stay?",
        "What attractions should I visit in Paris?",
    ]

    for i, message in enumerate(conversation_steps, 1):
        print(f"\n👤 User Step {i}: {message}")
        print("-" * 40)

        try:
            result = await travel_agent.run(message, deps=deps)
            print(f"🤖 Agent: {result.output}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(example_usage())
