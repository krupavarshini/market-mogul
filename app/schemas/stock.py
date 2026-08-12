# app/schemas/stock.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IPORequest(BaseModel):
    company_id: int
    shares_to_issue: int
    initial_price: float

class OrderRequest(BaseModel):
    company_id: int
    order_type: str
    shares: int
    price_per_share: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    order_type: str
    shares: int
    price_per_share: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class StockOwnershipResponse(BaseModel):
    company_id: int
    company_name: str = ""
    ticker: str = ""
    shares_owned: int
    average_price: float
    current_price: float = 0.0
    profit_loss: float = 0.0

    class Config:
        from_attributes = True

class TradeResponse(BaseModel):
    id: int
    company_id: int
    shares: int
    price_per_share: float
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True

class WorldEventResponse(BaseModel):
    id: int
    title: str
    description: str
    sector_affected: Optional[str]
    price_impact: float
    created_at: datetime

    class Config:
        from_attributes = True# app/schemas/stock.py 
