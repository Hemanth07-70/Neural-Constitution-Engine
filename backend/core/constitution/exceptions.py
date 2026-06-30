"""Typed exceptions for the Constitution Loader."""


class ConstitutionLoaderError(Exception):
    """Base exception for all constitution loader errors."""


class ConstitutionParseError(ConstitutionLoaderError):
    """Raised when the constitution file (JSON/YAML) is syntactically malformed."""


class ConstitutionValidationError(ConstitutionLoaderError):
    """Raised when the loaded data fails structural validation (missing keys, bad types)."""
