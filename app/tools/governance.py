"""Governance note management tool with in-memory storage.

Allows appending notes to governance proposals and retrieving them.
Uses a simple dict-based in-memory store for development/demo purposes.

In production, this would be backed by:
- PostgreSQL with SQLAlchemy
- Redis for distributed caching
- On-chain storage for decentralized governance
- Document database like MongoDB
"""

from typing import Any

from pydantic import BaseModel, Field

from app.tools.base import tool_registry


class GovernanceNoteInput(BaseModel):
    """Input schema for governance note tool."""

    proposal_id: str = Field(..., min_length=1, description="Proposal identifier")
    note: str = Field(..., min_length=1, description="Note content to append")


class GovernanceNoteOutput(BaseModel):
    """Output schema for governance note tool."""

    proposal_id: str = Field(..., description="Proposal identifier")
    note_added: str = Field(..., description="The note that was added")
    total_notes: int = Field(..., description="Total notes for this proposal")


class GovernanceNoteStore:
    """In-memory store for governance notes.

    Simple dict-based storage for development. Data is lost on restart.

    Production upgrade path:
    1. Replace dict with database connection
    2. Keep the same interface (add_note, get_notes)
    3. Add persistence, transactions, and concurrency control
    4. No changes needed in tool or API layer

    Example:
        store = GovernanceNoteStore()
        count = store.add_note("PROP-123", "Approved by legal")
        notes = store.get_notes("PROP-123")
    """

    def __init__(self):
        """Initialize empty note storage."""
        self._store: dict[str, list[str]] = {}

    def add_note(self, proposal_id: str, note: str) -> int:
        """Add a note to a proposal and return total count.

        Args:
            proposal_id: Unique proposal identifier
            note: Note content to append

        Returns:
            Total number of notes for this proposal
        """
        if proposal_id not in self._store:
            self._store[proposal_id] = []

        self._store[proposal_id].append(note)
        return len(self._store[proposal_id])

    def get_notes(self, proposal_id: str) -> list[str]:
        """Retrieve all notes for a proposal.

        Args:
            proposal_id: Unique proposal identifier

        Returns:
            List of notes (empty list if proposal not found)
        """
        return self._store.get(proposal_id, []).copy()

    def clear(self):
        """Clear all notes (useful for testing)."""
        self._store.clear()


# Global store instance (singleton pattern)
governance_store = GovernanceNoteStore()


class GovernanceNoteTool:
    """Tool for appending governance notes to proposals.

    Designed for AI governance workflows where agents need to:
    - Record decisions and rationale
    - Track proposal review status
    - Maintain audit trails
    - Coordinate multi-agent governance processes

    Future extension: integrate with on-chain governance systems,
    ENS proposals, DAO voting platforms, etc.
    """

    def __init__(self, store: GovernanceNoteStore | None = None):
        """Initialize tool with optional custom store.

        Args:
            store: GovernanceNoteStore instance (uses global by default)
        """
        self._store = store or governance_store

    @property
    def name(self) -> str:
        return "governance_note"

    @property
    def description(self) -> str:
        return (
            "Appends a note to a governance proposal. "
            "Input: {'proposal_id': 'PROP-123', 'note': 'Review completed'}. "
            "Returns: confirmation with total note count."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return GovernanceNoteInput.model_json_schema()

    def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Add governance note to store.

        Args:
            input: Dict with 'proposal_id' and 'note'

        Returns:
            Dict with confirmation and total note count

        Raises:
            ValueError: If input validation fails
        """
        # Validate input
        validated_input = GovernanceNoteInput(**input)

        # Add note to store
        total = self._store.add_note(validated_input.proposal_id, validated_input.note)

        # Return validated output
        output = GovernanceNoteOutput(
            proposal_id=validated_input.proposal_id,
            note_added=validated_input.note,
            total_notes=total,
        )
        return output.model_dump()


# Auto-register tool on module import
tool_registry.register(GovernanceNoteTool())
