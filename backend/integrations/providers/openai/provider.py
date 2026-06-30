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


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider implementation."""

    def __init__(self):
        self.api_key = provider_settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        payload = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            )

            if response.status_code != 200:
                raise ProviderAPIError(f"OpenAI API Error: {response.text}")

            data = response.json()
            message = data["choices"][0]["message"]
            usage = data.get("usage", {})

            return ProviderResponse(
                message=ChatMessage(role=message["role"], content=message.get("content", "")),
                model=data["model"],
                provider="openai",
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            )

    async def stream(self, request: ProviderRequest) -> AsyncGenerator[str, None]:
        payload = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            ) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise ProviderAPIError(f"OpenAI API Error: {text.decode('utf-8')}")

                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: ") and chunk != "data: [DONE]":
                        # Simplistic parsing for demo
                        import json

                        data = json.loads(chunk[6:])
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        payload = {"model": request.model, "input": request.input}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            )
            if response.status_code != 200:
                raise ProviderAPIError(f"OpenAI API Error: {response.text}")

            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]
            usage = data.get("usage", {})

            return EmbeddingResponse(
                embeddings=embeddings, model=request.model, provider="openai", total_tokens=usage.get("total_tokens", 0)
            )

    async def health(self) -> bool:
        # Check models endpoint as a health check
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/models", headers=self.headers, timeout=5.0)
            return response.status_code == 200

    async def models(self) -> list[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/models", headers=self.headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
            return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    def count_tokens(self, text: str, model: str) -> int:
        # Simplistic token counting (approx 4 chars per token)
        return len(text) // 4
