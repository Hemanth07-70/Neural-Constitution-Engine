"""Public SDK Exceptions."""


class EngineError(Exception):
    """Base exception for all SDK errors."""

    pass


class ConfigurationError(EngineError):
    """Raised when the Engine is misconfigured."""

    pass


class ConstitutionValidationError(EngineError):
    """Raised when a constitution is structurally or semantically invalid."""

    pass


class EvaluationError(EngineError):
    """Raised when a request cannot be evaluated."""

    pass
