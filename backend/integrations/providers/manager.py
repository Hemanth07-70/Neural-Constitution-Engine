import time
from collections.abc import AsyncGenerator

from backend.integrations.providers.base import BaseAIProvider
from backend.integrations.providers.exceptions import ProviderException
from backend.integrations.providers.models import ProviderRequest, ProviderResponse
from backend.integrations.providers.registry import ProviderRegistry
from backend.integrations.providers.telemetry import log_telemetry


class ProviderManager:
    """Manages AI Provider lifecycle, failovers, and telemetry logging."""

    @staticmethod
    async def get_provider(name: str) -> BaseAIProvider:
        """Retrieves a provider instance by name."""
        provider_cls = ProviderRegistry.get(name)
        return provider_cls()

    @staticmethod
    async def generate(request: ProviderRequest, provider_name: str, max_retries: int = 3) -> ProviderResponse:
        """Executes a generation request with automatic retries and telemetry logging."""
        provider = await ProviderManager.get_provider(provider_name)

        retries = 0
        last_error = None

        while retries <= max_retries:
            start_time = time.time()
            try:
                response = await provider.generate(request)
                latency_ms = (time.time() - start_time) * 1000

                await log_telemetry(
                    provider_name=provider_name,
                    model_name=request.model,
                    success=True,
                    latency_ms=latency_ms,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    retries=retries,
                    organization_id=request.organization_id,
                )
                return response

            except ProviderException as e:
                last_error = e
                latency_ms = (time.time() - start_time) * 1000
                retries += 1

                if retries > max_retries:
                    await log_telemetry(
                        provider_name=provider_name,
                        model_name=request.model,
                        success=False,
                        latency_ms=latency_ms,
                        error_message=str(e),
                        retries=retries - 1,
                        organization_id=request.organization_id,
                    )
                    raise last_error

    @staticmethod
    async def stream(request: ProviderRequest, provider_name: str) -> AsyncGenerator[str, None]:
        """Streams a completion. Note: Telemetry for streaming is more complex and often omitted or logged at the end."""
        provider = await ProviderManager.get_provider(provider_name)
        # Note: True streaming telemetry requires a wrapper around the generator
        async for chunk in provider.stream(request):
            yield chunk

    @staticmethod
    async def health(provider_name: str) -> bool:
        try:
            provider = await ProviderManager.get_provider(provider_name)
            return await provider.health()
        except Exception:
            return False
