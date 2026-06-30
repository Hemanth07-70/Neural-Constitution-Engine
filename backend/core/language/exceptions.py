"""Typed exceptions for the Constitution Language."""


class LanguageError(Exception):
    """Base exception for Constitution Language errors."""

    pass


class LexError(LanguageError):
    """Raised when the tokenizer encounters invalid syntax."""

    def __init__(self, message: str, position: int) -> None:
        super().__init__(message)
        self.position = position


class ParseError(LanguageError):
    """Raised when the parser encounters unexpected tokens."""

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.position = position


class EvaluationError(LanguageError):
    """Raised when an expression fails to evaluate at runtime."""

    pass
