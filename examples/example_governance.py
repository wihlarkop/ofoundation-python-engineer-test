"""Example: Governance Note Tool Usage

Demonstrates governance proposal note management.
Uses in-memory storage (data lost on restart).

Run with: uv run python examples/example_governance.py
"""

from app.agent.core import Agent
from app.tools.governance import governance_store


def main():
    """Run governance note examples."""
    print("=" * 60)
    print("Governance Note Tool Example")
    print("=" * 60)

    # Initialize agent
    agent = Agent()

    # Clear any existing notes for clean demo
    governance_store.clear()

    # Example 1: Adding notes to proposals
    print("\n[Example 1] Adding notes to proposals")
    print("-" * 40)

    proposals = [
        ("PROP-2025-001", "Initial review completed by technical team"),
        ("PROP-2025-001", "Legal department approved with minor conditions"),
        ("PROP-2025-001", "Budget allocation confirmed: $500K"),
        ("PROP-2025-002", "Proposal submitted for Q1 2025"),
        ("PROP-2025-002", "Awaiting stakeholder feedback"),
    ]

    for proposal_id, note in proposals:
        result = agent.run(
            goal=f"Add note to {proposal_id}: {note}", tool_names=["governance_note"]
        )

        print(f"\nProposal: {proposal_id}")
        print(f"Note: {note}")
        print(f"Status: {result.status}")
        print(f"Output: {result.output}")

    # Example 2: Retrieving notes
    print("\n\n[Example 2] Retrieving all notes for proposals")
    print("-" * 40)

    for proposal_id in ["PROP-2025-001", "PROP-2025-002"]:
        notes = governance_store.get_notes(proposal_id)
        print(f"\n{proposal_id} - Total notes: {len(notes)}")
        for i, note in enumerate(notes, 1):
            print(f"  {i}. {note}")

    # Example 3: Complete workflow
    print("\n\n[Example 3] Complete governance workflow")
    print("-" * 40)

    workflow_steps = [
        "Add note to proposal PROP-2025-003: Proposal received from DAO member",
        "record note for PROP-2025-003: Initial feasibility assessment - positive",
        "document decision for PROP-2025-003: Moving to community vote stage",
    ]

    print("\nExecuting workflow:")
    for step in workflow_steps:
        result = agent.run(goal=step, tool_names=["governance_note"])
        print(f"  ✓ {result.output}")

    # Show final state
    print("\nFinal state of PROP-2025-003:")
    notes = governance_store.get_notes("PROP-2025-003")
    for i, note in enumerate(notes, 1):
        print(f"  {i}. {note}")

    # Example 4: Show execution trace
    print("\n\n[Example 4] Detailed execution trace")
    print("-" * 40)

    result = agent.run(
        goal='Add note to proposal PROP-2025-004: "Final approval granted"',
        tool_names=["governance_note"],
    )

    print("Execution trace:")
    for step in result.trace:
        print(f"\n  Step {step.step}:")
        print(f"    Tool: {step.tool}")
        print(f"    Input: {step.input}")
        print(f"    Output: {step.output}")
        print(f"    Timestamp: {step.timestamp}")

    # Summary
    print("\n\n[Summary] Current governance store state")
    print("-" * 40)

    # Get all unique proposal IDs
    all_proposals = set()
    for proposal_id in [
        "PROP-2025-001",
        "PROP-2025-002",
        "PROP-2025-003",
        "PROP-2025-004",
    ]:
        notes = governance_store.get_notes(proposal_id)
        if notes:
            all_proposals.add(proposal_id)
            print(f"\n{proposal_id}: {len(notes)} notes")

    print(f"\nTotal proposals tracked: {len(all_proposals)}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nNote: This uses in-memory storage.")
    print("Data will be lost when the process ends.")
    print("For production, use a persistent database.")
    print("=" * 60)


if __name__ == "__main__":
    main()
