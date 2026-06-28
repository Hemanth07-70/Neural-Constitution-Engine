"""Neural Constitution Engine — framework-independent core.

This package holds the pure, dependency-free heart of NCE. It must never import
a web framework, a database driver, an HTTP client, or any third-party library.
See ``docs/architecture.md`` for the rule that dependencies always point inward,
toward this core.

Subpackages
-----------
domain
    The canonical Decision Model entities (see ``docs/decision-model.md``).
"""
