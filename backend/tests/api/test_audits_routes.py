"""Tests for the /audits API route."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api.dependencies import get_audit_service, verify_api_key_or_token
from backend.database.session import get_db


def override_verify_api_key_or_token():
    return {"organization_id": "test-org"}


def override_get_db():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock())
    yield db


def _make_fake_record(record_id="rec-1"):
    """Build a MagicMock that looks like an AuditRecordModel."""
    import datetime

    r = MagicMock()
    r.id = record_id
    r.api_version = "nce/v1"
    r.request_data = {"action": "test"}
    r.result_data = {"action": "allow"}
    r.explanation_data = {}
    r.recorded_at = datetime.datetime(2026, 1, 1, 0, 0, 0)
    return r


@pytest.fixture
def client():
    app.dependency_overrides[verify_api_key_or_token] = override_verify_api_key_or_token
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_with_audits():
    fake_records = [_make_fake_record("rec-1"), _make_fake_record("rec-2")]

    async def override_audit_service_get():
        svc = AsyncMock()
        svc.get_audits = AsyncMock(return_value=fake_records)
        return svc

    def _override_svc():
        svc = AsyncMock()
        svc.get_audits = AsyncMock(return_value=fake_records)
        return svc

    app.dependency_overrides[verify_api_key_or_token] = override_verify_api_key_or_token
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_audit_service] = _override_svc

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_list_audits_returns_empty(client):
    """When AuditService returns nothing, endpoint should return 200 with empty list."""
    empty_svc = AsyncMock()
    empty_svc.get_audits = AsyncMock(return_value=[])
    app.dependency_overrides[get_audit_service] = lambda: empty_svc

    response = client.get("/audits/?organization_id=test-org")
    assert response.status_code == 200
    assert response.json() == []


def test_list_audits_returns_records(client_with_audits):
    """Audit records should be returned and formatted."""
    response = client_with_audits.get("/audits/?organization_id=test-org")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "rec-1"
    assert data[1]["id"] == "rec-2"
    assert "recorded_at" in data[0]


def test_list_audits_forbidden_for_wrong_org(client):
    """An org-scoped token must not be able to query a different org."""
    response = client.get("/audits/?organization_id=other-org")
    assert response.status_code == 403
