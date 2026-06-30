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


class OllamaProvider(BaseAIProvider):
    """Ollama API provider implementation."""

    def __init__(self):
        self.base_url = provider_settings.ollama_base_url
        self.headers = {"Content-Type": "application/json"}

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        payload = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            )

            if response.status_code != 200:
                raise ProviderAPIError(f"Ollama API Error: {response.text}")

            data = response.json()
            message = data.get("message", {})

            return ProviderResponse(
                message=ChatMessage(role=message.get("role", "assistant"), content=message.get("content", "")),
                model=data.get("model", request.model),
                provider="ollama",
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            )

    async def stream(self, request: ProviderRequest) -> AsyncGenerator[str, None]:
        payload = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "stream": True,
            "options": {
                "temperature": request.temperature,
            },
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                headers=self.headers,
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            ) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise ProviderAPIError(f"Ollama API Error: {text.decode('utf-8')}")

                async for chunk in response.aiter_lines():
                    if chunk:
                        import json

                        try:
                            data = json.loads(chunk)
                            message = data.get("message", {})
                            if "content" in message:
                                yield message["content"]
                        except Exception:
                            pass

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        inputs = [request.input] if isinstance(request.input, str) else request.input
        embeddings = []

        async with httpx.AsyncClient() as client:
            for inp in inputs:
                payload = {"model": request.model, "prompt": inp}
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    headers=self.headers,
                    json=payload,
                    timeout=provider_settings.provider_timeout_seconds,
                )
                if response.status_code != 200:
                    raise ProviderAPIError(f"Ollama API Error: {response.text}")

                data = response.json()
                embeddings.append(data.get("embedding", []))

        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model,
            provider="ollama",
            total_tokens=0,  # Ollama doesn't return token count for embeddings yet
        )

    async def health(self) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
            except Exception:
                return False

    async def models(self) -> list[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
                return []
            except Exception:
                return []

    def count_tokens(self, text: str, model: str) -> int:
        return len(text) // 4
