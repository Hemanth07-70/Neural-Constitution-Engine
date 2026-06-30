"""Fuzz testing script for the Constitution Language."""
import os
import random
import string
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from backend.core.language.exceptions import LanguageError
from backend.core.language.parser import Parser
from backend.core.language.tokens import Lexer


def generate_random_string(length: int) -> str:
    """Generate a random string of characters."""
    chars = string.ascii_letters + string.digits + " \t\n!@#$%^&*()_+-=[]{}|;':\",./<>?"
    return "".join(random.choice(chars) for _ in range(length))


def generate_mutated_valid_string() -> str:
    """Mutate a valid DSL string."""
    base = "action.type == 'deploy' and action.params.vulns < 0 or exists context.project_id"
    # mutate some chars
    chars = list(base)
    for _ in range(random.randint(1, 5)):
        idx = random.randint(0, len(chars) - 1)
        chars[idx] = random.choice(string.printable)
    return "".join(chars)


def fuzz(iterations: int = 10000):
    print(f"Starting Fuzz Test with {iterations} iterations...")
    passed = 0
    crashed = 0

    for i in range(iterations):
        if random.random() > 0.5:
            source = generate_random_string(random.randint(1, 100))
        else:
            source = generate_mutated_valid_string()

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            parser.parse()
            # If it passes, it's remarkably valid syntax
            passed += 1
        except LanguageError:
            # Expected failures: lexer or parser error
            passed += 1
        except Exception as e:
            # UNEXPECTED ERROR (Crash)
            print(f"CRASH: {e} on input: {repr(source)}")
            crashed += 1

    print("Fuzzing Complete.")
    print(f"Handled gracefully (Valid or typed LanguageError): {passed}")
    print(f"Crashed ungracefully: {crashed}")

    if crashed > 0:
        sys.exit(1)


if __name__ == "__main__":
    fuzz(20000)
