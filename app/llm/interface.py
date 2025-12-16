"""LLM client interface definition.

Defines the Protocol for LLM client implementations, allowing the system
to swap between different LLM providers without changing agent code.

This abstraction supports:
- Mock LLM (for development/testing)
- Vercel AI SDK (future integration)
- OpenAI/Anthropic/other providers
- Custom "Sovereign AI CEO" models

The key is that all implementations follow the same interface contract.
"""

from typing import Protocol


class LLMResponse(dict):
    """Structured LLM response.

    This is a dict subclass for type clarity. Expected keys:

    - action: "answer" | "use_tool"
        Whether to answer directly or use a tool

    - tool_name: str (if action == "use_tool")
        Name of the tool to execute

    - tool_input: dict (if action == "use_tool")
        Input parameters for the tool

    - final_answer: str (if action == "answer")
        Direct answer without tool use

    - reasoning: str (optional)
        LLM's reasoning process (for debugging)

    Example (tool use):
        {
            "action": "use_tool",
            "tool_name": "math",
            "tool_input": {"expression": "2+2"},
            "reasoning": "User wants a calculation"
        }

    Example (direct answer):
        {
            "action": "answer",
            "final_answer": "Hello! How can I help you?",
            "reasoning": "Simple greeting, no tools needed"
        }
    """

    pass


class LLMClient(Protocol):
    """Protocol for LLM client implementations.

    This abstraction allows swapping between different LLM providers
    without changing the agent core logic.

    Implementations:
    - MockLLMClient: Pattern-based responses for testing
    - VercelLLMClient: Integration with Vercel AI SDK (future)
    - OpenAIClient: Direct OpenAI API integration (future)
    - AnthropicClient: Claude API integration (future)

    Example implementation:
        class MyLLMClient:
            def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
                # Call your LLM API here
                response = call_llm_api(prompt, system_prompt)
                return LLMResponse({
                    "action": "use_tool",
                    "tool_name": "math",
                    "tool_input": {"expression": "2+2"}
                })
    """

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """Generate a structured response from the LLM.

        The LLM should analyze the prompt and decide whether to:
        1. Answer directly (action: "answer")
        2. Use a tool (action: "use_tool")

        Args:
            prompt: User prompt or agent query
            system_prompt: Optional system-level instructions describing
                          available tools and expected response format

        Returns:
            LLMResponse dict with action and relevant parameters

        Note:
            In production implementations, use structured output modes:
            - OpenAI: function calling or JSON mode
            - Anthropic: tool use API
            - Vercel AI SDK: structured output helpers
        """
        ...
