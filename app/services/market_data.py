# app/services/market_data.py
import asyncio
import random
from sqlalchemy import select
from app.models.company import Company
from app.api.websocket import manager

async def get_live_prices(db):
    result = await db.execute(
        select(Company).where(Company.is_public == 1)
    )
    companies = result.scalars().all()
    return [{"id": c.id, "name": c.name, "ticker": c.ticker, "price": round(c.share_price, 2), "sector": c.sector} for c in companies]

async def simulate_prices(db):
    result = await db.execute(select(Company).where(Company.is_public == 1))
    companies = result.scalars().all()
    for c in companies:
        change = random.uniform(-1.5, 1.5)
        c.share_price = max(1, round(c.share_price * (1 + change/100), 2))
    await db.commit()
    return await get_live_prices(db)

async def price_loop(db_factory):
    while True:
        try:
            async with db_factory() as db:
                prices = await simulate_prices(db)
                await manager.broadcast({"type": "prices", "data": prices})
        except Exception as e:
            print(f"Price error: {e}")
        await asyncio.sleep(3)