"""Main FastAPI application factory."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.config import settings
from backend.api.errors import register_exception_handlers
from backend.api.middleware import CorrelationIdMiddleware
from backend.api.routes import (
    api_keys,
    audits,
    auth,
    constitutions,
    evaluate,
    health,
    langgraph_routes,
    plans,
    providers,
    validate,
)
from backend.sdk.engine import Engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle events for the FastAPI application."""
    # Startup
    try:
        logger.info(f"Loading Constitution from {settings.NCE_CONSTITUTION_PATH}")
        engine = Engine.load(settings.NCE_CONSTITUTION_PATH)
        app.state.engine = engine
        logger.info("Neural Constitution Engine successfully loaded.")
    except Exception as e:
        logger.error(f"Failed to load Engine during startup: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Neural Constitution Engine API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="FastAPI Runtime for the Neural Constitution Engine",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(auth.router)
    app.include_router(api_keys.router)
    app.include_router(audits.router)
    app.include_router(health.router, tags=["System"])
    app.include_router(evaluate.router, tags=["Evaluation"])
    app.include_router(plans.router, tags=["Plans"])
    app.include_router(validate.router, tags=["Validation"])
    app.include_router(langgraph_routes.router)
    app.include_router(providers.router)
    app.include_router(constitutions.router)

    # Mount the static frontend directory (single-container deployments only)
    import os

    if os.path.isdir("frontend/dist"):
        app.mount("/static", StaticFiles(directory="frontend/dist", html=True), name="static")
    else:
        logger.warning("frontend/dist not found – skipping static file mount (development mode)")

    return app


app = create_app()
