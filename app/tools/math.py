"""Safe mathematical expression evaluator tool.

Uses AST (Abstract Syntax Tree) parsing to safely evaluate arithmetic
expressions without the security risks of eval() or exec().

Only whitelisted operators are allowed, preventing code injection attacks.
"""

import ast
import operator
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from app.tools.base import tool_registry


class MathInput(BaseModel):
    """Input schema for math tool."""

    expression: str = Field(
        ..., min_length=1, description="Mathematical expression to evaluate"
    )


class MathOutput(BaseModel):
    """Output schema for math tool."""

    result: float | int = Field(..., description="Calculation result")
    expression: str = Field(..., description="Original expression")


class MathTool:
    """Safe mathematical expression evaluator.

    Security features:
    - AST parsing (no eval/exec)
    - Whitelisted operators only
    - No access to builtins or __import__
    - No function calls or attribute access

    Supported operations:
    - Addition: +
    - Subtraction: -
    - Multiplication: *
    - Division: /
    - Power: **
    - Unary minus: -x
    - Unary plus: +x
    - Parentheses for grouping

    Example expressions:
    - "2 + 2"
    - "(100 + 50) * 2"
    - "10 ** 2 - 5"
    - "-3 + 5"
    """

    # Whitelist of allowed operators with their implementations
    ALLOWED_OPERATORS: ClassVar = {
        ast.Add: operator.add,  # +
        ast.Sub: operator.sub,  # -
        ast.Mult: operator.mul,  # *
        ast.Div: operator.truediv,  # /
        ast.Pow: operator.pow,  # **
        ast.USub: operator.neg,  # unary -
        ast.UAdd: operator.pos,  # unary +
    }

    @property
    def name(self) -> str:
        return "math"

    @property
    def description(self) -> str:
        return (
            "Evaluates mathematical expressions safely. "
            "Supports: +, -, *, /, ** (power), parentheses. "
            "Input: {'expression': '2 + 2'}. "
            "Returns: numeric result."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return MathInput.model_json_schema()

    def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute safe mathematical evaluation.

        Args:
            input: Dict with 'expression' key

        Returns:
            Dict with 'result' and 'expression'

        Raises:
            ValueError: If expression is invalid or uses disallowed operators
        """
        # Validate input
        validated_input = MathInput(**input)
        expression = validated_input.expression

        try:
            result = self._safe_eval(expression)
            output = MathOutput(result=result, expression=expression)
            return output.model_dump()
        except Exception as e:
            raise ValueError(f"Math evaluation failed: {e!s}")

    def _safe_eval(self, expression: str) -> float | int:
        """Safely evaluate mathematical expression using AST.

        Args:
            expression: String containing mathematical expression

        Returns:
            Numeric result

        Raises:
            ValueError: If expression is invalid or uses disallowed operations
        """
        try:
            # Parse expression into AST
            tree = ast.parse(expression, mode="eval")
            # Evaluate the AST recursively
            return self._eval_node(tree.body)
        except SyntaxError:
            raise ValueError(f"Invalid mathematical expression: {expression}")

    def _eval_node(self, node):
        """Recursively evaluate AST nodes.

        This is the core security mechanism - only whitelisted
        node types and operators are evaluated.

        Args:
            node: AST node to evaluate

        Returns:
            Evaluated value

        Raises:
            ValueError: If node type or operator is not allowed
        """
        # Constant value (number)
        if isinstance(node, ast.Constant):
            return node.value

        # Binary operation (e.g., 2 + 3)
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)

            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} not allowed")

            return self.ALLOWED_OPERATORS[op_type](left, right)

        # Unary operation (e.g., -5)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)

            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} not allowed")

            return self.ALLOWED_OPERATORS[op_type](operand)

        # Anything else is not allowed
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")


# Auto-register tool on module import
tool_registry.register(MathTool())
