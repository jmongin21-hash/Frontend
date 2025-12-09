import asyncio

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from . import services
from .config import get_settings
from .db import get_db, Base, engine, db_session
from .dependencies import get_current_user, get_cors_origins
from .schemas import ClaimResponse, HealthResponse, LoginUrlResponse, MeResponse
from .security import create_token


settings = get_settings()
app = FastAPI(title=settings.app_name)


# CORS for frontend dev
origins = get_cors_origins()
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def on_startup():
    # Create tables if not using Alembic yet.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok"}


@app.get("/auth/discord-url", response_model=LoginUrlResponse)
async def discord_login_url():
    if not settings.discord_client_id or not settings.discord_client_secret or not settings.oauth_redirect_uri:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OAuth not configured")
    state = services.auth.generate_state()
    url = services.auth.build_discord_oauth_url(state)
    return {"url": url, "state": state}


@app.get("/auth/callback")
async def discord_callback(request: Request, response: Response, code: str, state: str):
    # NOTE: State validation/storage is omitted here for brevity; in production store/verify it.
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code")
    access_token = await services.auth.exchange_code_for_token(code)
    discord_id, username, avatar = await services.auth.fetch_discord_user(access_token)

    async with db_session() as session:
        user = await services.economy.ensure_user(session, discord_id, username=username)
        token = create_token(discord_id, user.username)
    response.set_cookie(
        "doodle_session",
        token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.jwt_exp_minutes * 60,
    )
    return {"ok": True, "discord_id": discord_id}


@app.get("/me", response_model=MeResponse)
async def me(user=Depends(get_current_user), session=Depends(get_db)):
    account = await services.economy.get_balance(session, int(user.sub))
    return {
        "discord_id": account.discord_id,
        "username": account.username,
        "balance": account.balance,
        "streak": account.streak,
        "last_daily_claim": account.last_daily_claim,
    }


@app.post("/economy/daily", response_model=ClaimResponse)
async def daily(user=Depends(get_current_user), session=Depends(get_db)):
    allowed, account, wait = await services.economy.claim_daily(session, int(user.sub), username=user.username)
    return {
        "allowed": allowed,
        "balance": account.balance,
        "streak": account.streak,
        "next_claim_in": int(wait.total_seconds()) if wait else None,
    }


@app.get("/economy/balance", response_model=MeResponse)
async def balance(user=Depends(get_current_user), session=Depends(get_db)):
    account = await services.economy.get_balance(session, int(user.sub))
    return {
        "discord_id": account.discord_id,
        "username": account.username,
        "balance": account.balance,
        "streak": account.streak,
        "last_daily_claim": account.last_daily_claim,
    }


# Ensure the event loop is available for async generator usage in docs and background tasks
asyncio.get_event_loop()


# Serve the frontend (static) from the repo-level /frontend directory
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
