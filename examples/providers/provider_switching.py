import asyncio

from backend.integrations.providers.manager import ProviderManager
from backend.integrations.providers.models import ChatMessage, ProviderRequest
from backend.integrations.providers.registry import ProviderRegistry


async def main():
    print("AI Provider Switching Demo")
    print("=" * 40)

    # We will test each registered provider
    providers = ProviderRegistry.list_providers()

    request = ProviderRequest(
        messages=[ChatMessage(role="user", content="Say hello!")],
        model="test-model",  # Models vary by provider
        temperature=0.7,
    )

    for provider in providers:
        print(f"\n--- Testing Provider: {provider.upper()} ---")

        is_healthy = await ProviderManager.health(provider)
        print(f"Health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")

        if is_healthy:
            # We mock the actual generation to prevent failure without API keys during demo runs.
            # In a real environment, ProviderManager.generate(request, provider) is used.
            try:
                # Update model to something valid based on provider
                models = await ProviderManager.get_provider(provider)
                available = await models.models()
                request.model = available[0] if available else "gpt-4o"

                print(f"Requesting completion from {provider} using {request.model}...")
                response = await ProviderManager.generate(request, provider_name=provider)
                print(f"Response: {response.message.content}")
                print(f"Tokens: {response.total_tokens}")
            except Exception as e:
                print(f"Execution skipped/failed (likely due to missing keys): {e}")


if __name__ == "__main__":
    asyncio.run(main())
