# app/schemas/company.py
from pydantic import BaseModel
from typing import Optional

class CompanyCreate(BaseModel):
    name: str
    ticker: str
    sector: str

class CompanyResponse(BaseModel):
    id: int
    name: str
    ticker: str
    sector: str
    owner_id: int
    cash: float
    reputation: float
    total_shares: int
    share_price: float
    is_public: int

    class Config:
        from_attributes = True