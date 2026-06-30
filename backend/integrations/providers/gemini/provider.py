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


class GeminiProvider(BaseAIProvider):
    """Google Gemini API provider implementation."""

    def __init__(self):
        self.api_key = provider_settings.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        contents = []
        system_instruction = None
        for m in request.messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                contents.append({"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
            },
        }
        if request.max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = request.max_tokens
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{request.model}:generateContent?key={self.api_key}",
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            )

            if response.status_code != 200:
                raise ProviderAPIError(f"Gemini API Error: {response.text}")

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ProviderAPIError("Gemini API Error: No candidates returned.")

            content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            usage = data.get("usageMetadata", {})

            return ProviderResponse(
                message=ChatMessage(role="assistant", content=content),
                model=request.model,
                provider="gemini",
                prompt_tokens=usage.get("promptTokenCount", 0),
                completion_tokens=usage.get("candidatesTokenCount", 0),
                total_tokens=usage.get("totalTokenCount", 0),
            )

    async def stream(self, request: ProviderRequest) -> AsyncGenerator[str, None]:
        contents = []
        system_instruction = None
        for m in request.messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                contents.append({"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
            },
        }
        if request.max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = request.max_tokens
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/{request.model}:streamGenerateContent?alt=sse&key={self.api_key}",
                json=payload,
                timeout=provider_settings.provider_timeout_seconds,
            ) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise ProviderAPIError(f"Gemini API Error: {text.decode('utf-8')}")

                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        import json

                        try:
                            data = json.loads(chunk[6:])
                            candidates = data.get("candidates", [])
                            if candidates:
                                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                if text:
                                    yield text
                        except Exception:
                            pass

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        inputs = [request.input] if isinstance(request.input, str) else request.input
        embeddings = []

        async with httpx.AsyncClient() as client:
            for inp in inputs:
                payload = {"model": f"models/{request.model}", "content": {"parts": [{"text": inp}]}}
                response = await client.post(
                    f"{self.base_url}/{request.model}:embedContent?key={self.api_key}",
                    json=payload,
                    timeout=provider_settings.provider_timeout_seconds,
                )
                if response.status_code != 200:
                    raise ProviderAPIError(f"Gemini API Error: {response.text}")

                data = response.json()
                embeddings.append(data.get("embedding", {}).get("values", []))

        return EmbeddingResponse(embeddings=embeddings, model=request.model, provider="gemini", total_tokens=0)

    async def health(self) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}", timeout=5.0
                )
                return response.status_code == 200
            except Exception:
                return False

    async def models(self) -> list[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}", timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return [
                        m["name"].split("/")[-1]
                        for m in data.get("models", [])
                        if "generateContent" in m.get("supportedGenerationMethods", [])
                    ]
                return ["gemini-1.5-pro", "gemini-1.5-flash"]
            except Exception:
                return ["gemini-1.5-pro", "gemini-1.5-flash"]

    def count_tokens(self, text: str, model: str) -> int:
        return len(text) // 4
