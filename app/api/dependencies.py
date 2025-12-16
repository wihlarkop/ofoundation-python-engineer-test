"""Dependency injection for FastAPI endpoints.

Provides injectable dependencies for routes, following FastAPI best practices.
This allows for:
- Easy testing with mocked dependencies
- Centralized configuration
- Lifecycle management
- Swappable implementations
"""

from functools import lru_cache

from app.agent.core import Agent
from app.config import settings
from app.llm.interface import LLMClient
from app.llm.mock_client import MockLLMClient


@lru_cache
def get_llm_client() -> LLMClient:
    """Get LLM client instance.

    Factory function for LLM client. Uses @lru_cache for singleton pattern.

    Returns:
        LLMClient instance (currently MockLLMClient)

    Example:
        @app.get("/endpoint")
        async def endpoint(llm: LLMClient = Depends(get_llm_client)):
            ...
    """
    # Currently returns MockLLMClient
    # In production, switch based on settings.llm_provider

    if settings.llm_provider == "mock":
        return MockLLMClient()
    elif settings.llm_provider == "openai":
        # from app.llm.openai_client import OpenAIClient
        # return OpenAIClient(api_key=settings.llm_api_key)
        raise NotImplementedError("OpenAI client not implemented yet")
    elif settings.llm_provider == "anthropic":
        # from app.llm.anthropic_client import AnthropicClient
        # return AnthropicClient(api_key=settings.llm_api_key)
        raise NotImplementedError("Anthropic client not implemented yet")
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


def get_agent() -> Agent:
    """Get Agent instance.

    Factory function for Agent. Creates a new instance on each call
    with the default LLM client.

    Returns:
        Agent instance

    Example:
        @app.post("/endpoint")
        async def endpoint(agent: Agent = Depends(get_agent)):
            result = agent.run(goal="...")
    """
    llm_client = get_llm_client()
    return Agent(llm_client=llm_client)


# Alternative: Async version for future async LLM clients
async def get_agent_async() -> Agent:
    """Async version of get_agent for future async LLM clients.

    Currently just wraps the sync version, but provides
    a hook for async initialization in the future.

    Returns:
        Agent instance
    """
    return get_agent()
