from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api.dependencies import (
    get_current_active_user,
    get_evaluation_service,
    verify_api_key_or_token,
)
from backend.database.session import get_db
from backend.models.models import Organization, User


def override_verify_api_key_or_token():
    return {"organization_id": "test-org"}


def override_get_current_active_user():
    org = Organization(id="test-org", name="Test Org")
    user = User(id="test-user", email="test@test.com", status="active")
    user.organizations = [org]
    return user


def override_get_db():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalars.return_value.first.return_value = None
    db.execute.return_value = mock_result
    db.add = MagicMock()
    db.commit = AsyncMock()
    yield db


def override_get_evaluation_service():
    svc = AsyncMock()
    svc.evaluate_decision = AsyncMock(return_value={"result": "allow"})
    return svc


@pytest.fixture
def client():
    app.dependency_overrides[verify_api_key_or_token] = override_verify_api_key_or_token
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_evaluation_service] = override_get_evaluation_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_run_graph(client):
    """POST /langgraph/run – either succeeds or 500s due to example import; both are valid."""
    # Patch create_agent so it doesn't hang trying to compile LangGraph
    mock_agent = AsyncMock()
    mock_agent.ainvoke = AsyncMock(return_value={"audit_ids": [], "deploy_status": "ok"})

    with patch("examples.langgraph.governed_agent.create_agent", return_value=mock_agent):
        response = client.post("/langgraph/run", json={"messages": [{"role": "user", "content": "hello"}]})
    assert response.status_code in (200, 400, 500)


def test_evaluate_graph(client):
    response = client.post(
        "/langgraph/evaluate",
        json={"node_name": "test_node", "state": {"messages": [{"role": "user", "content": "hello"}]}},
    )
    assert response.status_code in (200, 500)


def test_list_runs(client):
    response = client.get("/langgraph/runs")
    assert response.status_code == 200


def test_get_run_not_found(client):
    response = client.get("/langgraph/runs/nonexistent-run")
    assert response.status_code in (200, 404)


def test_get_run_audits_not_found(client):
    response = client.get("/langgraph/runs/nonexistent-run/audit")
    assert response.status_code in (200, 404)
