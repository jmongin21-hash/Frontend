from fastapi import Depends, HTTPException, Request, status

from .config import get_settings
from .security import decode_token


async def get_current_user(request: Request):
    token = request.cookies.get("doodle_session") or request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


def get_cors_origins():
    settings = get_settings()
    return [str(settings.frontend_origin)] if settings.frontend_origin else []
