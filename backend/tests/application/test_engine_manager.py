from unittest.mock import AsyncMock, patch

import pytest

from backend.application.cache.engine_cache import EngineCache
from backend.application.services.engine_manager import EngineManager
from backend.models.models import ConstitutionRecord


@pytest.fixture
def engine_cache():
    return EngineCache(default_ttl_seconds=3600)


@pytest.fixture
def engine_manager(engine_cache):
    return EngineManager(engine_cache)


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def dummy_yaml():
    return """
apiVersion: nce/v1
kind: Constitution
metadata:
  id: default
  version: "1.0"
  scope: global
resolution:
  strategy: strict
  default_verdict: block
principles:
  - id: p1
    statement: "Test"
    category: test
rules:
  - id: r1
    condition: "true"
    action:
      type: allow
"""


@pytest.mark.asyncio
async def test_get_engine_cache_miss_and_hit(engine_manager, mock_db_session, dummy_yaml):
    # Setup mock active constitution
    mock_record = ConstitutionRecord(version="1.0", yaml_content=dummy_yaml)

    with patch(
        "backend.application.repositories.constitution_repository.ConstitutionRepository.get_active_constitution",
        new_callable=AsyncMock,
    ) as mock_get_active:
        mock_get_active.return_value = mock_record

        # 1. First call - Cache Miss
        engine1 = await engine_manager.get_engine(mock_db_session, "org1")
        assert engine1 is not None
        mock_get_active.assert_called_once_with("org1")

        # 2. Second call - Cache Hit
        mock_get_active.reset_mock()
        engine2 = await engine_manager.get_engine(mock_db_session, "org1")
        assert engine2 is engine1
        # It shouldn't hit the DB again if it specifies the version,
        # BUT our current implementation always hits DB to find the "active" version first before checking cache.
        # Wait, the get_engine queries DB to get active version (lightweight query) and then checks cache for that version.
        mock_get_active.assert_called_once_with("org1")


@pytest.mark.asyncio
async def test_engine_invalidation(engine_manager, mock_db_session, dummy_yaml):
    mock_record = ConstitutionRecord(version="1.0", yaml_content=dummy_yaml)

    with patch(
        "backend.application.repositories.constitution_repository.ConstitutionRepository.get_active_constitution",
        new_callable=AsyncMock,
    ) as mock_get_active:
        mock_get_active.return_value = mock_record

        engine1 = await engine_manager.get_engine(mock_db_session, "org1")

        # Invalidate
        engine_manager.invalidate("org1")

        # This will create a new engine instance
        engine2 = await engine_manager.get_engine(mock_db_session, "org1")

        assert engine1 is not engine2
