"""Recursive descent parser for the Constitution Language."""

from .ast import ArrayLiteral, ASTNode, BinaryOp, Identifier, Literal, UnaryOp
from .exceptions import ParseError
from .tokens import Token, TokenType


class Parser:
    """Parses a list of tokens into an AST."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def _advance(self) -> Token:
        if self._peek().type != TokenType.EOF:
            self.pos += 1
        return self._previous()

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._peek().type == t:
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, error_message: str) -> Token:
        if self._peek().type == token_type:
            return self._advance()
        raise ParseError(error_message, self._peek().position)

    def parse(self) -> ASTNode:
        """Parse the token stream into an AST."""
        if len(self.tokens) == 0 or self._peek().type == TokenType.EOF:
            # Empty program?
            raise ParseError("Empty expression")
        node = self._expression()
        if self._peek().type != TokenType.EOF:
            raise ParseError(f"Unexpected token {self._peek().value}", self._peek().position)
        return node

    def _expression(self) -> ASTNode:
        return self._logical_or()

    def _logical_or(self) -> ASTNode:
        expr = self._logical_and()
        while self._match(TokenType.OR):
            op = self._previous()
            right = self._logical_and()
            expr = BinaryOp(left=expr, op=op, right=right)
        return expr

    def _logical_and(self) -> ASTNode:
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous()
            right = self._equality()
            expr = BinaryOp(left=expr, op=op, right=right)
        return expr

    def _equality(self) -> ASTNode:
        expr = self._relational()
        while self._match(TokenType.EQ, TokenType.EQ_SINGLE, TokenType.NEQ):
            op = self._previous()
            # Normalize single = to EQ for evaluation ease
            if op.type == TokenType.EQ_SINGLE:
                op = Token(type=TokenType.EQ, value="==", position=op.position)
            right = self._relational()
            expr = BinaryOp(left=expr, op=op, right=right)
        return expr

    def _relational(self) -> ASTNode:
        expr = self._unary()
        while self._match(
            TokenType.LT,
            TokenType.LTE,
            TokenType.GT,
            TokenType.GTE,
            TokenType.IN,
            TokenType.CONTAINS,
            TokenType.STARTS_WITH,
            TokenType.ENDS_WITH,
            TokenType.REGEX,
        ):
            op = self._previous()
            right = self._unary()
            expr = BinaryOp(left=expr, op=op, right=right)
        return expr

    def _unary(self) -> ASTNode:
        if self._match(TokenType.NOT, TokenType.EXISTS):
            op = self._previous()
            right = self._unary()
            return UnaryOp(op=op, right=right)
        return self._primary()

    def _primary(self) -> ASTNode:
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NULL):
            return Literal(None)

        if self._match(TokenType.NUMBER):
            val_str = self._previous().value
            if "." in val_str:
                return Literal(float(val_str))
            return Literal(int(val_str))

        if self._match(TokenType.STRING):
            return Literal(self._previous().value)

        if self._match(TokenType.IDENTIFIER):
            return Identifier(self._previous().value)

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expr

        if self._match(TokenType.LBRACKET):
            elements = []
            if self._peek().type != TokenType.RBRACKET:
                elements.append(self._expression())
                while self._match(TokenType.COMMA):
                    elements.append(self._expression())
            self._consume(TokenType.RBRACKET, "Expected ']' after array elements.")
            return ArrayLiteral(tuple(elements))

        raise ParseError(f"Expected expression, got {self._peek().type.name}", self._peek().position)
