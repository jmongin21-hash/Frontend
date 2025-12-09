import secrets
from typing import Optional

import httpx

from ..config import get_settings

DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"


def build_discord_oauth_url(state: str) -> str:
    settings = get_settings()
    base = "https://discord.com/api/oauth2/authorize"
    params = {
        "client_id": settings.discord_client_id,
        "redirect_uri": str(settings.oauth_redirect_uri),
        "response_type": "code",
        "scope": "identify",
        "state": state,
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base}?{query}"


def generate_state() -> str:
    return secrets.token_urlsafe(16)


async def exchange_code_for_token(code: str) -> str:
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id": settings.discord_client_id,
                "client_secret": settings.discord_client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": str(settings.oauth_redirect_uri),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


async def fetch_discord_user(access_token: str) -> tuple[int, Optional[str], Optional[str]]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(DISCORD_USER_URL, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    data = resp.json()
    return int(data["id"]), data.get("username"), data.get("avatar")
