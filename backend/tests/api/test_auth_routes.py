import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.database.session import get_db
from backend.models.models import User


def _make_mock_user():
    from backend.auth.security import get_password_hash
    return User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        status="active",
        full_name="Test User",
    )


def override_get_db():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    db.commit = AsyncMock()
    db.add = MagicMock()
    yield db


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_register_success(client):
    """Register should succeed when email is not taken."""
    # Mock UserRepository so get_by_email returns None (no existing user)
    # and create() doesn't actually touch DB
    with patch("backend.api.routes.auth.UserRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get_by_email = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=None)
        MockRepo.return_value = mock_repo

        response = client.post(
            "/auth/register",
            json={"full_name": "Test User", "email": "test@example.com", "password": "password123"},
        )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_conflict(client):
    """Register should return 409 if email already exists."""
    with patch("backend.api.routes.auth.UserRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get_by_email = AsyncMock(return_value=_make_mock_user())
        MockRepo.return_value = mock_repo

        response = client.post(
            "/auth/register",
            json={"full_name": "Test User", "email": "test@example.com", "password": "password123"},
        )
    assert response.status_code == 409


def test_login_success(client):
    """Login should return tokens for valid credentials."""
    with patch("backend.api.routes.auth.UserRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get_by_email = AsyncMock(return_value=_make_mock_user())
        MockRepo.return_value = mock_repo

        response = client.post("/auth/login", data={"username": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid(client):
    """Login should return 400 for wrong password."""
    with patch("backend.api.routes.auth.UserRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get_by_email = AsyncMock(return_value=_make_mock_user())
        MockRepo.return_value = mock_repo

        response = client.post("/auth/login", data={"username": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 400


def test_get_me_unauthorized(client):
    """Unauthenticated request to /auth/me should return 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401
