# Doodlebucks Backend (FastAPI)

Minimal API skeleton for the currency + game service. It provides:
- Discord OAuth2 login endpoints (identify scope)
- JWT session cookie issuance
- Economy endpoints: health, me, balance, daily claim
- Postgres models for users and a balance ledger

## Quickstart (dev)
1. Create `.env` in this folder (or repo root) with:
   ```
   DOODLE_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/doodlebucks
   DOODLE_JWT_SECRET=your-long-random-secret
   DOODLE_JWT_ISSUER=doodlebucks-api
   DOODLE_JWT_AUDIENCE=doodlebucks-web
   DOODLE_DISCORD_CLIENT_ID=your_discord_app_id
   DOODLE_DISCORD_CLIENT_SECRET=your_discord_app_secret
   DOODLE_OAUTH_REDIRECT_URI=https://yourdomain.com/auth/callback
   DOODLE_FRONTEND_ORIGIN=https://yourdomain.com
   ```
   For local dev with a tool like `ngrok`, set the redirect/front-end origins to that URL.

2. Install deps (from repo root): `pip install -r backend/requirements.txt`

3. Run: `uvicorn app.main:app --reload --app-dir backend`

## Endpoints
- `GET /health` — simple status.
- `GET /auth/discord-url` — returns OAuth URL + state (store/verify state in your frontend/service).
- `GET /auth/callback?code=...&state=...` — exchanges code for Discord user, issues JWT cookie `doodle_session`.
- `GET /me` — returns user/balance/streak (requires auth).
- `GET /economy/balance` — same as /me for now (requires auth).
- `POST /economy/daily` — claim daily reward with cooldown + streak (requires auth).

## Notes
- Tables are auto-created on startup for now; switch to Alembic migrations before production.
- State validation for OAuth is noted but not persisted here; store/validate in your frontend/backend flow.
- The bot should be updated later to use the same Postgres DB instead of SQLite for shared balances.
