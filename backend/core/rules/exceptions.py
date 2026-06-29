"""Exceptions for the Rule Engine."""

class RuleEngineError(Exception):
    """Base class for all rule engine exceptions."""


class PluginNotFoundError(RuleEngineError):
    """Raised when a requested plugin (evaluator or transform) is not found in the registry."""


class MatcherError(RuleEngineError):
    """Raised when a rule matcher encounters an unrecoverable error evaluating a condition."""


class ResolutionError(RuleEngineError):
    """Raised when the resolver fails to deterministically resolve conflicts."""
