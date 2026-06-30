from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.repositories.organization_repository import OrganizationRepository
from backend.models.models import Organization


@pytest.mark.asyncio
async def test_get_by_slug():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_org = Organization(name="Test")
    mock_result.scalars.return_value.first.return_value = mock_org
    mock_db.execute.return_value = mock_result

    repo = OrganizationRepository(mock_db)
    org = await repo.get_by_slug("test-org")

    assert org == mock_org
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_role_in_org():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = "Admin"
    mock_db.execute.return_value = mock_result

    repo = OrganizationRepository(mock_db)
    role = await repo.get_role_in_org("user-1", "org-1")

    assert role == "Admin"
    mock_db.execute.assert_called_once()
