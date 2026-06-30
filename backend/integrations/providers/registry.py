from backend.integrations.providers.base import BaseAIProvider
from backend.integrations.providers.exceptions import ProviderNotFoundError


class ProviderRegistry:
    """Dynamic registry for AI Provider implementations."""

    _providers: dict[str, type[BaseAIProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: type[BaseAIProvider]) -> None:
        """Registers a provider class under a given name."""
        cls._providers[name] = provider_cls

    @classmethod
    def remove(cls, name: str) -> None:
        """Removes a registered provider."""
        if name in cls._providers:
            del cls._providers[name]

    @classmethod
    def get(cls, name: str) -> type[BaseAIProvider]:
        """Gets a provider class by name."""
        if name not in cls._providers:
            raise ProviderNotFoundError(f"Provider '{name}' is not registered.")
        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        """Lists all registered providers."""
        return list(cls._providers.keys())
