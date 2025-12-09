from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, AnyHttpUrl


class HealthResponse(BaseModel):
    status: str


class LoginUrlResponse(BaseModel):
    url: AnyHttpUrl
    state: str


class MeResponse(BaseModel):
    discord_id: int
    username: Optional[str]
    balance: int
    streak: int
    last_daily_claim: Optional[datetime]


class ClaimResponse(BaseModel):
    allowed: bool
    balance: int
    streak: int
    next_claim_in: Optional[int]  # seconds

