"""Central module exposing the Rule Engine interfaces."""

from .context import EvaluationContext, MatchResult, ResolvedVerdict
from .evaluator import RuleEvaluator
from .exceptions import MatcherError, PluginNotFoundError, ResolutionError, RuleEngineError
from .matcher import RuleMatcher
from .registry import RuleRegistry
from .resolver import RuleResolver

__all__ = [
    "EvaluationContext",
    "MatcherError",
    "MatchResult",
    "PluginNotFoundError",
    "ResolutionError",
    "ResolvedVerdict",
    "RuleEngineError",
    "RuleEvaluator",
    "RuleMatcher",
    "RuleRegistry",
    "RuleResolver",
]
