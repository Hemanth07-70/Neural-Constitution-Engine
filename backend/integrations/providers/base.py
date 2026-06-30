import abc
from collections.abc import AsyncGenerator

from backend.integrations.providers.models import EmbeddingRequest, EmbeddingResponse, ProviderRequest, ProviderResponse


class BaseAIProvider(abc.ABC):
    """Abstract base class for all AI Providers in the integration layer."""

    @abc.abstractmethod
    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generates a completion from the provider."""
        pass

    @abc.abstractmethod
    async def stream(self, request: ProviderRequest) -> AsyncGenerator[str, None]:
        """Streams a completion from the provider."""
        pass

    @abc.abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generates embeddings from the provider."""
        pass

    @abc.abstractmethod
    async def health(self) -> bool:
        """Checks if the provider API is accessible and healthy."""
        pass

    @abc.abstractmethod
    async def models(self) -> list[str]:
        """Returns a list of supported models by this provider."""
        pass

    @abc.abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Counts the number of tokens in a given text for a model."""
        pass
