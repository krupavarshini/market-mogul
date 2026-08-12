# app/api/stocks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.stock import StockOwnership, StockOrder, Trade, WorldEvent
from app.schemas.stock import (
    IPORequest, OrderRequest, OrderResponse,
    StockOwnershipResponse, TradeResponse, WorldEventResponse
)
from app.api.dependencies import get_current_user
from app.services.trading import match_orders, get_or_create_ownership
import random

router = APIRouter(prefix="/stocks", tags=["Stock Market"])


@router.post("/ipo")
async def make_company_public(
    request: IPORequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    company = await db.get(Company, request.company_id)
    if not company or company.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Company not found or not yours")
    if company.is_public:
        raise HTTPException(status_code=400, detail="Company already public")
    
    company.is_public = 1
    company.total_shares = request.shares_to_issue
    company.share_price = request.initial_price
    
    ownership = await get_or_create_ownership(db, current_user.id, company.id)
    ownership.shares_owned = request.shares_to_issue
    ownership.average_price = request.initial_price
    
    await db.commit()
    return {"message": f"{company.name} is now public!", "ticker": company.ticker}


@router.post("/order", response_model=OrderResponse)
async def place_order(
    request: OrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    company = await db.get(Company, request.company_id)
    if not company or not company.is_public:
        raise HTTPException(status_code=400, detail="Company not public")
    
    if request.order_type == "SELL":
        ownership = await get_or_create_ownership(db, current_user.id, company.id)
        if not ownership or ownership.shares_owned < request.shares:
            raise HTTPException(status_code=400, detail="Not enough shares")
    
    if request.order_type == "BUY":
        total = request.shares * request.price_per_share
        if current_user.cash_balance < total:
            raise HTTPException(status_code=400, detail="Not enough cash")
    
    order = StockOrder(
        user_id=current_user.id,
        company_id=request.company_id,
        order_type=request.order_type,
        shares=request.shares,
        price_per_share=request.price_per_share
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    await match_orders(db, company.id)
    
    return order


@router.get("/portfolio", response_model=list[StockOwnershipResponse])
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(StockOwnership, Company.name, Company.ticker, Company.share_price)
        .join(Company, StockOwnership.company_id == Company.id)
        .where(StockOwnership.user_id == current_user.id)
        .where(StockOwnership.shares_owned > 0)
    )
    
    portfolio = []
    for ownership, name, ticker, price in result:
        profit = (price - ownership.average_price) * ownership.shares_owned
        portfolio.append(StockOwnershipResponse(
            company_id=ownership.company_id,
            company_name=name,
            ticker=ticker,
            shares_owned=ownership.shares_owned,
            average_price=ownership.average_price,
            current_price=price,
            profit_loss=profit
        ))
    
    return portfolio


@router.get("/trades/{company_id}", response_model=list[TradeResponse])
async def get_trades(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trade).where(Trade.company_id == company_id)
        .order_by(desc(Trade.created_at)).limit(20)
    )
    return result.scalars().all()


@router.get("/events", response_model=list[WorldEventResponse])
async def get_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorldEvent).order_by(desc(WorldEvent.created_at)).limit(10)
    )
    return result.scalars().all()


EVENTS = [
    {"title": "AI Breakthrough!", "desc": "Tech stocks surge on new AI innovation", "sector": "tech", "impact": 15},
    {"title": "Food Shortage", "desc": "Supply chain crisis hits food sector", "sector": "food", "impact": -10},
    {"title": "Oil Discovery", "desc": "Massive oil field found, energy prices drop", "sector": "energy", "impact": -8},
    {"title": "Market Crash", "desc": "Global panic selling across all sectors", "sector": None, "impact": -20},
    {"title": "Bull Market", "desc": "Investor optimism drives markets up", "sector": None, "impact": 10},
    {"title": "New Gadget Launch", "desc": "Revolutionary device announced", "sector": "tech", "impact": 12},
    {"title": "Trade Deal", "desc": "New trade agreement boosts markets", "sector": None, "impact": 8},
]


@router.post("/events/generate")
async def generate_event(db: AsyncSession = Depends(get_db)):
    event_data = random.choice(EVENTS)
    
    event = WorldEvent(
        title=event_data["title"],
        description=event_data["desc"],
        sector_affected=event_data["sector"],
        price_impact=event_data["impact"]
    )
    db.add(event)
    
    query = select(Company).where(Company.is_public == 1)
    if event_data["sector"]:
        query = query.where(Company.sector == event_data["sector"])
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    for company in companies:
        change = company.share_price * (event_data["impact"] / 100)
        company.share_price = max(1, round(company.share_price + change, 2))
    
    await db.commit()
    await db.refresh(event)
    
    return {"event": event.title, "companies_affected": len(companies)}