"""Tests for the FastAPI API."""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api.config import settings
from backend.api.dependencies import get_engine_manager, verify_api_key_or_token
from backend.application.cache.engine_cache import EngineCache
from backend.application.services.engine_manager import EngineManager


def override_verify_api_key_or_token():
    return {"organization_id": "test-org"}


class MockEngineManager(EngineManager):
    def __init__(self):
        super().__init__(EngineCache())

    async def get_engine(self, db: Any, organization_id: str, constitution_version: Any = None) -> Any:
        with open("examples/constitution.yaml") as f:
            yaml_content = f.read()
        return self._build_engine_from_yaml(yaml_content)


def override_get_engine_manager():
    return MockEngineManager()


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch: Any) -> None:
    """Override constitution path for testing and mock DB persistence."""
    monkeypatch.setattr(settings, "NCE_CONSTITUTION_PATH", "examples/constitution.yaml")

    # Mock AuditRepository to avoid foreign key constraint errors during API tests
    from backend.application.repositories.audit_repository import AuditRepository

    async def mock_save_audit(*args, **kwargs):
        pass

    async def mock_save_plan(*args, **kwargs):
        pass

    monkeypatch.setattr(AuditRepository, "save_audit", mock_save_audit)
    monkeypatch.setattr(AuditRepository, "save_plan_evaluation", mock_save_plan)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[verify_api_key_or_token] = override_verify_api_key_or_token
    app.dependency_overrides[get_engine_manager] = override_get_engine_manager
    # Use TestClient as context manager to trigger lifespan events
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    """Test the healthcheck endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(client: TestClient) -> None:
    """Test the version endpoint."""
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_validate_constitution(client: TestClient, tmp_path: Any) -> None:
    """Test constitution validation endpoint."""
    const_content = """apiVersion: nce/v1
kind: Constitution
metadata:
  id: test
  version: 1.0.0
  scope: global
resolution:
  strategy: most-restrictive-wins
  default_verdict: block
principles: []
rules: []
"""
    test_file = tmp_path / "test.yaml"
    test_file.write_text(const_content)

    with open(test_file, "rb") as f:
        response = client.post(
            "/validate",
            files={"file": ("test.yaml", f, "application/x-yaml")},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "valid"
    assert response.json()["filename"] == "test.yaml"


def test_evaluate_decision(client: TestClient) -> None:
    """Test the /evaluate endpoint with a valid payload."""
    payload = {
        "api_version": "nce/v1",
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "actor": {"id": "agent-123", "type": "agent", "roles": [], "attributes": {}},
        "action": {"type": "db.drop", "params": {"table": "customers"}},
        "context": {
            "constitution_id": "test",
            "constitution_version": "1.0",
            "environment": {"name": "production", "timestamp": "2026-06-29T00:00:00Z"},
            "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
        },
        "submitted_at": "2026-06-29T00:00:00Z",
    }

    response = client.post("/evaluate", json=payload)

    # Assert successful response (should map to fallback since empty constitution)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["result"]["action"] == "block"
    assert data["result"]["determining_rule_id"] == "R-SEC-1"


def test_invalid_evaluate_payload(client: TestClient) -> None:
    """Test the /evaluate endpoint with missing fields."""
    response = client.post("/evaluate", json={"api_version": "nce/v1"})
    assert response.status_code == 422  # Pydantic validation error


def test_evaluate_plan(client: TestClient) -> None:
    """Test the /plans/evaluate endpoint."""
    payload = {
        "metadata": {
            "id": "plan-123",
            "creator": "system",
            "created_at": "2026-06-29T00:00:00Z",
            "goal_description": "Test plan",
        },
        "nodes": [
            {
                "id": "node-1",
                "request": {
                    "api_version": "nce/v1",
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "actor": {"id": "agent-123", "type": "agent"},
                    "action": {"type": "db.drop", "params": {"table": "customers"}},
                    "context": {
                        "constitution_id": "test",
                        "constitution_version": "1.0",
                        "environment": {"name": "production", "timestamp": "2026-06-29T00:00:00Z"},
                        "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "submitted_at": "2026-06-29T00:00:00Z",
                },
            }
        ],
        "edges": [],
    }

    response = client.post("/plans/evaluate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["topological_order"] == ["node-1"]
