"""Extended provider coverage tests ensuring stream/generate/health/models are all hit."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.integrations.providers.anthropic.provider import AnthropicProvider
from backend.integrations.providers.gemini.provider import GeminiProvider
from backend.integrations.providers.models import ChatMessage, ProviderRequest
from backend.integrations.providers.ollama.provider import OllamaProvider
from backend.integrations.providers.openai.provider import OpenAIProvider

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _async_lines(*lines):
    for line in lines:
        yield line


def _make_stream_ctx(lines):
    """Return a MagicMock whose __aenter__ yields a stream response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.aiter_lines = lambda: _async_lines(*lines)

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=mock_resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


def _make_post_response(json_body: dict):
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = json_body
    return mock


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openai_provider_coverage():
    provider = OpenAIProvider()

    generate_resp = _make_post_response(
        {
            "choices": [{"message": {"role": "assistant", "content": "hello"}}],
            "model": "gpt-4",
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        }
    )
    health_resp = _make_post_response({"status": "ok"})
    # /v1/models returns list
    models_resp = MagicMock()
    models_resp.status_code = 200
    models_resp.json.return_value = {"data": [{"id": "gpt-4"}]}

    stream_ctx = _make_stream_ctx(
        [
            'data: {"choices": [{"delta": {"content": "hi"}}]}',
            "data: [DONE]",
        ]
    )

    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=[generate_resp, health_resp])
    mock_client.get = AsyncMock(return_value=models_resp)
    mock_client.stream = MagicMock(return_value=stream_ctx)

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    req = ProviderRequest(messages=[ChatMessage(role="user", content="hello")], model="gpt-4")

    with patch("httpx.AsyncClient", return_value=mock_cm):
        await provider.generate(req)
        await provider.health()
        await provider.models()
        provider.count_tokens("hello world", "gpt-4")
        async for _ in provider.stream(req):
            pass


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_anthropic_provider_coverage():
    provider = AnthropicProvider()

    generate_resp = _make_post_response(
        {
            "content": [{"text": "hello"}],
            "model": "claude-3",
            "usage": {"input_tokens": 10, "output_tokens": 10},
        }
    )
    health_resp = _make_post_response({"models": [{"id": "claude-3"}]})
    models_resp = _make_post_response({"models": [{"id": "claude-3"}]})

    stream_ctx = _make_stream_ctx(
        [
            'data: {"type": "content_block_delta", "delta": {"text": "hi"}}',
            'data: {"type": "message_stop"}',
        ]
    )

    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=[generate_resp, health_resp, models_resp])
    mock_client.stream = MagicMock(return_value=stream_ctx)

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    req = ProviderRequest(messages=[ChatMessage(role="user", content="hello")], model="claude-3")

    with patch("httpx.AsyncClient", return_value=mock_cm):
        await provider.generate(req)
        await provider.health()
        await provider.models()
        provider.count_tokens("hello world", "claude-3")
        async for _ in provider.stream(req):
            pass


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_gemini_provider_coverage():
    provider = GeminiProvider()

    generate_resp = _make_post_response(
        {
            "candidates": [{"content": {"parts": [{"text": "hello"}]}}],
            "usageMetadata": {
                "promptTokenCount": 5,
                "candidatesTokenCount": 5,
                "totalTokenCount": 10,
            },
        }
    )
    health_resp = _make_post_response({"models": [{"name": "models/gemini-1.5-pro"}]})
    models_resp = _make_post_response({"models": [{"name": "models/gemini-1.5-pro"}]})

    stream_ctx = _make_stream_ctx(
        [
            'data: {"candidates": [{"content": {"parts": [{"text": "hi"}]}}]}',
        ]
    )

    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=[generate_resp])
    mock_client.get = AsyncMock(side_effect=[health_resp, models_resp])
    mock_client.stream = MagicMock(return_value=stream_ctx)

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    req = ProviderRequest(messages=[ChatMessage(role="user", content="hello")], model="gemini-1.5-pro")

    with patch("httpx.AsyncClient", return_value=mock_cm):
        await provider.generate(req)
        await provider.health()
        await provider.models()
        provider.count_tokens("hello world", "gemini-1.5-pro")
        async for _ in provider.stream(req):
            pass


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ollama_provider_coverage():
    provider = OllamaProvider()

    generate_resp = _make_post_response(
        {
            "message": {"role": "assistant", "content": "hello"},
            "model": "llama3",
            "prompt_eval_count": 10,
            "eval_count": 10,
        }
    )
    health_resp = _make_post_response({"status": "ok"})
    models_resp = _make_post_response({"models": [{"name": "llama3"}]})

    stream_ctx = _make_stream_ctx(
        [
            '{"message": {"content": "hi"}}',
        ]
    )

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=generate_resp)
    mock_client.get = AsyncMock(side_effect=[health_resp, models_resp])
    mock_client.stream = MagicMock(return_value=stream_ctx)

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    req = ProviderRequest(messages=[ChatMessage(role="user", content="hello")], model="llama3")

    with patch("httpx.AsyncClient", return_value=mock_cm):
        await provider.generate(req)
        await provider.health()
        await provider.models()
        provider.count_tokens("hello world", "llama3")
        async for _ in provider.stream(req):
            pass
