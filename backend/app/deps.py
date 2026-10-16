from fastapi import Header, HTTPException, status

from .config import settings


def require_ingest_token(x_rover_token: str | None = Header(default=None)) -> None:
    """Rovers authenticate with a shared token when INGEST_TOKEN is configured."""
    if settings.ingest_token and x_rover_token != settings.ingest_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid rover token")
