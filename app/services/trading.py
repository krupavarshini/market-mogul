# app/services/trading.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.company import Company
from app.models.user import User
from app.models.stock import StockOwnership, StockOrder, Trade

async def match_orders(db: AsyncSession, company_id: int):
    buy_result = await db.execute(
        select(StockOrder)
        .where(and_(StockOrder.company_id == company_id,
                    StockOrder.order_type == "BUY",
                    StockOrder.status == "OPEN"))
        .order_by(StockOrder.price_per_share.desc())
    )
    buy_orders = list(buy_result.scalars().all())

    sell_result = await db.execute(
        select(StockOrder)
        .where(and_(StockOrder.company_id == company_id,
                    StockOrder.order_type == "SELL",
                    StockOrder.status == "OPEN"))
        .order_by(StockOrder.price_per_share.asc())
    )
    sell_orders = list(sell_result.scalars().all())

    trades_made = []

    for buy_order in buy_orders:
        for sell_order in sell_orders:
            if buy_order.status != "OPEN" or sell_order.status != "OPEN":
                continue
            if buy_order.price_per_share >= sell_order.price_per_share:
                trade_price = sell_order.price_per_share
                trade_shares = min(buy_order.shares, sell_order.shares)
                total_amount = trade_price * trade_shares

                buyer = await db.get(User, buy_order.user_id)
                if buyer.cash_balance < total_amount:
                    continue
                buyer.cash_balance -= total_amount

                seller = await db.get(User, sell_order.user_id)
                seller.cash_balance += total_amount

                trade = Trade(
                    company_id=company_id,
                    buyer_id=buy_order.user_id,
                    seller_id=sell_order.user_id,
                    shares=trade_shares,
                    price_per_share=trade_price,
                    total_amount=total_amount
                )
                db.add(trade)

                buy_own = await get_or_create_ownership(db, buy_order.user_id, company_id)
                buy_own.shares_owned += trade_shares

                sell_own = await get_or_create_ownership(db, sell_order.user_id, company_id)
                sell_own.shares_owned -= trade_shares

                company = await db.get(Company, company_id)
                company.share_price = trade_price

                buy_order.shares -= trade_shares
                sell_order.shares -= trade_shares

                if buy_order.shares == 0:
                    buy_order.status = "FILLED"
                if sell_order.shares == 0:
                    sell_order.status = "FILLED"

                trades_made.append(trade)

    await db.commit()
    return trades_made


async def get_or_create_ownership(db: AsyncSession, user_id: int, company_id: int):
    result = await db.execute(
        select(StockOwnership).where(
            and_(StockOwnership.user_id == user_id, StockOwnership.company_id == company_id)
        )
    )
    ownership = result.scalar_one_or_none()
    if not ownership:
        ownership = StockOwnership(user_id=user_id, company_id=company_id)
        db.add(ownership)
        await db.flush()
    return ownership