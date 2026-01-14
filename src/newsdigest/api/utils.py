"""API utilities for NewsDigest."""

from fastapi import Request

from newsdigest.config.settings import Config


def get_config(request: Request) -> Config:
    """Get configuration from request state.

    Args:
        request: FastAPI request object.

    Returns:
        Configuration object.
    """
    return getattr(request.app.state, "config", Config())
