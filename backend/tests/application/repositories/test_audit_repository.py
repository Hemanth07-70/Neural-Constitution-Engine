"""Tests for AuditRepository covering save_audit, save_plan_evaluation,
get_audits_for_org, and get_plans_for_org."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.repositories.audit_repository import AuditRepository
from backend.models.models import AuditRecordModel, ExecutionPlanRecordModel


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return AuditRepository(mock_session)


# ---- save_audit ----


@pytest.mark.asyncio
async def test_save_audit_adds_and_flushes(repo, mock_session):
    audit = MagicMock(spec=AuditRecordModel)
    result = await repo.save_audit(audit)
    mock_session.add.assert_called_once_with(audit)
    mock_session.flush.assert_awaited_once()
    assert result is audit


# ---- save_plan_evaluation ----


@pytest.mark.asyncio
async def test_save_plan_evaluation_adds_and_flushes(repo, mock_session):
    plan = MagicMock(spec=ExecutionPlanRecordModel)
    result = await repo.save_plan_evaluation(plan)
    mock_session.add.assert_called_once_with(plan)
    mock_session.flush.assert_awaited_once()
    assert result is plan


# ---- get_audits_for_org ----


@pytest.mark.asyncio
async def test_get_audits_for_org_returns_list(repo, mock_session):
    fake_audit = MagicMock(spec=AuditRecordModel)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_audit]
    mock_session.execute = AsyncMock(return_value=mock_result)

    audits = await repo.get_audits_for_org("org-1", limit=10)
    assert audits == [fake_audit]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_audits_for_org_empty(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    audits = await repo.get_audits_for_org("org-1")
    assert audits == []


# ---- get_plans_for_org ----


@pytest.mark.asyncio
async def test_get_plans_for_org_returns_list(repo, mock_session):
    fake_plan = MagicMock(spec=ExecutionPlanRecordModel)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_plan]
    mock_session.execute = AsyncMock(return_value=mock_result)

    plans = await repo.get_plans_for_org("org-1", limit=5)
    assert plans == [fake_plan]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_plans_for_org_empty(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    plans = await repo.get_plans_for_org("org-2")
    assert plans == []
