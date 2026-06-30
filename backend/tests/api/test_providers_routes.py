"""Tests for /providers API routes."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_list_providers(client):
    """GET /providers should return a list of provider names."""
    with patch(
        "backend.integrations.providers.registry.ProviderRegistry.list_providers",
        return_value=["openai", "anthropic", "gemini"],
    ):
        response = client.get("/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "openai" in data


def test_check_health_all_healthy(client):
    """GET /providers/health returns healthy when all providers respond OK."""
    with patch(
        "backend.integrations.providers.registry.ProviderRegistry.list_providers",
        return_value=["openai"],
    ), patch(
        "backend.integrations.providers.manager.ProviderManager.health",
        new=AsyncMock(return_value=True),
    ):
        response = client.get("/providers/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["providers"]["openai"] is True


def test_check_health_all_unhealthy(client):
    """GET /providers/health returns unhealthy when no providers respond."""
    with patch(
        "backend.integrations.providers.registry.ProviderRegistry.list_providers",
        return_value=["openai"],
    ), patch(
        "backend.integrations.providers.manager.ProviderManager.health",
        new=AsyncMock(return_value=False),
    ):
        response = client.get("/providers/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"


def test_list_models(client):
    """GET /providers/models should return models keyed by provider name."""
    mock_provider = AsyncMock()
    mock_provider.models = AsyncMock(return_value=["gpt-4", "gpt-3.5-turbo"])

    with patch(
        "backend.integrations.providers.registry.ProviderRegistry.list_providers",
        return_value=["openai"],
    ), patch(
        "backend.integrations.providers.manager.ProviderManager.get_provider",
        new=AsyncMock(return_value=mock_provider),
    ):
        response = client.get("/providers/models")
    assert response.status_code == 200
    data = response.json()
    assert "openai" in data
    assert "gpt-4" in data["openai"]


def test_list_models_handles_exception(client):
    """If a provider raises during models(), it should return an empty list for that provider."""
    with patch(
        "backend.integrations.providers.registry.ProviderRegistry.list_providers",
        return_value=["broken"],
    ), patch(
        "backend.integrations.providers.manager.ProviderManager.get_provider",
        new=AsyncMock(side_effect=Exception("Provider unavailable")),
    ):
        response = client.get("/providers/models")
    assert response.status_code == 200
    assert response.json()["broken"] == []


def test_generate_completion(client):
    """POST /providers/generate should call ProviderManager.generate."""
    from backend.integrations.providers.models import ChatMessage, ProviderResponse

    mock_response = ProviderResponse(
        message=ChatMessage(role="assistant", content="hello"),
        model="gpt-4",
        provider="openai",
        usage={"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
        raw={},
    )

    with patch(
        "backend.integrations.providers.manager.ProviderManager.generate",
        new=AsyncMock(return_value=mock_response),
    ):
        response = client.post(
            "/providers/generate",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"]["content"] == "hello"


def test_generate_completion_error(client):
    """POST /providers/generate should return 500 on provider error."""
    with patch(
        "backend.integrations.providers.manager.ProviderManager.generate",
        new=AsyncMock(side_effect=Exception("API key invalid")),
    ):
        response = client.post(
            "/providers/generate",
            json={
                "provider": "openai",
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 500
