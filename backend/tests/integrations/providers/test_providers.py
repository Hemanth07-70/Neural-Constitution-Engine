from unittest.mock import MagicMock, patch

import pytest

from backend.integrations.providers.exceptions import ProviderNotFoundError
from backend.integrations.providers.manager import ProviderManager
from backend.integrations.providers.models import ChatMessage, ProviderRequest
from backend.integrations.providers.registry import ProviderRegistry


@pytest.fixture
def dummy_request():
    return ProviderRequest(messages=[ChatMessage(role="user", content="Hello!")], model="gpt-4o")


@pytest.mark.asyncio
async def test_provider_registration():
    # Verify OpenAI is registered
    providers = ProviderRegistry.list_providers()
    assert "openai" in providers
    assert "anthropic" in providers


@pytest.mark.asyncio
async def test_provider_not_found():
    with pytest.raises(ProviderNotFoundError):
        await ProviderManager.get_provider("unknown_provider")


@pytest.mark.asyncio
@patch("backend.integrations.providers.openai.provider.httpx.AsyncClient.post")
async def test_openai_generate(mock_post, dummy_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "model": "gpt-4o",
        "choices": [{"message": {"role": "assistant", "content": "Hi there!"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_post.return_value = mock_response

    response = await ProviderManager.generate(dummy_request, provider_name="openai")

    assert response.provider == "openai"
    assert response.message.content == "Hi there!"
    assert response.total_tokens == 15


@pytest.mark.asyncio
@patch("backend.integrations.providers.openai.provider.httpx.AsyncClient.post")
async def test_openai_generate_error_retry(mock_post, dummy_request):
    # Setup mock to fail first time, then succeed
    fail_response = MagicMock()
    fail_response.status_code = 500
    fail_response.text = "Internal Server Error"

    success_response = MagicMock()
    success_response.status_code = 200
    success_response.json.return_value = {
        "model": "gpt-4o",
        "choices": [{"message": {"role": "assistant", "content": "Success on retry!"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }

    mock_post.side_effect = [fail_response, success_response]

    response = await ProviderManager.generate(dummy_request, provider_name="openai", max_retries=1)

    assert response.message.content == "Success on retry!"
    assert mock_post.call_count == 2
