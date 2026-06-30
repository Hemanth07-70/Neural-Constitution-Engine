import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base


class LangGraphRunRecord(Base):
    __tablename__ = "langgraph_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # Could store graph topological definition
    graph_definition: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    # Store overall execution status
    status: Mapped[str] = mapped_column(String, default="running")  # running, completed, failed, paused
    error_message: Mapped[str] = mapped_column(String, nullable=True)

    # Store list of audit IDs generated during this run
    audit_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
