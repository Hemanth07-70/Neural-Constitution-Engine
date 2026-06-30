"""Evaluator for the Constitution Language AST."""

import re
from typing import Any

from backend.core.rules.context import EvaluationContext

from .ast import ArrayLiteral, ASTNode, BinaryOp, Identifier, Literal, UnaryOp
from .exceptions import EvaluationError
from .tokens import TokenType


class LanguageEvaluator:
    """Evaluates an AST against an EvaluationContext."""

    def __init__(self, context: EvaluationContext) -> None:
        self.context = context

    def evaluate(self, node: ASTNode) -> Any:
        """Evaluate a node and return its value."""
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, Identifier):
            return self._resolve_field(node.name)

        if isinstance(node, ArrayLiteral):
            return tuple(self.evaluate(e) for e in node.elements)

        if isinstance(node, UnaryOp):
            return self._evaluate_unary(node)

        if isinstance(node, BinaryOp):
            return self._evaluate_binary(node)

        raise EvaluationError(f"Unknown AST node type: {type(node)}")

    def _resolve_field(self, path: str) -> Any:
        """Resolve a dot-notation path from the evaluation context request.

        Returns None (null) if the field does not exist.
        """
        if not path:
            return None

        # Base root is the request object
        current = self.context.request

        # We also might want to resolve fields off the context itself, e.g. context.system_state?
        # But for now, everything is under the request structure (which has request.context, request.action etc)
        # However, to allow "action.type" directly, we assume the root is the request object.
        parts = path.split(".")

        for part in parts:
            if current is None:
                return None

            # If it's a dict, use get()
            if isinstance(current, dict):
                current = current.get(part)
            # Otherwise use getattr()
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None

        # If it's an enum, we unwrap the value for ease of evaluation
        from enum import Enum

        if isinstance(current, Enum):
            return current.value

        return current

    def _evaluate_unary(self, node: UnaryOp) -> Any:
        # Note: For EXISTS, it does not evaluate the right side fully, it just checks for None
        # But wait, our `evaluate` returns None if missing. So `EXISTS` just checks if evaluate is not None.
        if node.op.type == TokenType.EXISTS:
            val = self.evaluate(node.right)
            return val is not None

        right = self.evaluate(node.right)

        if node.op.type == TokenType.NOT:
            return not bool(right)

        raise EvaluationError(f"Unknown unary operator: {node.op.type.name}")

    def _evaluate_binary(self, node: BinaryOp) -> Any:
        # Short-circuit logical operators
        if node.op.type == TokenType.AND:
            return bool(self.evaluate(node.left)) and bool(self.evaluate(node.right))
        if node.op.type == TokenType.OR:
            return bool(self.evaluate(node.left)) or bool(self.evaluate(node.right))

        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        op = node.op.type

        try:
            if op == TokenType.EQ:
                return left == right
            if op == TokenType.NEQ:
                return left != right
            if op == TokenType.LT:
                return left < right
            if op == TokenType.LTE:
                return left <= right
            if op == TokenType.GT:
                return left > right
            if op == TokenType.GTE:
                return left >= right

            if op == TokenType.IN:
                if not isinstance(right, (list, tuple, str)):
                    return False
                return left in right

            if op == TokenType.CONTAINS:
                if not isinstance(left, (list, tuple, str)):
                    return False
                return right in left

            if op == TokenType.STARTS_WITH:
                if not isinstance(left, str) or not isinstance(right, str):
                    return False
                return left.startswith(right)

            if op == TokenType.ENDS_WITH:
                if not isinstance(left, str) or not isinstance(right, str):
                    return False
                return left.endswith(right)

            if op == TokenType.REGEX:
                if not isinstance(left, str) or not isinstance(right, str):
                    return False
                return bool(re.search(right, left))

        except TypeError:
            # Type error during comparison (e.g., 5 < "str") evaluates to False
            return False

        raise EvaluationError(f"Unknown binary operator: {node.op.type.name}")
