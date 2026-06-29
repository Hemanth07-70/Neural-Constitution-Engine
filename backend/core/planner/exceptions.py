"""Exceptions for the execution plan graph."""

class PlanError(Exception):
    """Base exception for all plan-related errors."""
    pass

class PlanGraphError(PlanError):
    """Raised when there is a structural error in the plan graph."""
    pass

class CycleDetectedError(PlanGraphError):
    """Raised when a cycle is detected during topological sorting."""
    pass

class ValidationError(PlanError):
    """Raised when a plan fails semantic validation."""
    pass
