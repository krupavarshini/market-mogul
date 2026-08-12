# app/api/leaderboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.stock import StockOwnership

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    leaderboard = []
    
    for user in users:
        # Calculate net worth
        net_worth = user.cash_balance
        
        # Add value of companies owned
        comp_result = await db.execute(
            select(func.sum(Company.cash)).where(Company.owner_id == user.id)
        )
        company_cash = comp_result.scalar() or 0
        net_worth += company_cash
        
        # Add value of stock portfolio
        stock_result = await db.execute(
            select(StockOwnership, Company.share_price)
            .join(Company, StockOwnership.company_id == Company.id)
            .where(StockOwnership.user_id == user.id)
        )
        
        for ownership, share_price in stock_result:
            net_worth += ownership.shares_owned * share_price
        
        leaderboard.append({
            "username": user.username,
            "net_worth": round(net_worth, 2),
            "companies_owned": await count_user_companies(db, user.id)
        })
    
    # Sort by net worth
    leaderboard.sort(key=lambda x: x["net_worth"], reverse=True)
    
    # Add rank
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    return leaderboard[:20]  # Top 20


async def count_user_companies(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count(Company.id)).where(Company.owner_id == user_id)
    )
    return result.scalar() or 0