from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.api.schemas.evaluate import DecisionRequestSchema
from backend.application.services.evaluation_service import EvaluationService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_engine_manager():
    return AsyncMock()


@pytest.mark.asyncio
async def test_evaluate_decision_orchestration(mock_db, mock_engine_manager):
    service = EvaluationService(mock_db, mock_engine_manager)

    request_data = DecisionRequestSchema(
        id="123e4567-e89b-12d3-a456-426614174000",
        action={"type": "deploy", "params": {}},
        actor={"id": "dev1", "type": "human", "roles": [], "attributes": {}},
        context={
            "constitution_id": "test",
            "constitution_version": "1.0",
            "environment": {"name": "production", "timestamp": "2026-06-29T00:00:00Z"},
            "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
        },
        submitted_at="2026-06-29T00:00:00Z",
    )

    # Mock the Engine and its evaluate method
    mock_engine = MagicMock()
    mock_audit = MagicMock()
    mock_audit.id = "audit-123"
    mock_audit.api_version = "v1"
    mock_audit.request.model_dump.return_value = {}
    mock_audit.result.model_dump.return_value = {}
    mock_audit.explanation.model_dump.return_value = {}
    mock_audit.recorded_at = "2026-01-01T00:00:00Z"

    mock_engine.evaluate.return_value = mock_audit
    mock_engine_manager.get_engine.return_value = mock_engine

    # Mock adapters
    with patch("backend.api.adapters.to_sdk_decision_request"), patch(
        "backend.api.adapters.from_sdk_audit_record"
    ) as mock_from_sdk, patch(
        "backend.application.repositories.audit_repository.AuditRepository.save_audit", new_callable=AsyncMock
    ) as mock_save:
        mock_pydantic_audit = MagicMock()
        mock_pydantic_audit.id = "audit-123"
        mock_from_sdk.return_value = mock_pydantic_audit

        result = await service.evaluate_decision("org1", request_data)

        # Verify engine was retrieved for org1
        mock_engine_manager.get_engine.assert_called_once_with(mock_db, "org1")

        # Verify evaluation was called
        mock_engine.evaluate.assert_called_once()

        # Verify persistence was invoked
        mock_save.assert_called_once()
        mock_db.commit.assert_called_once()

        assert result == mock_pydantic_audit
