from backend.api.adapters import to_sdk_decision_request
from backend.api.schemas.evaluate import DecisionRequestSchema
from backend.core.language.evaluator import LanguageEvaluator
from backend.core.language.parser import Parser
from backend.core.language.tokens import Lexer, TokenType
from backend.core.rules.context import EvaluationContext


def test_lexer():
    source = "action.type == 'deploy' and exists action.params.cab_approved"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "action.type"
    assert tokens[1].type == TokenType.EQ
    assert tokens[2].type == TokenType.STRING
    assert tokens[2].value == "deploy"
    assert tokens[3].type == TokenType.AND
    assert tokens[4].type == TokenType.EXISTS
    assert tokens[5].type == TokenType.IDENTIFIER
    assert tokens[6].type == TokenType.EOF


def test_parser():
    source = "action.type == 'deploy' and (1 < 2 or not false)"
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    # just checking it parses without error
    assert ast is not None


def test_evaluator():
    req = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "actor": {"id": "urn:agent:devops", "type": "agent"},
        "action": {
            "type": "deploy",
            "params": {
                "environment": "production",
                "critical_vulns": 0,
                "cab_approved": True,
                "maintenance_window": "active",
                "has_rollback_plan": False,
            },
        },
        "context": {
            "constitution_id": "test",
            "constitution_version": "1.0",
            "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
            "environment": {"name": "production", "timestamp": "2026-06-29T00:00:00Z"},
        },
        "submitted_at": "2026-06-29T00:00:00Z",
    }

    r = to_sdk_decision_request(DecisionRequestSchema.model_validate(req))
    ctx = EvaluationContext(request=r, registry=None)
    evaluator = LanguageEvaluator(ctx)

    def evaluate(expr: str):
        lexer = Lexer(expr)
        parser = Parser(lexer.tokenize())
        return evaluator.evaluate(parser.parse())

    assert evaluate("action.type == 'deploy'") is True
    assert evaluate("action.params.environment == 'production'") is True
    assert evaluate("action.params.critical_vulns <= 0") is True
    assert evaluate("action.params.has_rollback_plan == false") is True
    assert evaluate("not action.params.has_rollback_plan") is True
    assert evaluate("exists action.params.cab_approved") is True
    assert evaluate("exists action.params.missing_field") is False
    assert evaluate("action.type in ['deploy', 'build']") is True
    assert evaluate("'prod' in action.params.environment") is True
    assert evaluate("action.params.environment starts_with 'prod'") is True
    assert evaluate("action.params.environment regex '^prod.*'") is True
    assert evaluate("1 == 1 and 2 == 2") is True
    assert evaluate("1 == 2 or 3 == 3") is True
