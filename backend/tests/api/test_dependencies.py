from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import JWTError

from backend.api.dependencies import verify_api_key_or_token


@pytest.mark.asyncio
async def test_verify_api_key_or_token_no_credentials():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_org = MagicMock()
    mock_org.id = "demo-org"
    mock_result.scalars.return_value.first.return_value = mock_org
    mock_db.execute.return_value = mock_result
    
    res = await verify_api_key_or_token(api_key_value=None, token=None, db=mock_db, x_organization_id=None)
    assert res == {"organization_id": "demo-org"}


@pytest.mark.asyncio
async def test_verify_api_key_valid():
    mock_db = AsyncMock()
    mock_key = AsyncMock()
    mock_key.organization_id = "org-1"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_key
    mock_db.execute.return_value = mock_result

    result = await verify_api_key_or_token(api_key_value="valid-key", token=None, db=mock_db, x_organization_id=None)
    assert result == {"organization_id": "org-1"}


@pytest.mark.asyncio
async def test_verify_api_key_invalid():
    mock_db = AsyncMock()

    mock_result_key = MagicMock()
    mock_result_key.scalar_one_or_none.return_value = None
    
    mock_result_org = MagicMock()
    mock_org = MagicMock()
    mock_org.id = "demo-org"
    mock_result_org.scalars.return_value.first.return_value = mock_org
    
    mock_db.execute.side_effect = [mock_result_key, mock_result_org]

    res = await verify_api_key_or_token(api_key_value="invalid-key", token=None, db=mock_db, x_organization_id=None)
    assert res == {"organization_id": "demo-org"}


@pytest.mark.asyncio
async def test_verify_token_valid():
    mock_db = AsyncMock()
    mock_user = AsyncMock()
    mock_user.id = "user-1"
    mock_user.status = "active"
    mock_org = AsyncMock()
    mock_org.id = "org-2"
    mock_user.organizations = [mock_org]

    with patch("backend.api.dependencies.jwt.decode", return_value={"sub": mock_user.id}), patch(
        "backend.api.dependencies.UserRepository.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_user

        result = await verify_api_key_or_token(api_key_value=None, token="valid-token", db=mock_db, x_organization_id=None)
        assert result == {"user_id": "user-1", "organization_id": "org-2"}


@pytest.mark.asyncio
async def test_verify_token_invalid():
    mock_db = AsyncMock()
    mock_result_org = MagicMock()
    mock_org = MagicMock()
    mock_org.id = "demo-org"
    mock_result_org.scalars.return_value.first.return_value = mock_org
    mock_db.execute.return_value = mock_result_org

    with patch("backend.api.dependencies.jwt.decode", side_effect=JWTError):
        res = await verify_api_key_or_token(api_key_value=None, token="invalid", db=mock_db, x_organization_id=None)
        assert res == {"organization_id": "demo-org"}
