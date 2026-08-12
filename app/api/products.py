# app/api/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProduceRequest
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/create", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.owner_id == current_user.id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found or not yours")
    
    new_product = Product(
        company_id=company_id,
        name=product_data.name,
        production_cost=product_data.production_cost,
        selling_price=product_data.selling_price
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    return new_product

@router.post("/produce", response_model=ProductResponse)
async def produce_goods(
    request: ProduceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == request.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = await db.execute(select(Company).where(Company.id == product.company_id))
    company = result.scalar_one_or_none()
    
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your company")
    
    total_cost = product.production_cost * request.quantity
    
    if company.cash < total_cost:
        raise HTTPException(status_code=400, detail="Company doesn't have enough cash")
    
    company.cash -= total_cost
    product.quantity += request.quantity
    
    await db.commit()
    await db.refresh(product)
    
    return product

@router.get("/company/{company_id}", response_model=list[ProductResponse])
async def get_company_products(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).where(Product.company_id == company_id)
    )
    return result.scalars().all()