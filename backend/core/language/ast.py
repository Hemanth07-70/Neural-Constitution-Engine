"""Abstract Syntax Tree nodes for the Constitution Language."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .tokens import Token


class ASTNode(ABC):
    """Base class for all AST nodes."""

    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass(slots=True, frozen=True)
class Literal(ASTNode):
    """A literal value (string, number, boolean, null)."""

    value: Any

    def __str__(self) -> str:
        if self.value is None:
            return "null"
        elif isinstance(self.value, bool):
            return "true" if self.value else "false"
        elif isinstance(self.value, str):
            return f"'{self.value}'"
        return str(self.value)


@dataclass(slots=True, frozen=True)
class Identifier(ASTNode):
    """A field path identifier (e.g., action.type)."""

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(slots=True, frozen=True)
class ArrayLiteral(ASTNode):
    """An array of expressions."""

    elements: tuple[ASTNode, ...]

    def __str__(self) -> str:
        return "[" + ", ".join(str(e) for e in self.elements) + "]"


@dataclass(slots=True, frozen=True)
class BinaryOp(ASTNode):
    """A binary operation (AND, OR, ==, etc.)."""

    left: ASTNode
    op: Token
    right: ASTNode

    def __str__(self) -> str:
        return f"({self.left} {self.op.type.name} {self.right})"


@dataclass(slots=True, frozen=True)
class UnaryOp(ASTNode):
    """A unary operation (NOT, EXISTS)."""

    op: Token
    right: ASTNode

    def __str__(self) -> str:
        return f"({self.op.type.name} {self.right})"
