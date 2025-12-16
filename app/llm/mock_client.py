"""Mock LLM client with rule-based responses.

Simulates LLM behavior using pattern matching and heuristics.
No actual LLM API calls - perfect for development and testing.

In production, this would be replaced with real LLM integration:
- Vercel AI SDK (via API gateway or Node.js microservice)
- OpenAI API with function calling
- Anthropic Claude with tool use
- Custom fine-tuned models

The mock demonstrates the interface contract and provides functional
tool selection logic without external dependencies.
"""

import re

from app.llm.interface import LLMResponse


class MockLLMClient:
    """Mock LLM client with pattern-based responses.

    Simulates intelligent tool selection using keyword matching:
    - Math keywords → MathTool
    - Search keywords → WebSearchTool
    - Governance keywords → GovernanceNoteTool
    - Simple questions → Direct answer

    This provides deterministic, testable behavior without API costs.

    Example:
        client = MockLLMClient()
        response = client.generate("Calculate 2 + 2")
        # Returns: {"action": "use_tool", "tool_name": "math", ...}
    """

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """Generate mock LLM response based on pattern matching.

        Args:
            prompt: User query or agent prompt
            system_prompt: System instructions (not used in mock)

        Returns:
            LLMResponse with action and parameters
        """
        prompt_lower = prompt.lower()

        # Check patterns in order of specificity
        # More specific patterns first to avoid false positives

        # Governance patterns (check first - most specific)
        if self._is_governance_query(prompt_lower):
            return self._generate_governance_response(prompt)

        # Math patterns
        elif self._is_math_query(prompt_lower):
            return self._generate_math_response(prompt)

        # Search patterns
        elif self._is_search_query(prompt_lower):
            return self._generate_search_response(prompt)

        # Default: direct answer
        else:
            return self._generate_direct_answer(prompt)

    def _is_math_query(self, prompt: str) -> bool:
        """Check if prompt requires mathematical calculation.

        Looks for math-related keywords and numeric expressions.
        Checks for actual numbers to avoid false positives.
        """
        # Must contain at least one digit to be considered math
        if not re.search(r"\d", prompt):
            return False

        math_keywords = [
            "calculate",
            "compute",
            "solve",
            "evaluate",
            "sum",
            "product",
            "result of",
            "multiply",
            "divide",
            "add",
            "subtract",
        ]

        # Check for math operators with surrounding digits
        # This avoids matching "add note" but catches "add 2 + 2"
        math_operator_patterns = [
            r"\d+\s*[\+\-\*/]\s*\d+",  # 2 + 2, 10-5, etc.
            r"\d+\s*\*\*\s*\d+",  # 2 ** 3
        ]

        if any(re.search(pattern, prompt) for pattern in math_operator_patterns):
            return True

        # Check for "what is" followed by numbers/operators
        if re.search(r"what\s+is\s+[\d\s\+\-\*/\(\)\.]+", prompt):
            return True

        return any(keyword in prompt for keyword in math_keywords)

    def _is_search_query(self, prompt: str) -> bool:
        """Check if prompt requires web search.

        Looks for information-seeking keywords.
        """
        search_keywords = [
            "search",
            "find",
            "look up",
            "information about",
            "who is",
            "where is",
            "latest",
            "current",
            "research",
            "discover",
            "learn about",
        ]
        return any(keyword in prompt for keyword in search_keywords)

    def _is_governance_query(self, prompt: str) -> bool:
        """Check if prompt is about governance notes.

        Looks for governance-specific terminology.
        """
        governance_keywords = [
            "proposal",
            "governance",
            "note",
            "prop-",
            "add note",
            "record",
            "document decision",
        ]
        return any(keyword in prompt for keyword in governance_keywords)

    def _generate_math_response(self, prompt: str) -> LLMResponse:
        """Generate tool use response for math calculation.

        Extracts the mathematical expression from the prompt.
        """
        expression = self._extract_math_expression(prompt)

        return LLMResponse(
            {
                "action": "use_tool",
                "tool_name": "math",
                "tool_input": {"expression": expression},
                "reasoning": f"User requested calculation: {expression}",
            }
        )

    def _extract_math_expression(self, prompt: str) -> str:
        """Extract mathematical expression from prompt.

        Uses regex to find numeric expressions with operators.
        Falls back to cleaned prompt if no clear expression found.
        """
        # Remove common question words
        cleaned = re.sub(
            r"\b(calculate|compute|what is|evaluate|solve|result of|the)\b",
            "",
            prompt,
            flags=re.IGNORECASE,
        ).strip()

        # Look for numeric expression with operators
        # Matches: numbers, spaces, +, -, *, /, **, parentheses, decimals
        match = re.search(r"[\d\s\+\-\*/\(\)\.\*\*]+", cleaned)
        if match:
            expr = match.group().strip()
            # Clean up any trailing/leading operators
            expr = re.sub(r"^[\+\-\*/\s]+|[\+\-\*/\s]+$", "", expr)
            if expr:
                return expr

        # Fallback: return cleaned prompt
        return cleaned.strip("?. ")

    def _generate_search_response(self, prompt: str) -> LLMResponse:
        """Generate tool use response for web search.

        Extracts the search query from the prompt.
        """
        query = self._extract_search_query(prompt)

        return LLMResponse(
            {
                "action": "use_tool",
                "tool_name": "web_search",
                "tool_input": {"query": query},
                "reasoning": f"User needs information about: {query}",
            }
        )

    def _extract_search_query(self, prompt: str) -> str:
        """Extract search query from prompt.

        Removes question prefixes to get the core query.
        """
        # Remove common search prefixes
        cleaned = re.sub(
            r"\b(search for|find|look up|information about|who is|where is|what is|research|learn about)\b",
            "",
            prompt,
            flags=re.IGNORECASE,
        ).strip()

        # Remove question marks and trailing punctuation
        cleaned = cleaned.strip("?. ")

        return cleaned if cleaned else prompt

    def _generate_governance_response(self, prompt: str) -> LLMResponse:
        """Generate tool use response for governance notes.

        Extracts proposal ID and note content from the prompt.
        """
        proposal_id, note = self._extract_governance_info(prompt)

        return LLMResponse(
            {
                "action": "use_tool",
                "tool_name": "governance_note",
                "tool_input": {"proposal_id": proposal_id, "note": note},
                "reasoning": f"Adding note to proposal {proposal_id}",
            }
        )

    def _extract_governance_info(self, prompt: str) -> tuple[str, str]:
        """Extract proposal ID and note content.

        Returns:
            Tuple of (proposal_id, note_content)
        """
        # Look for proposal ID patterns (e.g., PROP-123, PROP-2025-001)
        proposal_match = re.search(r"(PROP-[\w\-]+)", prompt, re.IGNORECASE)

        if proposal_match:
            proposal_id = proposal_match.group(1).upper()
        else:
            proposal_id = "UNKNOWN"

        # Extract note content after the proposal ID
        # Pattern: "PROP-ID: note content" or "Add note to PROP-ID: note content"
        note = ""

        # Try to find content after proposal ID and colon
        pattern = rf"{re.escape(proposal_id)}[:\s]+(.+?)(?:\n|$)"
        note_match = re.search(pattern, prompt, re.IGNORECASE)

        if note_match:
            note = note_match.group(1).strip()
        else:
            # Try to find "note: content" pattern
            note_match = re.search(r'note[:\s]+"?([^"\n]+)"?', prompt, re.IGNORECASE)
            if note_match:
                note = note_match.group(1).strip()
            else:
                # Fallback: extract everything after "add note to PROP-ID:"
                fallback_match = re.search(
                    r"(?:add\s+)?note\s+to\s+PROP-[\w\-]+[:\s]+(.+?)(?:\n|$)",
                    prompt,
                    re.IGNORECASE,
                )
                if fallback_match:
                    note = fallback_match.group(1).strip()
                else:
                    note = "Note added via agent"

        # Clean up the note - remove trailing "What should be the next step?" etc.
        note = re.sub(r"\s*what should.*$", "", note, flags=re.IGNORECASE).strip()
        note = note.strip("?. ")

        return proposal_id, note

    def _generate_direct_answer(self, prompt: str) -> LLMResponse:
        """Generate direct answer without tool use.

        For simple queries that don't require tools.
        """
        return LLMResponse(
            {
                "action": "answer",
                "final_answer": (
                    f"I understand your query about '{prompt}'. "
                    f"This is a mock LLM response. In production, this would contain "
                    f"intelligent reasoning from a real LLM model."
                ),
                "reasoning": "Query doesn't require tool use - answering directly",
            }
        )
