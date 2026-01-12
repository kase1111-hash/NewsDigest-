"""FastAPI application for NewsDigest."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from newsdigest.api.models import ErrorResponse
from newsdigest.api.routes import compare, digest, extract, health
from newsdigest.config.settings import Config
from newsdigest.exceptions import (
    DigestError,
    ExtractionError,
    IngestError,
    NewsDigestError,
    ValidationError,
)
from newsdigest.storage.cache import MemoryCache
from newsdigest.version import __version__


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    app.state.config = Config()
    app.state.cache = MemoryCache(max_size=1000, default_ttl=300)
    yield
    # Shutdown
    await app.state.cache.clear()


def create_app(
    config: Config | None = None,
    enable_auth: bool = False,
    enable_rate_limit: bool = True,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        config: Optional configuration object.
        enable_auth: Enable API key authentication.
        enable_rate_limit: Enable rate limiting.

    Returns:
        Configured FastAPI application.
    """
    from newsdigest.api.middleware import (
        AuthMiddleware,
        RateLimitMiddleware,
        RequestTrackingMiddleware,
    )

    app = FastAPI(
        title="NewsDigest API",
        description=(
            "Semantic compression engine for news. "
            "Extract signal from noise by removing speculation, "
            "emotional language, and redundant content."
        ),
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Store config
    if config:
        app.state.config = config

    # Add middleware (order matters - first added = last executed)
    # Request tracking (outermost)
    app.add_middleware(RequestTrackingMiddleware)

    # Rate limiting
    app.add_middleware(RateLimitMiddleware, enabled=enable_rate_limit)

    # Authentication
    app.add_middleware(AuthMiddleware, enabled=enable_auth)

    # CORS (innermost)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    _register_exception_handlers(app)

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(extract.router, prefix="/api/v1", tags=["Extraction"])
    app.include_router(digest.router, prefix="/api/v1", tags=["Digest"])
    app.include_router(compare.router, prefix="/api/v1", tags=["Extraction"])

    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the application."""

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="validation_error",
                message=str(exc),
                details={"field": getattr(exc, "field", None)},
            ).model_dump(),
        )

    @app.exception_handler(IngestError)
    async def ingest_error_handler(
        request: Request, exc: IngestError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="ingest_error",
                message=str(exc),
                details={"source": getattr(exc, "source", None)},
            ).model_dump(),
        )

    @app.exception_handler(ExtractionError)
    async def extraction_error_handler(
        request: Request, exc: ExtractionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="extraction_error",
                message=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(DigestError)
    async def digest_error_handler(
        request: Request, exc: DigestError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="digest_error",
                message=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(NewsDigestError)
    async def newsdigest_error_handler(
        request: Request, exc: NewsDigestError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                message=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                message="An unexpected error occurred",
            ).model_dump(),
        )


# Create default app instance
app = create_app()


def get_config(request: Request) -> Config:
    """Get configuration from request state.

    Args:
        request: FastAPI request object.

    Returns:
        Configuration object.
    """
    return getattr(request.app.state, "config", Config())
