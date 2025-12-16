"""Core agent orchestration logic.

This module implements the main Agent class responsible for:
- Accepting goals and orchestrating execution
- Using LLM to plan tool selection
- Executing tools in sequence
- Maintaining complete execution traces
- Returning structured results

The Agent is independent of the HTTP layer and can be called
directly by Trigger.dev, CLI scripts, or other orchestration systems.
"""

from typing import Any

import app.tools.governance
import app.tools.math

# Import tools to trigger auto-registration
import app.tools.web_search  # noqa: F401
from app.agent.planner import AgentPlanner
from app.agent.state import AgentResult, AgentState, ExecutionStep
from app.llm.interface import LLMClient
from app.llm.mock_client import MockLLMClient
from app.logger import setup_logger
from app.tools.base import Tool, tool_registry

# Setup logger
logger = setup_logger(__name__)


class Agent:
    """Core agent orchestration class.

    The Agent is the main entry point for task execution. It:
    1. Accepts a natural language goal
    2. Uses an LLM to plan which tools to use
    3. Executes tools step by step
    4. Maintains a complete trace of all actions
    5. Returns structured results

    Key features:
    - HTTP-independent (can be called directly)
    - Complete traceability (every step recorded)
    - Error handling at tool and agent level
    - Max step limit to prevent infinite loops
    - Swappable LLM client

    Example:
        agent = Agent()
        result = agent.run(
            goal="Calculate (100 + 50) * 2",
            tool_names=["math"]
        )
        print(result.output)  # "Calculation result: 300"
        print(result.trace)   # [ExecutionStep(...)]
    """

    # Safety limit to prevent infinite loops
    MAX_STEPS = 10

    def __init__(self, llm_client: LLMClient | None = None):
        """Initialize agent with optional LLM client.

        Args:
            llm_client: LLM client instance. If None, uses MockLLMClient.
                       In production, pass a real LLM client here.
        """
        self.llm_client = llm_client or MockLLMClient()
        self.planner = AgentPlanner(self.llm_client)

    def run(
        self, goal: str, context: str | None = None, tool_names: list[str] | None = None
    ) -> AgentResult:
        """Execute agent task from start to finish.

        This is the main entry point. It runs a complete execution loop:
        1. Initialize state with goal
        2. Get available tools
        3. Loop: plan next step → execute tool → update state
        4. Return final result with complete trace

        Args:
            goal: Natural language task description
            context: Optional additional context or constraints
            tool_names: List of tool names to make available.
                       If None, all registered tools are available.

        Returns:
            AgentResult with status, output, and execution trace

        Example:
            result = agent.run(
                goal="Search for Python async programming tips",
                context="Focus on FastAPI patterns",
                tool_names=["web_search"]
            )
        """
        # Initialize execution state
        state = AgentState(goal=goal, context=context)

        # Get available tools from registry
        if tool_names:
            available_tools = tool_registry.get_tools_for_names(tool_names)

            # Warn if some tools weren't found (but continue with what we have)
            missing = set(tool_names) - set(available_tools.keys())
            if missing:
                logger.warning(f"Tools not found: {missing}")
        else:
            available_tools = tool_registry.get_all()

        try:
            # Main execution loop
            for _ in range(self.MAX_STEPS):
                # Plan next step using LLM
                plan = self.planner.plan_next_step(
                    goal=state.goal,
                    context=state.context,
                    available_tools=available_tools,
                    execution_history=[s.model_dump() for s in state.steps],
                )

                # Handle different action types
                action = plan.get("action")

                if action == "answer":
                    # Agent decided to answer directly without tools
                    state.status = "completed"
                    state.final_output = plan.get("final_answer", "Task completed")
                    break

                elif action == "use_tool":
                    # Execute the selected tool
                    tool_name = plan.get("tool_name")
                    tool_input = plan.get("tool_input", {})

                    self._execute_tool(
                        state=state,
                        tool_name=tool_name,
                        tool_input=tool_input,
                        available_tools=available_tools,
                    )

                    # Check if goal is achieved after tool execution
                    if self._is_goal_achieved(state):
                        state.status = "completed"
                        state.final_output = self._format_final_output(state)
                        break

                else:
                    # Unknown action type
                    raise ValueError(f"Unknown action type: {action}")

            # If we exited loop without breaking, we hit MAX_STEPS
            if state.status == "running":
                state.status = "completed"
                state.final_output = self._format_final_output(state)

            # Return successful result
            return AgentResult(
                status=state.status,
                output=state.final_output or "Task completed",
                trace=state.steps,
            )

        except Exception as e:
            # Handle execution errors gracefully
            state.status = "error"
            state.final_output = f"Error: {e!s}"

            return AgentResult(
                status="error", output=state.final_output, trace=state.steps
            )

    def _execute_tool(
        self,
        state: AgentState,
        tool_name: str,
        tool_input: dict[str, Any],
        available_tools: dict[str, Tool],
    ) -> ExecutionStep:
        """Execute a single tool and update state.

        This method:
        1. Creates an execution step record
        2. Looks up the tool in the registry
        3. Executes the tool with provided input
        4. Updates the step with results or errors
        5. Returns the completed step

        Args:
            state: Current agent state
            tool_name: Name of tool to execute
            tool_input: Input parameters for the tool
            available_tools: Available tool instances

        Returns:
            ExecutionStep with results
        """
        # Create step record (starts with no output)
        step = state.add_step(tool_name, tool_input)

        try:
            # Get tool instance from registry
            tool = available_tools.get(tool_name)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found in available tools")

            # Execute tool
            output = tool.run(tool_input)

            # Update step with successful output
            step.output = output
            step.error = None

        except Exception as e:
            # Update step with error
            step.output = None
            step.error = str(e)

        return step

    def _is_goal_achieved(self, state: AgentState) -> bool:
        """Determine if the goal has been achieved.

        Simple heuristic: if the last step succeeded, goal is achieved.

        In a production system with a real LLM, you would:
        1. Ask the LLM "Has the goal been achieved?"
        2. Provide the goal and execution history
        3. Let LLM decide based on results

        Args:
            state: Current agent state

        Returns:
            True if goal appears to be achieved
        """
        if not state.steps:
            return False

        last_step = state.get_latest_step()

        # Goal is achieved if last step succeeded (no error)
        return last_step is not None and last_step.error is None

    def _format_final_output(self, state: AgentState) -> str:
        """Format final output based on execution history.

        Generates a user-friendly summary of what was accomplished.

        Args:
            state: Current agent state with execution history

        Returns:
            Formatted output string
        """
        if not state.steps:
            return "No steps executed"

        last_step = state.get_latest_step()

        if not last_step:
            return "Task completed"

        # If last step had an error, report it
        if last_step.error:
            return f"Task failed: {last_step.error}"

        # Format output based on tool type
        if last_step.output:
            output = last_step.output

            if last_step.tool == "web_search":
                results = output.get("results", [])
                query = output.get("query", "")
                return f"Found {len(results)} search results for '{query}'"

            elif last_step.tool == "math":
                result = output.get("result")
                expression = output.get("expression", "")
                return f"Calculation result: {result} (from {expression})"

            elif last_step.tool == "governance_note":
                proposal_id = output.get("proposal_id", "")
                total = output.get("total_notes", 0)
                return f"Added note to proposal {proposal_id} (total notes: {total})"

            else:
                # Generic output for unknown tool types
                return f"Tool {last_step.tool} completed: {output}"

        return "Task completed successfully"
