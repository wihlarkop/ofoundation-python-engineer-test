"""Example: Web Search Tool Usage

Demonstrates how to use the agent to search for information.
The mock implementation returns realistic search results without API calls.

Run with: uv run python examples/example_web_search.py
"""

from app.agent.core import Agent


def main():
    """Run web search examples."""
    print("=" * 60)
    print("Web Search Tool Example")
    print("=" * 60)

    # Initialize agent
    agent = Agent()

    # Example 1: Basic search
    print("\n[Example 1] Basic web search")
    print("-" * 40)
    result = agent.run(
        goal="Search for Python FastAPI best practices", tool_names=["web_search"]
    )

    print(f"Status: {result.status}")
    print(f"Output: {result.output}")
    print("\nExecution trace:")
    for step in result.trace:
        print(f"  Step {step.step}: {step.tool}")
        print(f"    Input: {step.input}")
        if step.output:
            results = step.output.get("results", [])
            print(f"    Output: {len(results)} results")
            for i, res in enumerate(results[:2], 1):  # Show first 2
                print(f"      {i}. {res.get('title', 'N/A')}")
                print(f"         {res.get('url', 'N/A')}")

    # Example 2: Search with context
    print("\n\n[Example 2] Search with specific context")
    print("-" * 40)
    result = agent.run(
        goal="Find information about async programming",
        context="Focus on Python 3.11+ features",
        tool_names=["web_search"],
    )

    print(f"Status: {result.status}")
    print(f"Output: {result.output}")

    # Example 3: Multiple search-style queries
    print("\n\n[Example 3] Multiple queries")
    print("-" * 40)
    queries = [
        "look up machine learning tutorials",
        "research blockchain technology",
        "find Docker best practices",
    ]

    for query in queries:
        result = agent.run(goal=query, tool_names=["web_search"])
        print(f"\nQuery: {query}")
        print(f"Result: {result.output}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
