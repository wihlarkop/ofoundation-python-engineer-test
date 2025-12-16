"""Web search tool with mock implementation.

In production, this would integrate with a real search API
(Google Custom Search, Bing Search API, Brave Search, DuckDuckGo, etc.).

For this demo, it returns realistic mock results based on the query.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.tools.base import tool_registry


class WebSearchInput(BaseModel):
    """Input schema for web search tool."""

    query: str = Field(..., min_length=1, description="Search query string")


class WebSearchOutput(BaseModel):
    """Output schema for web search tool."""

    results: list[dict[str, str]] = Field(..., description="List of search results")
    query: str = Field(..., description="Original query")


class WebSearchTool:
    """Mock web search tool returning realistic but fake results.

    The mock implementation demonstrates the tool interface and provides
    deterministic results for testing without external API dependencies.

    Extension path for real implementation:
    1. Add search API client (e.g., Brave Search, SerpAPI)
    2. Replace _generate_mock_results with real API call
    3. Add API key to configuration
    4. Keep the same interface - no changes needed elsewhere
    """

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Searches the web for information. "
            "Input: {'query': 'search terms'}. "
            "Returns: list of relevant web results with titles, URLs, and snippets."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return WebSearchInput.model_json_schema()

    def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute web search with mock results.

        Args:
            input: Dict with 'query' key

        Returns:
            Dict with 'results' (list of search results) and 'query'

        Raises:
            ValueError: If input validation fails
        """
        # Validate input using Pydantic
        validated_input = WebSearchInput(**input)
        query = validated_input.query

        # Generate mock results based on query
        mock_results = self._generate_mock_results(query)

        # Return validated output
        output = WebSearchOutput(results=mock_results, query=query)
        return output.model_dump()

    def _generate_mock_results(self, query: str) -> list[dict[str, str]]:
        """Generate realistic mock search results.

        Creates deterministic but contextually relevant results
        based on the query content.
        """
        # Clean query for URL generation
        query_slug = query.lower().replace(" ", "-")

        results = [
            {
                "title": f"Understanding {query}: A Comprehensive Guide",
                "url": f"https://example.com/guide/{query_slug}",
                "snippet": (
                    f"Learn everything about {query} with this detailed guide covering "
                    f"best practices, examples, and common pitfalls. Updated for 2025."
                ),
            },
            {
                "title": f"{query} - Official Documentation",
                "url": f"https://docs.example.com/{query_slug}",
                "snippet": (
                    f"Official documentation for {query}. Includes API reference, "
                    f"tutorials, and migration guides."
                ),
            },
            {
                "title": f"Top 10 Tips for {query}",
                "url": f"https://blog.example.com/tips/{query_slug}",
                "snippet": (
                    f"Discover the top 10 expert tips for mastering {query}. "
                    f"From beginners to advanced users."
                ),
            },
        ]

        return results


# Auto-register tool on module import
tool_registry.register(WebSearchTool())
