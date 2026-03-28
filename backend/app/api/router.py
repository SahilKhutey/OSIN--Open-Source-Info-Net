from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import Signal, Trend
from typing import List

router = APIRouter()

@router.get("/signals", response_model=None)
async def list_signals(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Retrieve real-time signals extracted from global sources.
    """
    result = await db.execute(select(Signal).order_by(Signal.created_at.desc()).limit(limit).offset(offset))
    signals = result.scalars().all()
    return signals

@router.get("/trends", response_model=None)
async def list_trends(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Get current trending signals across the OSIN network.
    """
    result = await db.execute(select(Trend).order_by(Trend.score.desc()).limit(limit))
    trends = result.scalars().all()
    return trends

@router.get("/signal/{signal_id}", response_model=None)
async def get_signal(signal_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Signal).where(Signal.id == signal_id))
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal
