"""Stage 5: Seals the decision into an AuditRecord."""

import uuid
from datetime import UTC, datetime

from backend.core.constitution.constitution import Constitution
from backend.core.domain.audit import AuditRecord
from backend.core.domain.provenance import Provenance
from backend.core.domain.request import DecisionRequest
from backend.core.rules.context import EvaluationContext

from .stages import PipelineData, PipelineStage


class AuditStage(PipelineStage):
    """Constructs the immutable AuditRecord."""

    def execute(
        self,
        request: DecisionRequest,
        constitution: Constitution,
        context: EvaluationContext,
        data: PipelineData,
    ) -> PipelineData:
        assert data.result is not None
        assert data.explanation is not None

        audit_id = uuid.uuid7() if hasattr(uuid, "uuid7") else uuid.uuid4()

        provenance = Provenance(
            constitution_version=constitution.metadata.version, engine_version="0.1.0", model_api_version="nce/v1"
        )

        content_hash = "sha256:00000000000000000000000000000000"

        audit = AuditRecord(
            id=audit_id,
            api_version="nce/v1",
            request=request,
            result=data.result,
            explanation=data.explanation,
            provenance=provenance,
            recorded_at=datetime.now(UTC),
            content_hash=content_hash,
        )

        return data.replace(audit=audit)
