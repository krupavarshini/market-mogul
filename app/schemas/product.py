# app/schemas/product.py
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    production_cost: float = 5.0
    selling_price: float = 10.0

class ProductResponse(BaseModel):
    id: int
    company_id: int
    name: str
    quantity: int
    production_cost: float
    selling_price: float

    class Config:
        from_attributes = True

class ProduceRequest(BaseModel):
    product_id: int
    quantity: int