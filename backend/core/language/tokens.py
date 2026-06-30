"""Token definitions and Lexer for the Constitution Language."""

import re
from dataclasses import dataclass
from enum import Enum, auto

from .exceptions import LexError


class TokenType(Enum):
    """Types of tokens in the language."""

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()

    # Operators
    AND = auto()
    OR = auto()
    NOT = auto()
    IN = auto()
    CONTAINS = auto()
    STARTS_WITH = auto()
    ENDS_WITH = auto()
    REGEX = auto()
    EXISTS = auto()

    EQ = auto()  # ==
    EQ_SINGLE = auto()  # =
    NEQ = auto()  # !=
    LT = auto()  # <
    LTE = auto()  # <=
    GT = auto()  # >
    GTE = auto()  # >=

    # Syntax
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,

    EOF = auto()


@dataclass(slots=True, frozen=True)
class Token:
    """A lexical token."""

    type: TokenType
    value: str
    position: int


class Lexer:
    """Regex-based lexical analyzer."""

    # Keywords mapped to token types
    KEYWORDS = {
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "in": TokenType.IN,
        "contains": TokenType.CONTAINS,
        "starts_with": TokenType.STARTS_WITH,
        "ends_with": TokenType.ENDS_WITH,
        "regex": TokenType.REGEX,
        "exists": TokenType.EXISTS,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "null": TokenType.NULL,
    }

    # Regex rules
    # Note: ORDER MATTERS! e.g., == must come before =
    RULES = [
        (r"\s+", None),  # Whitespace
        (r"==?", TokenType.EQ),  # == or =
        (r"!=", TokenType.NEQ),  # !=
        (r"<=", TokenType.LTE),  # <=
        (r">=", TokenType.GTE),  # >=
        (r"<", TokenType.LT),  # <
        (r">", TokenType.GT),  # >
        (r"\(", TokenType.LPAREN),  # (
        (r"\)", TokenType.RPAREN),  # )
        (r"\[", TokenType.LBRACKET),  # [
        (r"\]", TokenType.RBRACKET),  # ]
        (r",", TokenType.COMMA),  # ,
        (r"-?\d+\.\d+", TokenType.NUMBER),  # Float
        (r"-?\d+", TokenType.NUMBER),  # Integer
        (r"'([^'\\]*(?:\\.[^'\\]*)*)'", TokenType.STRING),  # Single-quoted string
        (r'"([^"\\]*(?:\\.[^"\\]*)*)"', TokenType.STRING),  # Double-quoted string
        (r"[a-zA-Z_][a-zA-Z0-9_\.]*", TokenType.IDENTIFIER),  # Identifier
    ]

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.tokens: list[Token] = []

        # Compile rules with named groups to avoid index shifting
        parts = []
        self.rule_types = {}
        for i, (regex, token_type) in enumerate(self.RULES):
            name = f"R{i}"
            parts.append(f"(?P<{name}>{regex})")
            self.rule_types[name] = token_type
        self.master_regex = re.compile("|".join(parts))

    def tokenize(self) -> list[Token]:
        """Convert the source string into a list of Tokens."""
        while self.pos < len(self.source):
            match = self.master_regex.match(self.source, self.pos)
            if not match:
                raise LexError(f"Unexpected character: {self.source[self.pos]}", self.pos)

            name = match.lastgroup
            value = match.group(name)
            token_type = self.rule_types[name]

            if token_type is not None:
                # Handle Keywords
                if token_type == TokenType.IDENTIFIER:
                    lower_val = value.lower()
                    if lower_val in self.KEYWORDS:
                        token_type = self.KEYWORDS[lower_val]

                # Handle Strings (remove quotes and handle escapes)
                if token_type == TokenType.STRING:
                    # groups are indexed 1-based, we have to find which group matched
                    # Actually, we can just strip the first and last char
                    val_str = value[1:-1]
                    # basic unescaping for quotes
                    val_str = val_str.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
                    value = val_str

                # Special handle for EQ / EQ_SINGLE
                if token_type == TokenType.EQ:
                    if value == "=":
                        token_type = TokenType.EQ_SINGLE

                self.tokens.append(Token(type=token_type, value=value, position=self.pos))

            self.pos = match.end()

        self.tokens.append(Token(type=TokenType.EOF, value="", position=self.pos))
        return self.tokens
