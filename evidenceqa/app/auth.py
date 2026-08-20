"""Optional API-key authentication.

Enabled only when ``EVIDENCEQA_API_KEY`` is set. When it is unset every request
passes through, so the demo, tests and CI stay open by default.
"""

import os

from fastapi import Header, HTTPException, Request, status


def load_api_key() -> str | None:
    return os.getenv("EVIDENCEQA_API_KEY") or None


def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> None:
    """Dependency that rejects unauthenticated calls only when auth is enabled."""
    api_key = request.app.state.api_key
    if api_key is None:
        return
    if x_api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
