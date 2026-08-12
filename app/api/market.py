# app/api/market.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.product import Product, Resource
from app.schemas.product import ProductResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/market", tags=["Market"])

# ---------- Buy Resources ----------
@router.post("/buy-resource")
async def buy_resource(
    company_id: int,
    resource_name: str,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get company
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.owner_id == current_user.id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found or not yours")
    
    # Get resource
    result = await db.execute(select(Resource).where(Resource.name == resource_name))
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.quantity_available < quantity:
        raise HTTPException(status_code=400, detail="Not enough resources available")
    
    total_cost = resource.current_price * quantity
    
    if company.cash < total_cost:
        raise HTTPException(status_code=400, detail=f"Need ${total_cost:.2f}, have ${company.cash:.2f}")
    
    # Deduct cash, reduce resource quantity
    company.cash -= total_cost
    resource.quantity_available -= quantity
    
    # Increase resource price due to demand
    resource.current_price *= (1 + (quantity / resource.quantity_available) * 0.1) if resource.quantity_available > 0 else 1.1
    
    await db.commit()
    
    return {
        "message": f"Bought {quantity} {resource_name} for ${total_cost:.2f}",
        "new_price": resource.current_price,
        "company_cash": company.cash
    }


# ---------- Sell Products ----------
@router.post("/sell-product")
async def sell_product(
    product_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get company
    result = await db.execute(select(Company).where(Company.id == product.company_id))
    company = result.scalar_one_or_none()
    
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your company")
    
    if product.quantity < quantity:
        raise HTTPException(status_code=400, detail="Not enough products in inventory")
    
    # Calculate revenue
    total_revenue = product.selling_price * quantity
    
    # Update inventory and cash
    product.quantity -= quantity
    company.cash += total_revenue
    
    # Increase reputation
    company.reputation = min(100, company.reputation + (quantity * 0.1))
    
    await db.commit()
    
    return {
        "message": f"Sold {quantity} {product.name} for ${total_revenue:.2f}",
        "revenue": total_revenue,
        "company_cash": company.cash,
        "remaining_quantity": product.quantity,
        "reputation": company.reputation
    }


# ---------- View Market Prices ----------
@router.get("/resources")
async def get_resources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resource))
    resources = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "price": r.current_price,
            "available": r.quantity_available,
            "sector": r.sector
        }
        for r in resources
    ]


# ---------- Seed Initial Resources ----------
@router.post("/seed-resources")
async def seed_resources(db: AsyncSession = Depends(get_db)):
    default_resources = [
        {"name": "Silicon", "price": 50, "sector": "tech"},
        {"name": "Wheat", "price": 20, "sector": "food"},
        {"name": "Oil", "price": 80, "sector": "energy"},
        {"name": "Steel", "price": 40, "sector": "tech"},
        {"name": "Corn", "price": 15, "sector": "food"},
        {"name": "Solar Panels", "price": 100, "sector": "energy"},
    ]
    
    for r in default_resources:
        existing = await db.execute(select(Resource).where(Resource.name == r["name"]))
        if not existing.scalar_one_or_none():
            resource = Resource(
                name=r["name"],
                base_price=r["price"],
                current_price=r["price"],
                sector=r["sector"],
                quantity_available=1000
            )
            db.add(resource)
    
    await db.commit()
    return {"message": "Resources seeded!"}