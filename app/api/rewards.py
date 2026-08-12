# app/api/rewards.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/rewards", tags=["Rewards"])

@router.post("/daily-login")
async def daily_login(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.cash_balance += 500
    await db.commit()
    return {"message": "Daily bonus claimed! +$500", "reward": 500, "streak": 1}

@router.get("/stats")
async def stats(current_user: User = Depends(get_current_user)):
    return {"level": 1, "xp": 0, "cash": current_user.cash_balance}