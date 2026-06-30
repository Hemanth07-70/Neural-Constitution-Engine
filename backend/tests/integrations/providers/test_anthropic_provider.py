from unittest.mock import patch

import pytest

from backend.integrations.providers.anthropic.provider import AnthropicProvider
from backend.integrations.providers.exceptions import ProviderAPIError
from backend.integrations.providers.models import ChatMessage, ProviderRequest


@pytest.fixture
def provider():
    return AnthropicProvider()


@pytest.mark.asyncio
async def test_anthropic_generate_success(provider):
    request = ProviderRequest(messages=[ChatMessage(role="user", content="Hello")], model="claude-3-opus-20240229")

    import httpx

    mock_response = httpx.Response(
        200,
        json={
            "content": [{"text": "Hi there"}],
            "model": "claude-3-opus-20240229",
            "usage": {"input_tokens": 10, "output_tokens": 20},
        },
        request=httpx.Request("POST", "http://test"),
    )

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = await provider.generate(request)

        assert response.message.content == "Hi there"
        assert response.model == "claude-3-opus-20240229"
        assert response.provider == "anthropic"


@pytest.mark.asyncio
async def test_anthropic_generate_error(provider):
    request = ProviderRequest(messages=[ChatMessage(role="user", content="Hello")], model="claude-3-opus-20240229")

    import httpx

    mock_response = httpx.Response(400, text="Bad Request", request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(ProviderAPIError, match="Anthropic API Error: Bad Request"):
            await provider.generate(request)
