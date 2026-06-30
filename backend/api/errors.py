"""Global exception handlers for the FastAPI service."""

from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

from backend.sdk.exceptions import ConstitutionValidationError, EvaluationError


async def evaluation_error_handler(request: Request, exc: EvaluationError) -> JSONResponse:
    """Handle core evaluation failures."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Evaluation failed closed due to an internal error.", "error": str(exc)},
    )


async def constitution_validation_error_handler(request: Request, exc: ConstitutionValidationError) -> JSONResponse:
    """Handle structural invalidities in constitutions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Constitution validation failed.", "error": str(exc)},
    )


def register_exception_handlers(app: Any) -> None:
    """Register all global error handlers on the FastAPI app."""
    app.add_exception_handler(EvaluationError, evaluation_error_handler)
    app.add_exception_handler(ConstitutionValidationError, constitution_validation_error_handler)
