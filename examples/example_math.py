"""Example: Math Tool Usage

Demonstrates safe mathematical expression evaluation.
Uses AST parsing to prevent code injection attacks.

Run with: uv run python examples/example_math.py
"""

from app.agent.core import Agent


def main():
    """Run math calculation examples."""
    print("=" * 60)
    print("Math Tool Example")
    print("=" * 60)

    # Initialize agent
    agent = Agent()

    # Example calculations
    examples = [
        "Calculate 2 + 2",
        "What is 100 / 3",
        "Evaluate (5 + 3) ** 2",
        "Compute 42 * 1.5",
        "Solve (100 + 50) * 2",
        "Calculate 10 ** 2 - 5",
    ]

    print("\n[Running calculations]")
    print("-" * 40)

    for example in examples:
        result = agent.run(goal=example, tool_names=["math"])

        print(f"\nGoal: {example}")
        print(f"Status: {result.status}")
        print(f"Output: {result.output}")

        # Show execution details
        if result.trace:
            step = result.trace[0]
            if step.output:
                expression = step.output.get("expression", "")
                result_value = step.output.get("result", "")
                print(f"  Expression: {expression} = {result_value}")

    # Example: Show full trace details
    print("\n\n[Detailed trace example]")
    print("-" * 40)
    result = agent.run(
        goal="Calculate the result of (20 + 30) * 5", tool_names=["math"]
    )

    print("Goal: Calculate the result of (20 + 30) * 5")
    print(f"Status: {result.status}")
    print(f"Output: {result.output}")
    print("\nComplete execution trace:")
    for step in result.trace:
        print(f"  Step {step.step}:")
        print(f"    Tool: {step.tool}")
        print(f"    Input: {step.input}")
        print(f"    Output: {step.output}")
        print(f"    Error: {step.error}")
        print(f"    Timestamp: {step.timestamp}")

    # Example: Error handling (invalid expression)
    print("\n\n[Error handling example]")
    print("-" * 40)
    result = agent.run(
        goal="Calculate __import__('os').system('echo bad')", tool_names=["math"]
    )

    print("Goal: (attempting malicious code)")
    print(f"Status: {result.status}")
    print(f"Output: {result.output}")
    if result.trace and result.trace[0].error:
        print(f"Error caught: {result.trace[0].error}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("Note: The math tool uses safe AST parsing - ")
    print("malicious code is blocked automatically.")
    print("=" * 60)


if __name__ == "__main__":
    main()
