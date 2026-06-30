from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.application.services.constitution_service import ConstitutionService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_engine_cache():
    return AsyncMock()


@pytest.mark.asyncio
async def test_publish_constitution_version(mock_db, mock_engine_cache):
    service = ConstitutionService(mock_db, mock_engine_cache)

    with patch(
        "backend.application.repositories.constitution_repository.ConstitutionRepository.save", new_callable=AsyncMock
    ) as mock_save, patch(
        "backend.application.repositories.constitution_repository.ConstitutionRepository.get_active_constitution",
        new_callable=AsyncMock,
    ) as mock_get_active, patch("backend.sdk.engine.Engine.validate_constitution") as mock_validate:
        mock_active = MagicMock()
        mock_active.active = True
        mock_get_active.return_value = mock_active

        record = await service.publish("org-1", "author-1", "apiVersion: nce/v1", "1.0.0")

        assert record.version == "1.0.0"
        assert record.organization_id == "org-1"
        assert record.active is True

        assert mock_active.active is False
        assert mock_save.call_count == 2
        mock_db.commit.assert_called_once()
        mock_engine_cache.invalidate.assert_called_once_with("org-1")
        mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_get_active_constitution(mock_db, mock_engine_cache):
    service = ConstitutionService(mock_db, mock_engine_cache)

    mock_record = AsyncMock()

    with patch(
        "backend.application.repositories.constitution_repository.ConstitutionRepository.get_active_constitution",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = mock_record

        result = await service.get_active_constitution("org-1")
        assert result == mock_record
        mock_get.assert_called_once_with("org-1")
