"""FastAPI route definitions.

Exposes agent execution capabilities via REST endpoints:
- POST /run-task: Execute agent with goal and tools
- GET /governance-notes/{proposal_id}: Retrieve proposal notes
- GET /health: Health check

These endpoints provide HTTP access for AI orchestration systems
(AI CEOs, operators, other agents) to interact with the agent core.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.agent.core import Agent
from app.api.dependencies import get_agent
from app.api.models import (
    GovernanceNotesResponse,
    HealthResponse,
    RunTaskRequest,
    RunTaskResponse,
)
from app.tools.governance import governance_store

# Create router instance
router = APIRouter()


@router.post("/run-task", response_model=RunTaskResponse)
async def run_task(
    request: RunTaskRequest, agent: Agent = Depends(get_agent)
) -> RunTaskResponse:
    """Execute an agent task with specified goal and tools.

    This is the main entry point for AI orchestration systems.
    It accepts a natural language goal, optional context, and tool selection,
    then returns structured results with full execution trace.

    Args:
        request: RunTaskRequest with goal, context, and tools

    Returns:
        RunTaskResponse with status, output, and trace

    Raises:
        HTTPException: If agent execution fails

    Example:
        POST /api/v1/run-task
        {
            "goal": "Calculate (100 + 50) * 2",
            "tools": ["math"]
        }

        Response:
        {
            "status": "success",
            "output": "Calculation result: 300",
            "trace": [...]
        }
    """
    try:
        # Agent is injected via dependency injection
        # Execute task
        result = agent.run(
            goal=request.goal,
            context=request.context,
            tool_names=request.tools if request.tools else None,
        )

        # Convert to API response
        # Serialize ExecutionStep objects to dicts
        return RunTaskResponse(
            status=result.status,
            output=result.output,
            trace=[step.model_dump() for step in result.trace],
        )

    except Exception as e:
        # Return structured error
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e!s}")


@router.get("/governance-notes/{proposal_id}", response_model=GovernanceNotesResponse)
async def get_governance_notes(proposal_id: str) -> GovernanceNotesResponse:
    """Retrieve all notes for a specific governance proposal.

    This endpoint provides read access to the governance note store,
    allowing external systems to query proposal notes without
    executing the agent.

    Args:
        proposal_id: Unique proposal identifier (e.g., "PROP-2025-001")

    Returns:
        GovernanceNotesResponse with proposal_id and notes list

    Raises:
        HTTPException: If retrieval fails

    Example:
        GET /api/v1/governance-notes/PROP-2025-001

        Response:
        {
            "proposal_id": "PROP-2025-001",
            "notes": [
                "Initial review completed",
                "Legal approval granted"
            ]
        }
    """
    try:
        # Get notes from global store
        notes = governance_store.get_notes(proposal_id)

        return GovernanceNotesResponse(proposal_id=proposal_id, notes=notes)

    except Exception as e:
        # Return structured error
        raise HTTPException(status_code=500, detail=f"Failed to retrieve notes: {e!s}")


@router.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint for monitoring and load balancers.

    Returns basic service status and metadata.
    Can be extended with:
    - Database connectivity checks
    - Tool registry validation
    - LLM client status
    - Memory usage metrics

    Returns:
        Dict with status and service info

    Example:
        GET /api/v1/health

        Response:
        {
            "status": "healthy",
            "service": "llm-agent-core",
            "version": "0.1.0"
        }
    """

    return HealthResponse(status="healthy", service="llm-agent-core", version="0.1.0")
