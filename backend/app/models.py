from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text

from .db import Base


class UserAccount(Base):
    __tablename__ = "users"

    discord_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    avatar = Column(String(255), nullable=True)
    balance = Column(Integer, nullable=False, default=0)
    streak = Column(Integer, nullable=False, default=0)
    last_daily_claim = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class BalanceLedger(Base):
    __tablename__ = "balance_ledger"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, index=True, nullable=False)
    delta = Column(Integer, nullable=False)
    reason = Column(String(50), nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
