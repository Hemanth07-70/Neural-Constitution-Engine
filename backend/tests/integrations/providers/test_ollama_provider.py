from unittest.mock import patch

import pytest

from backend.integrations.providers.exceptions import ProviderAPIError
from backend.integrations.providers.models import ChatMessage, ProviderRequest
from backend.integrations.providers.ollama.provider import OllamaProvider


@pytest.fixture
def provider():
    return OllamaProvider()


@pytest.mark.asyncio
async def test_ollama_generate_success(provider):
    request = ProviderRequest(messages=[ChatMessage(role="user", content="Hello")], model="llama3")

    import httpx

    mock_response = httpx.Response(
        200,
        json={
            "message": {"role": "assistant", "content": "Hi there"},
            "model": "llama3",
            "prompt_eval_count": 10,
            "eval_count": 20,
        },
        request=httpx.Request("POST", "http://test"),
    )

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = await provider.generate(request)

        assert response.message.content == "Hi there"
        assert response.model == "llama3"
        assert response.provider == "ollama"


@pytest.mark.asyncio
async def test_ollama_generate_error(provider):
    request = ProviderRequest(messages=[ChatMessage(role="user", content="Hello")], model="llama3")

    import httpx

    mock_response = httpx.Response(400, text="Bad Request", request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(ProviderAPIError, match="Ollama API Error: Bad Request"):
            await provider.generate(request)
