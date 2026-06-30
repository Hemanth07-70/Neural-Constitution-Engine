from collections.abc import AsyncGenerator

import httpx

from backend.integrations.providers.base import BaseAIProvider
from backend.integrations.providers.config import provider_settings
from backend.integrations.providers.exceptions import ProviderAPIError
from backend.integrations.providers.models import (
    ChatMessage,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderRequest,
    ProviderResponse,
)


class AnthropicProvider(BaseAIProvider):
    """Anthropic API provider implementation."""

    def __init__(self):
        self.api_key = provider_settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        system_message = ""
        messages = []
        for m in request.messages:
            if m.role == "system":
                system_message += m.content + "\n"
            else:
                messages.append({"role": "user" if m.role == "user" else "assistant", "content": m.content})

        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
            "system": system_message.strip() if system_message else None,
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            )

            if response.status_code != 200:
                raise ProviderAPIError(f"Anthropic API Error: {response.text}")

            data = response.json()
            usage = data.get("usage", {})

            content = data["content"][0]["text"] if data.get("content") else ""

            return ProviderResponse(
                message=ChatMessage(role="assistant", content=content),
                model=data["model"],
                provider="anthropic",
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            )

    async def stream(self, request: ProviderRequest) -> AsyncGenerator[str, None]:
        system_message = ""
        messages = []
        for m in request.messages:
            if m.role == "system":
                system_message += m.content + "\n"
            else:
                messages.append({"role": "user" if m.role == "user" else "assistant", "content": m.content})

        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
            "system": system_message.strip() if system_message else None,
            "stream": True,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            ) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise ProviderAPIError(f"Anthropic API Error: {text.decode('utf-8')}")

                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        import json

                        try:
                            data = json.loads(chunk[6:])
                            if data.get("type") == "content_block_delta":
                                yield data["delta"]["text"]
                        except Exception:
                            pass

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        # Anthropic doesn't have a public embedding API in the same way, return mock
        raise NotImplementedError("Anthropic does not currently support embeddings via this API.")

    async def health(self) -> bool:
        # Anthropic doesn't have a simple health endpoint without using models, mock it
        return True

    async def models(self) -> list[str]:
        return ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]

    def count_tokens(self, text: str, model: str) -> int:
        return len(text) // 4
