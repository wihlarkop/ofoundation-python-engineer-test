"""Agent state management and execution trace models.

This module defines the core data structures for tracking agent execution:
- ExecutionStep: Individual tool execution records
- AgentState: Complete execution state with steps and memory
- AgentResult: Final result returned to users
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(tz=UTC)


class ExecutionStep(BaseModel):
    """Represents a single step in agent execution trace.

    Each step records what tool was executed, with what inputs,
    what outputs were produced, and any errors that occurred.
    """

    step: int = Field(..., description="Step number (1-indexed)")
    tool: str = Field(..., description="Tool name that was executed")
    input: dict[str, Any] = Field(..., description="Tool input parameters")
    output: dict[str, Any] | None = Field(None, description="Tool execution result")
    error: str | None = Field(None, description="Error message if step failed")
    timestamp: datetime = Field(default_factory=get_utc_now)

    model_config = {"frozen": False}


class AgentState(BaseModel):
    """Maintains agent execution state throughout task execution.

    The state tracks the goal, all execution steps, intermediate memory,
    and the current status. It provides a complete audit trail of agent actions.

    Example:
        state = AgentState(goal="Calculate 2+2")
        step = state.add_step("math", {"expression": "2+2"})
        step.output = {"result": 4}
    """

    goal: str = Field(..., description="User's natural language goal")
    context: str | None = Field(None, description="Optional context")
    steps: list[ExecutionStep] = Field(default_factory=list)
    memory: dict[str, Any] = Field(
        default_factory=dict, description="Scratch space for intermediate values"
    )
    status: str = Field(
        "running", description="Current status: running | completed | error"
    )
    final_output: str | None = Field(None, description="Final result to user")

    def add_step(self, tool: str, input_data: dict[str, Any]) -> ExecutionStep:
        """Add a new execution step and return it for mutation.

        Args:
            tool: Name of the tool being executed
            input_data: Input parameters for the tool

        Returns:
            ExecutionStep instance that can be updated with results
        """
        step = ExecutionStep(step=len(self.steps) + 1, tool=tool, input=input_data)
        self.steps.append(step)
        return step

    def get_latest_step(self) -> ExecutionStep | None:
        """Get the most recent execution step.

        Returns:
            Last ExecutionStep or None if no steps exist
        """
        return self.steps[-1] if self.steps else None


class AgentResult(BaseModel):
    """Final result returned by agent execution.

    Contains the overall status, user-facing output, and complete
    execution trace for transparency and debugging.

    Example:
        {
            "status": "success",
            "output": "Calculation result: 42",
            "trace": [
                {
                    "step": 1,
                    "tool": "math",
                    "input": {"expression": "40+2"},
                    "output": {"result": 42},
                    "error": None
                }
            ]
        }
    """

    status: str = Field(..., description="success | error")
    output: str = Field(..., description="Final user-facing result")
    trace: list[ExecutionStep] = Field(..., description="Complete execution trace")
