from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import JWTError

from backend.api.dependencies import verify_api_key_or_token


@pytest.mark.asyncio
async def test_verify_api_key_or_token_no_credentials():
    with pytest.raises(HTTPException) as exc:
        await verify_api_key_or_token(api_key_value=None, token=None, db=AsyncMock())
    assert exc.value.status_code == 401
    assert "Could not validate credentials" in exc.value.detail


@pytest.mark.asyncio
async def test_verify_api_key_valid():
    mock_db = AsyncMock()
    mock_key = AsyncMock()
    mock_key.organization_id = "org-1"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_key
    mock_db.execute.return_value = mock_result

    result = await verify_api_key_or_token(api_key_value="valid-key", token=None, db=mock_db)
    assert result == {"organization_id": "org-1"}


@pytest.mark.asyncio
async def test_verify_api_key_invalid():
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await verify_api_key_or_token(api_key_value="invalid-key", token=None, db=mock_db)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_token_valid():
    mock_db = AsyncMock()
    mock_user = AsyncMock()
    mock_user.status = "active"
    mock_org = AsyncMock()
    mock_org.id = "org-2"
    mock_user.organizations = [mock_org]

    with patch("backend.api.dependencies.jwt.decode", return_value={"sub": mock_user.id}), patch(
        "backend.api.dependencies.UserRepository.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_user

        result = await verify_api_key_or_token(api_key_value=None, token="valid-token", db=mock_db)
        assert result == {"user_id": mock_user.id}


@pytest.mark.asyncio
async def test_verify_token_invalid():
    mock_db = AsyncMock()

    with patch("backend.api.dependencies.jwt.decode", side_effect=JWTError):
        with pytest.raises(HTTPException) as exc:
            await verify_api_key_or_token(api_key_value=None, token="invalid", db=mock_db)
        assert exc.value.status_code == 401
