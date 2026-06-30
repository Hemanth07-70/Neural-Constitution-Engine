from datetime import datetime

from backend.database.session import get_db
from backend.models.models import ProviderTelemetryModel


async def log_telemetry(
    provider_name: str,
    model_name: str,
    success: bool,
    latency_ms: float,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    retries: int = 0,
    error_message: str | None = None,
    organization_id: str | None = None,
) -> None:
    """Logs provider usage telemetry to the database asynchronously."""

    # Very simple cost estimation (mock logic)
    cost_estimate = (prompt_tokens * 0.0001) + (completion_tokens * 0.0002)

    async for db in get_db():
        telemetry = ProviderTelemetryModel(
            organization_id=organization_id,
            provider_name=provider_name,
            model_name=model_name,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_estimate=cost_estimate,
            success=success,
            error_message=error_message,
            retries=retries,
            timestamp=datetime.utcnow(),
        )
        db.add(telemetry)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
        break
