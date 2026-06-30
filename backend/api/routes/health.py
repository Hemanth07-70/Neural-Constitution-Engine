"""Healthcheck and version endpoints."""

from fastapi import APIRouter

from backend.sdk.engine import Engine

router = APIRouter()


@router.get("/health", summary="System Healthcheck")
async def health_check() -> dict[str, str]:
    """Verify that the API is running."""
    return {"status": "ok"}


@router.get("/version", summary="Engine Version")
async def version() -> dict[str, str]:
    """Return the underlying Neural Constitution Engine SDK version."""
    return {"version": Engine.version()}
