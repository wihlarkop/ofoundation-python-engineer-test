"""Agent planner for LLM-driven tool selection and sequencing.

This module bridges the agent core and LLM client, handling:
- Prompt construction for the LLM
- Tool description formatting
- Execution history summarization
- Response parsing

The planner is responsible for asking the LLM "what should I do next?"
at each step of agent execution.
"""

from typing import Any

from app.llm.interface import LLMClient
from app.tools.base import Tool


class AgentPlanner:
    """Handles LLM-based planning and tool selection.

    The planner's job is to:
    1. Format available tools for the LLM
    2. Build prompts with goal, context, and history
    3. Ask LLM to decide next action
    4. Return structured decision

    Example:
        planner = AgentPlanner(llm_client)
        decision = planner.plan_next_step(
            goal="Calculate 2+2",
            context=None,
            available_tools={"math": MathTool()},
            execution_history=[]
        )
        # Returns: {"action": "use_tool", "tool_name": "math", ...}
    """

    def __init__(self, llm_client: LLMClient):
        """Initialize planner with LLM client.

        Args:
            llm_client: LLM client instance (MockLLMClient or real LLM)
        """
        self.llm = llm_client

    def plan_next_step(
        self,
        goal: str,
        context: str | None,
        available_tools: dict[str, Tool],
        execution_history: list[dict],
    ) -> dict[str, Any]:
        """Determine next action using LLM.

        The LLM analyzes the goal, available tools, and execution history
        to decide whether to use a tool or provide a direct answer.

        Args:
            goal: User's objective
            context: Optional additional context
            available_tools: Tools the agent can use (name -> Tool instance)
            execution_history: Previous execution steps as dicts

        Returns:
            Dict with action ("answer" or "use_tool") and relevant parameters:
            - action="answer": includes "final_answer"
            - action="use_tool": includes "tool_name" and "tool_input"
        """
        # Build system prompt describing tools and expected behavior
        system_prompt = self._build_system_prompt(available_tools)

        # Build user prompt with goal, context, and history
        user_prompt = self._build_planning_prompt(
            goal, context, available_tools, execution_history
        )

        # Ask LLM to decide next action
        response = self.llm.generate(user_prompt, system_prompt)

        return response

    def _build_system_prompt(self, available_tools: dict[str, Tool]) -> str:
        """Build system prompt describing available tools and expected behavior.

        This prompt tells the LLM:
        - What tools are available
        - How to use each tool
        - What format to respond in

        Args:
            available_tools: Available tool instances

        Returns:
            Formatted system prompt string
        """
        tool_descriptions = []

        for tool_name, tool in available_tools.items():
            # Format each tool's description and schema
            tool_descriptions.append(
                f"- **{tool_name}**: {tool.description}\n"
                f"  Input schema: {tool.input_schema}"
            )

        system_prompt = f"""
        You are an AI agent that can use tools to accomplish tasks.

        Available tools:
        {chr(10).join(tool_descriptions)}

        Your job is to analyze the user's goal and decide:
        1. If you can answer directly without tools, respond with action: "answer"
        2. If you need to use a tool, respond with action: "use_tool" and specify tool_name and tool_input

        Always choose the most appropriate tool for the task.
        Provide clear reasoning for your decision.
        """

        return system_prompt

    def _build_planning_prompt(
        self,
        goal: str,
        context: str | None,
        available_tools: dict[str, Tool],
        execution_history: list[dict],
    ) -> str:
        """Build user prompt for next step planning.

        Includes:
        - The goal to achieve
        - Optional context
        - Execution history (what's been done so far)
        - Question: what should be the next step?

        Args:
            goal: User's goal
            context: Optional context
            available_tools: Available tools (for reference)
            execution_history: Previous steps

        Returns:
            Formatted prompt string
        """
        prompt_parts = [f"Goal: {goal}"]

        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}")

        # Add execution history if any steps have been completed
        if execution_history:
            prompt_parts.append("\nExecution history:")
            for step in execution_history:
                step_num = step.get("step", "?")
                tool_name = step.get("tool", "unknown")
                tool_input = step.get("input", {})
                tool_output = step.get("output", "N/A")
                error = step.get("error")

                if error:
                    prompt_parts.append(
                        f"  Step {step_num}: Used {tool_name} "
                        f"with input {tool_input} -> ERROR: {error}"
                    )
                else:
                    prompt_parts.append(
                        f"  Step {step_num}: Used {tool_name} "
                        f"with input {tool_input} -> {tool_output}"
                    )

        # Ask for next step
        prompt_parts.append("\nWhat should be the next step?")

        return "\n".join(prompt_parts)
