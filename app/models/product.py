# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=0)
    production_cost = Column(Float, default=5.0)
    selling_price = Column(Float, default=10.0)
    
    company = relationship("Company", back_populates="products")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    sector = Column(String(20), nullable=False)
    quantity_available = Column(Integer, default=1000)