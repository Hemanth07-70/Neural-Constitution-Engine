"""Exceptions for the deterministic evaluation pipeline."""


class EvaluatorError(Exception):
    """Base exception for all evaluator errors."""

    pass


class PipelineError(EvaluatorError):
    """Raised if the pipeline configuration or execution is invalid."""

    pass


class FailClosedError(EvaluatorError):
    """Internal error raised when the engine forcibly fails-closed."""

    pass
