# app/models/company.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    ticker = Column(String(5), unique=True, nullable=False)
    sector = Column(String(20), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cash = Column(Float, default=50000.0)
    reputation = Column(Float, default=50.0)
    total_shares = Column(Integer, default=1000)
    share_price = Column(Float, default=10.0)
    is_public = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="companies")
    comments = relationship("Comment", back_populates="company")
    products = relationship("Product", back_populates="company")
    stock_owners = relationship("StockOwnership", back_populates="company")