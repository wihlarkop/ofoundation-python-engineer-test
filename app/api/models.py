"""API request and response models for FastAPI endpoints.

Defines Pydantic models for HTTP request/response validation and
automatic OpenAPI documentation generation.
"""

from pydantic import BaseModel, ConfigDict, Field


class RunTaskRequest(BaseModel):
    """Request model for POST /run-task endpoint.

    Clients submit a natural language goal, optional context,
    and a list of tools to make available to the agent.
    """

    goal: str = Field(..., min_length=1, description="Natural language task goal")
    context: str | None = Field(None, description="Optional context or constraints")
    tools: list[str] = Field(
        default_factory=lambda: ["web_search", "math", "governance_note"],
        description="Tool names to make available to the agent",
    )

    model_config: ConfigDict = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "goal": "Search for Python async best practices and summarize",
                    "context": "Focus on FastAPI-specific patterns",
                    "tools": ["web_search"],
                },
                {"goal": "Calculate the result of (100 + 50) * 2", "tools": ["math"]},
            ]
        }
    )


class RunTaskResponse(BaseModel):
    """Response model for POST /run-task endpoint.

    Returns the execution status, final output, and complete
    trace of all tool executions for transparency.
    """

    status: str = Field(..., description="success | error")
    output: str = Field(..., description="Final user-facing result")
    trace: list[dict] = Field(..., description="Complete execution trace")

    model_config: ConfigDict = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "success",
                    "output": "Calculation result: 300",
                    "trace": [
                        {
                            "step": 1,
                            "tool": "math",
                            "input": {"expression": "(100 + 50) * 2"},
                            "output": {"result": 300, "expression": "(100 + 50) * 2"},
                            "error": None,
                            "timestamp": "2025-12-16T10:00:00Z",
                        }
                    ],
                }
            ]
        }
    )


class GovernanceNotesResponse(BaseModel):
    """Response model for GET /governance-notes/{proposal_id}.

    Returns all notes associated with a specific governance proposal.
    """

    proposal_id: str = Field(..., description="Proposal identifier")
    notes: list[str] = Field(..., description="All notes for this proposal")

    model_config: ConfigDict = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "proposal_id": "PROP-2025-001",
                    "notes": [
                        "Initial review completed",
                        "Requires legal approval",
                        "Budget approved",
                    ],
                }
            ]
        }
    )


class HealthResponse(BaseModel):
    """Response model for GET /health.

    Returns the health status of the application.
    """
    status: str = Field(..., description="success | error")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
