# app/models/user.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    cash_balance = Column(Float, default=100000.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    companies = relationship("Company", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    stock_portfolio = relationship("StockOwnership", back_populates="user")