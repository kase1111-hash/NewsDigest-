"""Health check endpoint for NewsDigest API."""

from datetime import datetime, timezone

from fastapi import APIRouter

from newsdigest.api.models import HealthResponse, HealthStatus
from newsdigest.version import __version__

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check service health status.

    Returns:
        Health status with version and timestamp.
    """
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        version=__version__,
        timestamp=datetime.now(timezone.utc),
    )
