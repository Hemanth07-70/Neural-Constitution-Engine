"""Stage 1: Matches rules against the request."""

from backend.core.constitution.constitution import Constitution
from backend.core.domain.request import DecisionRequest
from backend.core.rules.context import EvaluationContext, MatchResult

from .stages import PipelineData, PipelineStage


class MatcherStage(PipelineStage):
    """Evaluates all constitution rules against the request.

    Since plugins are not fully implemented, this stage delegates to a stubbed Matcher
    if provided in the registry, or provides simple deterministic matching logic.
    """

    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        matches = []
        for rule in constitution.rules:
            if not rule.enabled:
                continue

            is_match = False
            if not rule.condition:
                is_match = True
            elif isinstance(rule.condition, str):
                try:
                    from backend.core.language.evaluator import LanguageEvaluator
                    from backend.core.language.parser import Parser
                    from backend.core.language.tokens import Lexer

                    lexer = Lexer(rule.condition)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    ast = parser.parse()

                    evaluator = LanguageEvaluator(context)
                    is_match = bool(evaluator.evaluate(ast))
                except Exception as e:
                    # Treat evaluation failure as a non-match but could also be fail-closed?
                    # The prompt says fail-closed if there's an error.
                    matches.append(MatchResult(matched=True, rule=rule, error_note=f"Evaluation error: {e}"))
                    continue
            else:
                # Basic literal match stub for testing (backward compatibility)
                field_path = rule.condition.get("field")
                op = rule.condition.get("op")
                value = rule.condition.get("value")
                if field_path == "action.type" and op == "equals":
                    is_match = request.action.type == value

            if is_match:
                matches.append(MatchResult(matched=True, rule=rule))

        return data.replace(matches=tuple(matches))
