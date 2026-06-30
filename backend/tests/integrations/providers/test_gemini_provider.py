from unittest.mock import patch

import pytest

from backend.integrations.providers.exceptions import ProviderAPIError
from backend.integrations.providers.gemini.provider import GeminiProvider
from backend.integrations.providers.models import ChatMessage, ProviderRequest


@pytest.fixture
def provider():
    return GeminiProvider()


@pytest.mark.asyncio
async def test_gemini_generate_success(provider):
    request = ProviderRequest(messages=[ChatMessage(role="user", content="Hello")], model="gemini-1.5-pro")

    import httpx

    mock_response = httpx.Response(
        200,
        json={
            "candidates": [{"content": {"parts": [{"text": "Hi there"}]}}],
            "usageMetadata": {"promptTokenCount": 1, "candidatesTokenCount": 2, "totalTokenCount": 3},
        },
        request=httpx.Request("POST", "http://test"),
    )

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = await provider.generate(request)

        assert response.message.content == "Hi there"
        assert response.model == "gemini-1.5-pro"
        assert response.provider == "gemini"


@pytest.mark.asyncio
async def test_gemini_generate_error(provider):
    request = ProviderRequest(messages=[ChatMessage(role="user", content="Hello")], model="gemini-1.5-pro")

    import httpx

    mock_response = httpx.Response(400, text="Bad Request", request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(ProviderAPIError, match="Gemini API Error: Bad Request"):
            await provider.generate(request)
