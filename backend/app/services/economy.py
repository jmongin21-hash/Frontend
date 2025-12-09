from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserAccount, BalanceLedger

DAILY_REWARD = 100
DAILY_COOLDOWN = timedelta(hours=24)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_user(session: AsyncSession, discord_id: int, username: Optional[str] = None) -> UserAccount:
    result = await session.execute(select(UserAccount).where(UserAccount.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if user:
        if username and user.username != username:
            user.username = username
        return user
    user = UserAccount(discord_id=discord_id, username=username, balance=0, streak=0)
    session.add(user)
    await session.flush()
    return user


async def get_balance(session: AsyncSession, discord_id: int) -> UserAccount:
    return await ensure_user(session, discord_id)


async def claim_daily(session: AsyncSession, discord_id: int, username: Optional[str]) -> tuple[bool, UserAccount, Optional[timedelta]]:
    user = await ensure_user(session, discord_id, username)
    now = _utcnow()
    if user.last_daily_claim:
        elapsed = now - user.last_daily_claim
        if elapsed < DAILY_COOLDOWN:
            return False, user, DAILY_COOLDOWN - elapsed
        if (now.date() - user.last_daily_claim.date()).days == 1:
            user.streak = (user.streak or 0) + 1
        else:
            user.streak = 1
    else:
        user.streak = 1

    user.balance += DAILY_REWARD
    user.last_daily_claim = now
    session.add(
        BalanceLedger(
            discord_id=discord_id,
            delta=DAILY_REWARD,
            reason="daily",
            context=None,
        )
    )
    await session.flush()
    return True, user, None
