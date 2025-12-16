"""Tool system foundation: Protocol definition and registry.

This module defines the contract that all tools must follow (Protocol)
and provides a centralized registry for tool discovery and access.

The Protocol-based approach (vs inheritance) offers:
- Flexible implementation (duck typing)
- No shared state between tools
- Easy mocking for tests
- Clear interface contract
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """Protocol defining the contract for all tools.

    Tools use structural typing (Protocol) rather than inheritance,
    allowing flexible implementations while maintaining a clear contract.

    This abstraction supports future extension: blockchain tools,
    API integration tools, database tools, etc.

    Example:
        class MyTool:
            @property
            def name(self) -> str:
                return "my_tool"

            @property
            def description(self) -> str:
                return "Does something useful"

            @property
            def input_schema(self) -> dict[str, Any]:
                return {"type": "object", "properties": {...}}

            def run(self, input: dict[str, Any]) -> dict[str, Any]:
                # Tool logic here
                return {"result": "success"}
    """

    @property
    def name(self) -> str:
        """Unique tool identifier (snake_case).

        Used by LLM to reference the tool and by registry for lookup.
        """
        ...

    @property
    def description(self) -> str:
        """Human-readable description for LLM tool selection.

        Should clearly explain:
        - What the tool does
        - What inputs it expects
        - What outputs it returns

        The LLM uses this to decide when to use the tool.
        """
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema describing expected input parameters.

        Used by:
        - LLM to understand how to call the tool
        - Pydantic for input validation
        - OpenAPI docs for API documentation

        Should be derived from a Pydantic model's .model_json_schema()
        """
        ...

    def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool with given input.

        Args:
            input: Dictionary matching the input_schema

        Returns:
            Dictionary containing tool execution results

        Raises:
            ValueError: If input validation fails
            Exception: If tool execution fails (tool-specific)
        """
        ...


class ToolRegistry:
    """Central registry for discovering and accessing tools.

    Provides a singleton pattern for tool management. Tools
    self-register by calling registry.register() on module import.

    Example:
        # In tool module
        tool_registry.register(MyTool())

        # In agent
        tools = tool_registry.get_all()
        math_tool = tool_registry.get("math")
    """

    def __init__(self):
        """Initialize empty registry."""
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool instance.

        Args:
            tool: Tool instance implementing the Tool protocol

        Raises:
            TypeError: If tool doesn't implement Tool protocol
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"{tool} does not implement Tool protocol")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Retrieve a tool by name.

        Args:
            name: Tool name (e.g., "math", "web_search")

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def get_all(self) -> dict[str, Tool]:
        """Get all registered tools.

        Returns:
            Dictionary mapping tool names to tool instances
        """
        return self._tools.copy()

    def get_tools_for_names(self, names: list[str]) -> dict[str, Tool]:
        """Get subset of tools by names.

        Args:
            names: List of tool names to retrieve

        Returns:
            Dictionary of available tools (missing names are skipped)
        """
        return {name: tool for name, tool in self._tools.items() if name in names}


# Global registry instance - tools self-register on import
tool_registry = ToolRegistry()
