# app/models/stock.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone

class StockOwnership(Base):
    __tablename__ = "stock_ownerships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    shares_owned = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)

    user = relationship("User", back_populates="stock_portfolio")
    company = relationship("Company", back_populates="stock_owners")


class StockOrder(Base):
    __tablename__ = "stock_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    order_type = Column(String(4), nullable=False)
    shares = Column(Integer, nullable=False)
    price_per_share = Column(Float, nullable=False)
    status = Column(String(10), default="OPEN")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shares = Column(Integer, nullable=False)
    price_per_share = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WorldEvent(Base):
    __tablename__ = "world_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    sector_affected = Column(String(20), nullable=True)
    price_impact = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))