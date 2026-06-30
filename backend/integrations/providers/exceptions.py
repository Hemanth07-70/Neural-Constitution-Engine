class ProviderException(Exception):
    """Base exception for all Provider errors."""

    pass


class ProviderAuthenticationError(ProviderException):
    """Raised when provider authentication fails."""

    pass


class ProviderRateLimitError(ProviderException):
    """Raised when provider rate limits are hit."""

    pass


class ProviderAPIError(ProviderException):
    """Raised when the provider API returns an error."""

    pass


class ProviderNotFoundError(ProviderException):
    """Raised when a requested provider is not registered."""

    pass


class ModelNotFoundError(ProviderException):
    """Raised when a requested model is not supported by the provider."""

    pass
