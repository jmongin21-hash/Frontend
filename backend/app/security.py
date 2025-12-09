from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from .config import get_settings


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iss: str
    aud: str
    username: Optional[str] = None


def create_token(discord_id: int, username: Optional[str]) -> str:
    settings = get_settings()
    now = datetime.utcnow()
    exp = now + timedelta(minutes=settings.jwt_exp_minutes)
    payload = {
        "sub": str(discord_id),
        "exp": exp,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "username": username,
        "iat": now,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        decoded = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
        return TokenPayload(**decoded)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
