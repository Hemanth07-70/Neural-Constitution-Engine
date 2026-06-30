import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base

# Association table for Membership
memberships_table = Table(
    "memberships",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("organization_id", String, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String, nullable=False),  # Admin, Developer, Auditor, Viewer
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization", secondary=memberships_table, back_populates="users"
    )


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", secondary=memberships_table, back_populates="organizations")
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey", back_populates="organization", cascade="all, delete-orphan"
    )
    constitutions: Mapped[list["ConstitutionRecord"]] = relationship(
        "ConstitutionRecord", back_populates="organization", cascade="all, delete-orphan"
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_key: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String, nullable=False)

    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="api_keys")


class ConstitutionRecord(Base):
    __tablename__ = "constitutions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    yaml_content: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="constitutions")


class AuditRecordModel(Base):
    """Stores the execution trace from a POST /evaluate call."""

    __tablename__ = "audit_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )  # Optional for now to support quickstart
    api_version: Mapped[str] = mapped_column(String, nullable=False)

    # We store the Pydantic dumps as JSON
    request_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    explanation_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExecutionPlanRecordModel(Base):
    """Stores an execution DAG plan."""

    __tablename__ = "execution_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )

    plan_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    validation_result_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProviderConfigModel(Base):
    """Stores configuration for AI Providers."""

    __tablename__ = "provider_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    provider_name: Mapped[str] = mapped_column(String, nullable=False)  # e.g. openai, anthropic
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Store settings like timeout, max_retries, default_model
    config_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Do not store raw API keys. In production, this would be a Vault reference.
    # For this milestone, we might store a hashed key or a placeholder for environment variables.
    credentials_ref: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProviderTelemetryModel(Base):
    """Stores telemetry for AI Provider requests."""

    __tablename__ = "provider_telemetry"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )

    provider_name: Mapped[str] = mapped_column(String, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)

    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    cost_estimate: Mapped[float] = mapped_column(Float, default=0.0)

    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str] = mapped_column(String, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, default=0)

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
